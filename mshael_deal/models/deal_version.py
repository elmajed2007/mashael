from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import UserError


class MshDealVersion(models.Model):
    _name = 'msh.deal.version'
    _description = 'Deal'

    name = fields.Char()
    main_deal_id = fields.Many2one(
        comodel_name='msh.deal',
        string='Main_deal_id',
        required=False)
    state = fields.Selection([
        ('draft', 'Requested'),
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
    destination_id = fields.Many2one(comodel_name='destination', string='Destination',
                                     domain="[('partner_id', '=', partner_id)]")
    discount_needed = fields.Float(
        string='Discount Needed',
        required=False)  # persent
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
    req_no_of_orders = fields.Float(
        string='Req. No. of Orders (Text Entry)',
        required=False)
    req_qty_variance = fields.Float(
        string='Req. Qty Variance % -/+',
        required=False)

    # py purchasing
    processed_date = fields.Date(
        string='Processed Date',
        required=False)
    supplier_confirmation = fields.Boolean(
        string='Supplier Confirmation',
        required=False)
    supplier_ref = fields.Char(
        string='Supplier Ref',
        required=False)
    offer_date = fields.Date(
        string='Offer Date',
        required=False)
    offer_expiry_date = fields.Date(
        string='Offer/Deal Expiry Date',
        required=False)
    conf_no_of_orders = fields.Char(
        string='Conf. No. of Orders (Text Entry)',
        required=False)
    conf_qty_variance = fields.Float(
        string='Conf. Qty Variance % -/+',
        required=False)

    general_line_ids = fields.One2many(
        comodel_name='deal.general.version.specification',
        inverse_name='general_line_id',
        string='General_line_ids',
        required=False)


    ms_screen_line_ids = fields.One2many(
        comodel_name='ms.screen.version.line',
        inverse_name='ms_screen_line_id',
        string='ms_screen_line_ids',
        required=False)

    purchase_line_ids = fields.One2many(
        comodel_name='deal.purchase.version.line',
        inverse_name='purchase_line_id',
        string='Purchase_line_ids',
        required=False)


class GeneralSpecification(models.Model):
    _name = 'deal.general.version.specification'
    _description = 'General Specification'

    name = fields.Char()
    general_line_id = fields.Many2one(comodel_name='msh.deal.version', string='General_line_id', required=False)
    product_id = fields.Many2one('product.product', string='Code')
    # item_description = fields.Char(string='Item Description', required=False, related='product_id.description')
    item_description = fields.Html(string="Item Description", related='product_id.description')
    item_wise_additional_specification = fields.Char(string='Item Wise Additional Specification', required=False)
    qty = fields.Float(string='Qty', required=False)
    uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit', required=False, related='product_id.uom_po_id')
    discount_requested = fields.Float(string='Discount Requested', required=False)  # percent
    total_given_discount = fields.Float(string='Total Given Discount', required=False,
                                        )
    hs_code = fields.Many2one('hs.code', string="HS Code")
    origin = fields.Char(string='Origin', required=False)
    saber_regulation = fields.Float(string='Saber Regulation', required=False)
    certificate = fields.Float(string='Certificate', required=False)

class MSScreen(models.Model):
    _name = 'ms.screen.version.line'
    _description = 'M&S Screen'

    ms_screen_line_id = fields.Many2one(comodel_name='msh.deal.version', string='ms_screen_line_id', required=False)
    confirmed_qty_variance = fields.Float(string='Confirmed Qty Variance -/+ %', required=False)  # percent
    deal_red = fields.Float(string='Deal Red', required=False)
    deal_green = fields.Float(string='Deal Green', required=False)
    sales_delivery_condition = fields.Float(string='Sales Delivery Condition', required=False)


class Purchasecreen(models.Model):
    _name = 'deal.purchase.version.line'
    _description = 'Management Screen'

    purchase_line_id = fields.Many2one(comodel_name='msh.deal.version', string='purchase_line_id', required=False)
    product_id = fields.Many2one('product.product', string='Code')
    hs_code = fields.Many2one('hs.code', string="HS Code")

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

    price_policy_id = fields.Many2one(comodel_name='price.policy', string='Price Policy', required=False)
    insurance = fields.Float(string='Insurance', required=False)
    overhead = fields.Float(string='Over head', required=False)
    delivery = fields.Float(string='Delivery', required=False)
    direct_cost = fields.Float(string='Direct Cost', required=False)
    total_cost = fields.Float(string='Total Cost', required=False)
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