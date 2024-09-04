import json
from odoo import api, fields, models, _



class PurchasePiv(models.Model):
    _name = 'purchase.piv'
    _description = 'Purchase Piv'

    name = fields.Char()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.piv') or _('New')
        result = super(PurchasePiv, self).create(vals)
        return result

    currency_id = fields.Many2one('res.currency', 'Currency')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)

    #vendor
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, tracking=True, help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    destination_id = fields.Many2one(
        comodel_name='destination',
        string='Destination_id',
        required=False)

    purchase_order_ids = fields.Many2many(
        comodel_name='purchase.order',
        string='Purchase Orders')

    purchase_order_ids_domain = fields.Char(
        compute="_compute_purchase_order_ids_domain",
        readonly=True,
        store=False,
    )

    @api.depends('partner_id')
    def _compute_purchase_order_ids_domain(self):
        purchase = []
        for rec in self:
            if rec.partner_id:
                purchase_orders = self.env['purchase.order'].search([('partner_id', '=', rec.partner_id.id), ('destination_id', '=', rec.destination_id.id)])
                for po in purchase_orders:
                    purchase.append(po.id)
            rec.purchase_order_ids_domain = json.dumps(
                [('id', 'in', purchase)])
    @api.onchange('purchase_order_ids')
    def onchange_purchase_order_ids(self):
        po_lines = []
        self.purchase_piv_line_ids = [(5, 0)]
        for po in self.purchase_order_ids:
            for line in po.order_line:
                    po_lines.append(
                        {
                            "product_id": line.product_id.id,
                            # "currency_id": line.currency_id.id,
                            "name": line.name,
                            "product_qty": line.product_qty,
                            # "product_uom_category_id": line.product_uom_category_id,
                            # "qty_received": line.qty_received,
                            # "qty_invoiced": line.qty_invoiced,
                            # "price_unit": line.price_unit,
                            # "taxes_id": line.taxes_id,
                            # "price_subtotal": line.price_subtotal,
                            # "price_total": line.price_total,
                            # "product_uom": line.product_uom,
                            # "price_tax": line.price_tax,
                            # "purchase_order_id": line.order_id.id,

                        }
                    )
        for line in po_lines:
            self.purchase_piv_line_ids = [(0, 0, line)]

    #supplier data
    supplier_invoice_number = fields.Char(
        string='Supplier Invoice Number',
        required=False)

    supplier_invoice_date = fields.Date(
        string='Supplier Invoice Date',
        required=False)

    packing_list = fields.Char(
        string='Packing List',
        required=False)

    purchase_piv_line_ids = fields.One2many(
        comodel_name='purchase.piv.line',
        inverse_name='purchase_piv_line_id',
        string='',
        required=False)

    total_lines = fields.Float(
        string='Total Lines',
        required=False, compute='_compute_total_lines')

    total = fields.Float(
        string='Total',
        required=False)

    @api.depends('purchase_piv_line_ids.price_total')
    def _compute_total_lines(self):
        for rec in self:
            total = 0
            for line in rec.purchase_piv_line_ids:
                total += line.price_total
            rec.total_lines = total
            rec.total = total




class PurchasePivLine(models.Model):
    _name = 'purchase.piv.line'
    _description = 'Purchase Piv Line'

    purchase_piv_line_id = fields.Many2one(
        comodel_name='purchase.piv',
        string='purchase_piv_line_id',
        required=False)

    currency_id = fields.Many2one(store=True, string='Currency', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)])
    name = fields.Text(
        string='Description', required=True, store=True,
        readonly=False)
    product_qty = fields.Float(string='Quantity')
    # product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    # product_uom_category_id = fields.Many2one()
    #
    # qty_received = fields.Float("Received Qty", compute_sudo=True, store=True)
    # qty_invoiced = fields.Float(string="Billed Qty", store=True)
    # price_unit = fields.Float(
    #     string='Unit Price', required=True, digits='Product Price', readonly=False, store=True)
    # taxes_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    # price_subtotal = fields.Monetary(string='Subtotal', store=True)
    price_total = fields.Monetary(string='Total', store=True)
    # # product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    # product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    # # price_tax = fields.Float(string='Tax', store=True)
    # coll_no = fields.Char(
    #     string='Coll NO',
    #     required=False)
    # company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    #
    # purchase_order_id = fields.Many2one(
    #     comodel_name='purchase.order',
    #     string='Purchase_order_id',
    #     required=False)
    #
    #
    # serial_no = fields.Char(
    #     string='Serial NO',
    #     required=False)
    #
    # serial_mts = fields.Binary('Serial MTC')
    # serial_calibration_cert = fields.Binary('Serial Calibration Cert')
    # #
    # # serial_no_ids = fields.Many2one(
    # #     comodel_name='piv.serial',
    # #     string='Serial No',
    # #     required=False)
    #
    # expiry_date = fields.Date(
    #     string='Expiry Date',
    #     required=False)
    #
    # production_date = fields.Date(
    #     string='Production Date',
    #     required=False)
    #
    # batch_no = fields.Char(
    #     string='Batch NO',
    #     required=False)
    #
    # net_weight = fields.Char(
    #     string='Net Weight',
    #     required=False)
