from odoo import api, fields, models , _
from dateutil.relativedelta import relativedelta



class MshGit(models.Model):
    _name = 'msh.git'
    _description = 'Git'
    _rec_name = "name"



    name = fields.Char()
    partner_id = fields.Many2one('res.partner', string='Vendor')
    destination_id = fields.Many2one(comodel_name='destination', string='Destination', domain="[('partner_id', '=', partner_id)]")
    loading_port_id = fields.Many2one(
        comodel_name='msh.port',
        string='Port Of Loading',
        required=False)

    destination_port_id = fields.Many2one(
        comodel_name='msh.port',
        string='Find Destination Board',
        required=False)

    stock_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='To Wh',
        required=False)

    shipping_date = fields.Date(
        string='Shipping Date',
        required=False)

    clearing_agent = fields.Char(
        string='Clearing Agent',
        required=False)

    transporter = fields.Char(
        string='Transporter',
        required=False)

    piv_line_ids = fields.One2many(
        comodel_name='msh.git.piv.line',
        inverse_name='piv_line_id',
        string='',
        required=False)

    @api.onchange('piv_line_ids')
    def onchange_piv_line_ids(self):
        po_lines = []
        self.piv_products_line_ids = [(5, 0)]
        for piv in self.piv_line_ids:
            for line in piv.piv_id.purchase_piv_line_ids:
                    po_lines.append(
                        {
                            "product_id": line.product_id.id,
                            "po_quantity": line.product_qty,
                            "piv_quantity": line.qty_invoiced,
                            "hs_code": line.product_id.hs_code.id,
                            "eta": (self.shipping_date + relativedelta(days=self.destination_id.duration)) if self.shipping_date else False,
                        }
                    )
        for line in po_lines:
            self.piv_products_line_ids = [(0, 0, line)]


    piv_products_line_ids = fields.One2many(
        comodel_name='piv.products.lines',
        inverse_name='piv_products_line_id',
        string='',
        required=False)
    #
    carrier_name = fields.Char(
        string='Carrier Name',
        required=False)
    vessel_flight = fields.Char(
        string='Vessel/Flight No./Plate No',
        required=False)
    bl_manifest = fields.Char(
        string='Bl/Manifest',
        required=False)
    manifest_date = fields.Date(
        string='Date',
        required=False)
    manifest_attachment = fields.Binary('Attach')
    create_bayan_no = fields.Char(
        string='Create Bayan No',
        required=False)
    manual_date = fields.Date(
        string='(Manual) Date',
        required=False)
    current_attachment = fields.Binary('(Current Enable Manual Change)Attach')






    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('msh.git') or _('New')
        result = super(MshGit, self).create(vals)
        return result

class mshGitLine(models.Model):
    _name = 'msh.git.piv.line'

    piv_line_id = fields.Many2one(
        comodel_name='msh.git',
        string='',
        required=False)
    destination_id = fields.Many2one('destination', string='Destination', related="piv_line_id.destination_id")

    piv_id = fields.Many2one(
        comodel_name='purchase.piv',
        string='Piv',
        required=False,domain="[('destination_id', '=', destination_id)]")

    supplier_inv_num = fields.Char(
        string='Supplier Inv Num',
        required=False, related="piv_id.supplier_invoice_number")

    supplier_inv_date = fields.Date(
        string='Supplier Inv Date',
        required=False, related="piv_id.supplier_invoice_date")

    value = fields.Float(
        string='Value',
        required=False, related="piv_id.total")

    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency")

    is_select = fields.Boolean(
        string='Select Check Box',
        required=False)

    packing_list_ref = fields.Char(
        string='Packing List Ref',
        required=False)

    container_num = fields.Char(
        string='Container Num',
        required=False)

    coo_no = fields.Char(
        string='Coo.No.',
        required=False)

    coo_date = fields.Date(
        string='Coo.Date.',
        required=False)

    attachment = fields.Binary('Attach')
    
class PivProductsLines(models.Model):
    _name = 'piv.products.lines'

    piv_products_line_id = fields.Many2one(
        comodel_name='msh.git',
        string='',
        required=False)

    # shipping_date = fields.Date(
    #     string='Shipping Date',
    #     required=False, related='piv_products_line_id.shipping_date')
    product_id = fields.Many2one('product.product', string='Po')
    code = fields.Char(string='Code', required=False, related='product_id.code')
    # description = fields.Char(string='Description', required=False)
    description = fields.Html('Description', related='product_id.description')

    po_quantity = fields.Float(string='Po Quantity', required=False)
    piv_quantity = fields.Float(string='Piv Quantity', required=False)
    packing_list_number = fields.Char(string='Packing List Number', required=False)
    call_no = fields.Char(string='Call No', required=False)
    hs_code = fields.Many2one('hs.code', string="HS Code", related='product_id.hs_code')
    origin = fields.Char(string='Origin', required=False)
    saber_reguiation = fields.Char(string='Saber Reguiation', required=False)
    cart_no = fields.Char(string='Cart No', required=False)
    cert_expiration_date = fields.Date(string='Cert Expiration Date', required=False)
    eta = fields.Date(
        string='ETA',
        required=False)

    @api.onchange('piv_products_line_id.shipping_date', 'description')
    def onchange_method(self):
        self.eta = self.piv_products_line_id.shipping_date + relativedelta(days=self.description.duration)
