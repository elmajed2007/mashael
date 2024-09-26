from odoo import api, fields, models , _
from odoo.http import request
from odoo.exceptions import UserError



class MshDeal(models.Model):
    _name = 'msh.deal'
    _description = 'Deal'


    name = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('confirm', 'Supplier Confirm'),
        ('reject', 'Reject'),
        ('validate', 'Validate'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    version = fields.Char(
        string='Version',
        required=False)
    deal_requester_id = fields.Many2one(
        comodel_name='crm.team',
        string='Deal Requester',
        required=False)
    req_date = fields.Date(
        string='Req Date', 
        required=False)
    offer_deadline = fields.Datetime(
        string='Offer Deadline',
        required=False)
    partner_id = fields.Many2one('res.partner', string='Supplier')
    destination_id = fields.Many2one(comodel_name='destination', string='Destination', domain="[('partner_id', '=', partner_id)]")
    discount_needed = fields.Float(
        string='Discount Needed',
        required=False) #persent
    req_project_duration = fields.Char(
        string='Req Project Duration',
        required=False)
    project_name = fields.Char(
        string='Project Name',
        required=False)
    owner_name = fields.Char(
        string='Owner Name',
        required=False)
    client_name = fields.Char(
        string='Client Name',
        required=False)
    
    #send notification for po users group
    def deal_page(self):
        menu_id = self.env.ref('mshael_deal.mashael_deal_menu')
        action_id = self.env.ref('mshael_deal.mshael_deal_action')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        base_url += '&menu_id=%d&action=%d' % (menu_id.id, action_id.id)
        return base_url

    def send_notification(self, po_users, deal_name, deal_page):
        self.message_post(record_name='Deal', body=""" Deal Was Created: """ + deal_name + '<br>' + """
        <br> You Can Check: <br>""" + """<a href="%s">Link</a> """ % (deal_page)
                          , message_type="notification",
                          subtype_xmlid="mail.mt_comment",
                          author_id=self.env.user.partner_id.id,
                          partner_ids=po_users)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('msh.deal') or _('New')
        result = super(MshDeal, self).create(vals)
        po_users = []
        users = self.env['res.users'].search([])
        for user in users:
            if user not in po_users:
                if user.has_groups('mshael_deal.purchase_users_confirm_deal'):
                    po_users.append(user)
        result.send_notification(po_users, self.name, self.deal_page())
        return result

    def processing_deal(self):
        self.write({'state': 'processing'})

    def confirm_deal(self):
        self.write({'state': 'confirm'})

    def validate_deal(self):
        self.write({'state': 'validate'})

    def reject_deal(self):
        self.write({'state': 'reject'})

    def reset_to_draft(self):
        self.write({'state': 'draft'})


    general_line_ids = fields.One2many(
        comodel_name='deal.general.specification',
        inverse_name='general_line_id',
        string='General_line_ids',
        required=False)

    @api.onchange('general_line_ids')
    def onchange_general_line_ids(self):
        pr_lines = []
        self.purchase_line_ids = [(5, 0)]
        for line in self.general_line_ids:
            price = 0
            if line.product_id:
                pricelist = self.env['product.supplierinfo'].search([('destination_id', '=', self.destination_id.id), ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id), ('partner_id', '=', self.partner_id.id)]).filtered(lambda d: d.date_start != False).sorted(key=lambda x: x.date_start)
                print('pricelist >>', pricelist)
                for line in pricelist.supplier_line_ids:
                    if line.product_id == line.product_id:
                         price = line.unit_purchase_price

                pr_lines.append(
                    {
                        "product_id": line.product_id.id,
                        "pl_price": price,
                        "requested_price": (price * line.discount_requested),


                    }
                )
        for line in pr_lines:
            self.purchase_line_ids = [(0, 0, line)]




    ms_screen_line_ids = fields.One2many(
        comodel_name='ms.screen.line',
        inverse_name='ms_screen_line_id',
        string='ms_screen_line_ids',
        required=False)

    purchase_line_ids = fields.One2many(
        comodel_name='deal.purchase.line',
        inverse_name='purchase_line_id',
        string='Purchase_line_ids',
        required=False)



class GeneralSpecification(models.Model):
    _name = 'deal.general.specification'
    _description = 'General Specification'

    name = fields.Char()
    general_line_id = fields.Many2one(comodel_name='msh.deal', string='General_line_id', required=False)
    product_id = fields.Many2one('product.product', string='Code')
    # item_description = fields.Char(string='Item Description', required=False, related='product_id.description')
    item_description = fields.Html(string="Item Description", related='product_id.description')
    item_wise_additional_specification = fields.Char(string='Item Wise Additional Specification', required=False)
    qty = fields.Float(string='Qty', required=False)
    uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit', required=False, related='product_id.uom_po_id')
    discount_requested = fields.Float(string='Discount Requested', required=False)# percent
    total_given_discount = fields.Float(string='Total Given Discount', required=False, compute='_compute_total_given_discount')

    @api.depends('product_id', 'general_line_id.price_total')
    def _compute_total_given_discount(self):
        for rec in self:
            total = 0
            value_rec = self.env['deal.purchase.line'].search([('purchase_line_id', '=', rec.general_line_id.id), ('product_id', '=', rec.product_id.id)])
            for rec in value_rec:
                total = rec.confirmed_supplier_discount + rec.management_discount
            rec.total_given_discount = total
    hs_code = fields.Many2one('hs.code', string="HS Code")
    origin = fields.Char(string='Origin', required=False)
    saber_regulation = fields.Float(string='Saber Regulation', required=False)
    certificate = fields.Float(string='Certificate', required=False)

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.hs_code = self.product_id.hs_code
        self.origin = self.product_id.origin

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('deal.general.specification') or _('New')
        result = super(GeneralSpecification, self).create(vals)
        return result



class MSScreen(models.Model):
    _name = 'ms.screen.line'
    _description = 'M&S Screen'

    ms_screen_line_id = fields.Many2one(comodel_name='msh.deal', string='ms_screen_line_id', required=False)
    confirmed_qty_variance = fields.Float(string='Confirmed Qty Variance -/+ %', required=False)# percent
    deal_red = fields.Float(string='Deal Red', required=False)
    deal_green = fields.Float(string='Deal Green', required=False)
    sales_delivery_condition = fields.Float(string='Sales Delivery Condition', required=False)



class Purchasecreen(models.Model):
    _name = 'deal.purchase.line'
    _description = 'Management Screen'

    purchase_line_id = fields.Many2one(comodel_name='msh.deal', string='purchase_line_id', required=False)
    product_id = fields.Many2one('product.product', string='Code')
    hs_code = fields.Many2one('hs.code', string="HS Code")

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.hs_code = self.product_id.product_tmpl_id.hs_code.id
        self.customs_unit = self.product_id.product_tmpl_id.duty_rate

    pl_price = fields.Float(
        string='Pl_price',
        required=False)
    requested_price = fields.Float(
        string='Requested Price',
        required=False)
    main_discount = fields.Float(
        string='Main_discount',
        required=False)
    confirmed_price = fields.Float(
        string='Confirmed Price',
        required=False)
    confirmed_qty = fields.Float(
        string='Confirmed Qty Variance -/+ %',
        required=False)

    confirmed_supplier_discount = fields.Float(
        string='Confirmed Supplier Discount',
        required=False)

    purchase_price = fields.Float(
        string='Purchase Price',
        required=False)
    customs_unit = fields.Float(
        string='Customs Unit',
        required=False)

    @api.onchange('confirmed_qty', 'pl_price')
    def onchange_method(self):
        self.confirmed_price = self.confirmed_qty - self.pl_price
        self.purchase_price = self.confirmed_qty - self.pl_price
        #
    price_policy_id = fields.Many2one(comodel_name='price.policy', string='Price Policy', required=False, related='product_id.product_tmpl_id.price_policy_id')
    insurance = fields.Float(string='Insurance', required=False, compute='_compute_insurance')

    @api.depends('purchase_price', 'price_policy_id', 'price_policy_id.insurance')
    def _compute_insurance(self):
        for rec in self:
            value = 0
            value = rec.purchase_price * rec.price_policy_id.insurance
            rec.insurance = value

    overhead = fields.Float(string='Over head', required=False, compute='_compute_overhead')

    @api.depends('purchase_price', 'price_policy_id', 'price_policy_id.over_head_factor')
    def _compute_overhead(self):
        for rec in self:
            value = 0
            value = rec.purchase_price * rec.price_policy_id.over_head_factor
            rec.overhead = value

    delivery = fields.Float(string='Delivery', required=False, compute='_compute_delivery')

    @api.depends('purchase_price', 'price_policy_id', 'price_policy_id.delivery')
    def _compute_delivery(self):
        for rec in self:
            value = 0
            value = rec.purchase_price * rec.price_policy_id.delivery
            rec.delivery = value

    direct_cost = fields.Float(string='Direct Cost', required=False, compute='_compute_direct_cost')

    @api.depends('purchase_price', 'price_policy_id', 'hs_code', 'price_policy_id.delivery', 'price_policy_id.insurance')
    def _compute_direct_cost(self):
        for rec in self:
            value = 0
            value = rec.rec.purchase_price + rec.hs_code.duty_rate + (rec.purchase_price * rec.price_policy_id.insurance) + (rec.purchase_price * rec.price_policy_id.delivery)
            rec.direct_cost = value

    
    total_cost = fields.Float(string='Total Cost', required=False, compute='_compute_total_cost')

    @api.depends('purchase_price', 'price_policy_id', 'hs_code', 'price_policy_id.delivery', 'price_policy_id.insurance', 'price_policy_id.over_head_factor')
    def _compute_total_cost(self):
        for rec in self:
            value = 0
            value = (rec.rec.purchase_price + rec.hs_code.duty_rate + (rec.purchase_price * rec.price_policy_id.insurance) + (rec.purchase_price * rec.price_policy_id.delivery)) + (rec.purchase_price * rec.price_policy_id.over_head_factor)
            rec.total_cost = value

    red_price = fields.Float(string='Red Price', required=False)
    green_price = fields.Float(string='Green Price', required=False)
    # sales_delivery_condit = fields.Char(
    #     string='# Sales Delivery Conditions',
    #     required=False)
    management_discount = fields.Float(
        string='Management Discount',
        required=False)
    deal_red = fields.Float(
        string='Deal Red', 
        required=False)
    deal_green = fields.Float(
        string='Deal Green',
        required=False)