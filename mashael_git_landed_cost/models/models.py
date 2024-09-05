from odoo import api, fields, models


from odoo import api, fields, models , _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    commercial_reg_no = fields.Char(
        string='Commercial Reg No',
        required=False)



class GitLandedCost(models.Model):
    _name = 'git.landed.cost'
    _description = 'Git Landed Cost'
    _rec_name = "name"


    name = fields.Char()
    git_id = fields.Many2one(
        comodel_name='msh.git',
        string='',
        required=False)
    
    dec_no = fields.Char(
        string='رقم البيان',
        required=False)
    dec_date = fields.Date(
        string='تاريخ البيان',
        required=False)
    saded_unified_number = fields.Integer(
        string='الرقم الموحد',
        required=False)
    company_id = fields.Many2one('res.company', 'Company', required=False
                                 , readonly=1, default=lambda self: self.env.company.id)
    commercial_reg_no = fields.Char(
        string='Commercial Reg No',
        required=False, related='company_id.commercial_reg_no')
    vat = fields.Char(related='company_id.vat', string='الرقم الضريبى')
    partner_id = fields.Many2one('res.partner', string='المخلص الجمركى', required=True)

    license_no = fields.Char(
        string='رقم الرخصة',
        required=False)

    loading_port_id = fields.Many2one(
        comodel_name='msh.port',
        string='Port Of Loading',
        required=False, related='git_id.loading_port_id')

    destination_port_id = fields.Many2one(
        comodel_name='msh.port',
        string='Find Destination Board',
        required=False, related='git_id.destination_port_id')

    destination_id = fields.Many2one(comodel_name='destination', related='git_id.destination_id', string='نوع المنفذ', domain="[('partner_id', '=', partner_id)]")
    destination_company_id = fields.Many2one('res.company', 'جهة المقصد', required=False
                                 , readonly=1, default=lambda self: self.env.company.id)
    bl_manifest = fields.Char(
        string='Bl/Manifest',
        required=False, related='git_id.bl_manifest')

    carrier_name = fields.Char(
        string='رقم الناقل',
        required=False, related='git_id.carrier_name')
    
    flight_no = fields.Char(
        string='رقم الرحلة',
        required=False)

    piv_line_ids = fields.One2many(
        comodel_name='git.landed.cost.line',
        inverse_name='piv_line_id',
        string='',
        required=False)

    piv_custom_ids = fields.One2many(
        comodel_name='piv.custom.line',
        inverse_name='piv_custom_id',
        string='Piv_custom_ids',
        required=False)
#totals
    total_custom = fields.Float(
        string='Total',
        required=False, compute='_compute_total_custom')

    total_custom_vat = fields.Float(
        string='Total',
        required=False, compute='_compute_total_custom')
    
    excis = fields.Float(
        string='Excis', 
        required=False)
    handing_fees = fields.Float(
        string='Handing_fees',
        required=False)
    landing_fees = fields.Float(
        string='Landing_fees', 
        required=False)
    other_fees = fields.Float(
        string='Other_fees', 
        required=False)
    definitive = fields.Float(
        string='Definitive',
        required=False)
    insurance = fields.Float(
        string='Insurance',
        required=False)
    total_feeses = fields.Float(
        string='Total_feeses',
        required=False, compute='_compute_total_feeses')


    @api.depends('total_custom','total_custom_vat', 'excis', 'handing_fees', 'landing_fees', 'other_fees', 'definitive', 'insurance')
    def _compute_total_feeses(self):
        for rec in self:
            total = 0
            total = (rec.total_custom + rec.total_custom_vat + rec.excis + rec.handing_fees+ rec.landing_fees + rec.other_fees + rec.definitive+ rec.insurance)
            rec.total_feeses = total

    @api.depends('piv_custom_ids')
    def _compute_total_custom(self):
        for rec in self:
            total = 0
            total_vats = 0
            for line in rec.piv_custom_ids:
                total += line.total
                total_vats += line.total_pr_taxes * line.local_value
            rec.total_custom = total
            rec.total_custom_vat = total_vats


    @api.onchange('git_id')
    def onchange_git_id(self):
        piv_lines = []
        self.piv_line_ids = [(5, 0)]
        for line in self.git_id.piv_line_ids:
                    piv_lines.append(
                        {
                            "piv_id": line.piv_id.id,
                        }
                    )
        for line in piv_lines:
            self.piv_line_ids = [(0, 0, line)]

    @api.constrains('piv_line_ids')
    def check_piv_line_ids(self):
        products = []
        hs_codes = []
        for line in self.piv_line_ids:
            for piv in line.piv_id.purchase_piv_line_ids:
                products.append(piv.product_id)
                hs_codes.append(piv.product_id.product_tmpl_id.hs_code)
        piv_products = set(products)
        piv_hs_codes = set(hs_codes)
        print('piv_products >>', piv_products)
        print('piv_hs_codes >>', piv_hs_codes)
        if piv_hs_codes != False:
            for hs_code in piv_hs_codes:
                print(';;')
                add_line = self.env['piv.custom.line'].create({
                    'piv_custom_id': self.id,
                    'hs_code': hs_code.id if hs_code else False,
                })
                print('add_line >', add_line)
                total_prices = 0
                total_qty = 0
                currency = 0
                total_tax = 0
                for line in self.piv_line_ids:
                    for piv in line.piv_id.purchase_piv_line_ids:
                        if piv.product_id.product_tmpl_id.hs_code == hs_code:
                            total_prices += piv.price_unit
                            total_qty += piv.qty_invoiced
                            currency = piv.currency_id.id
                            for tax in piv.product_id.supplier_taxes_id:
                                total_tax += tax.amount
                add_line.total_pr_taxes = total_tax
            add_line.currency_id = currency
            add_line.total_products_price_hidden = total_prices
            add_line.total_products_qty_hidden = total_qty



    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('git.landed.cost') or _('New')
        result = super(GitLandedCost, self).create(vals)
        return result



class GitLandedCostLine(models.Model):
    _name = 'git.landed.cost.line'

    piv_line_id = fields.Many2one(
        comodel_name='git.landed.cost',
        string='',
        required=False)

    piv_id = fields.Many2one(
        comodel_name='purchase.piv',
        string='Piv',
        required=False)

    partner_id = fields.Many2one('res.partner', string='المخلص الجمركى', required=True, related="piv_id.partner_id")

    supplier_inv_num = fields.Char(
        string='Supplier Inv Num',
        required=False, related="piv_id.supplier_invoice_number")
    
    other = fields.Char(
        string='Other', 
        required=False)



class PivCustomLine(models.Model):
    _name = 'piv.custom.line'
    _description = 'PivCustomLine'

    piv_custom_id = fields.Many2one(
        comodel_name='git.landed.cost',
        string='',
        required=False)
    hs_code = fields.Many2one('hs.code', string="HS Code")

    type_arabic_name= fields.Char('Product In Arabic')
    origin = fields.Char(string='Origin', required=False)
    foreign_value = fields.Float(
        string='القيمة بالعملة الأجنبية',
        required=False)
    currency_id = fields.Many2one('res.currency', 'Currency')
    price = fields.Float(
        string='سعر الصرف',
        required=False)
    local_price = fields.Float(
        string='سعر الصرف المحلى',
        required=False)
    total_products_price_hidden = fields.Float(
        string='',
        required=False)
    total_products_qty_hidden = fields.Float(
        string='',
        required=False)

    local_value = fields.Float(
        string='القيمة بالعملة المحلية',
        required=False)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency', default=lambda self: self.env.user.company_id.currency_id.id)
    custom_rate=fields.Float('Custom Rate', related="hs_code.duty_rate")
    total_pr_taxes = fields.Float(
        string='Total_pr_taxes',
        required=False)
    total = fields.Float(
        string='Total', 
        required=False)
    




    @api.onchange('hs_code')
    def onchange_hs_code(self):
        self.type_arabic_name = self.piv_custom_id.type_arabic_name

    @api.onchange('hs_code')
    def onchange_hs_code(self):
        for line in self:
            for git_line in self.piv_custom_id.git_id.piv_products_line_ids:
                if git_line.product_id.product_tmpl_id.hs_code == line.hs_code:
                    line.origin = git_line.origin

    @api.onchange('price', 'total_products_qty_hidden')
    def onchange_method(self):
        self.local_value = self.total_products_qty_hidden * self.price

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        for rec in self:
            rec.price = rec.currency_id.rate_ids[0].inverse_company_rate

    @api.onchange('custom_rate', 'local_value')
    def onchange_total(self):
        self.total = self.local_value * self.custom_rate

