from odoo import api, fields, models
import json



class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    destination_id = fields.Many2one('destination', string='Destination')
    # destination_id = fields.Many2one('destination', string='Destination',default=lambda self: self.env['res.partner.destination'].search([('destination_line_id', '=', self.partner_id.id),('is_default', '=', True)], limit=1))

    supplier_line_ids = fields.One2many(
        comodel_name='product.supplierinfo.line',
        inverse_name='supplier_line_id',
        string='Supplier Lines',
        required=False)

class ProductSupplierinfoLine(models.Model):
    _name = 'product.supplierinfo.line'
    _description = 'Product Supplier info Line'

    supplier_line_id = fields.Many2one(
        comodel_name='product.supplierinfo',
        string='',
        required=False)

    product_id = fields.Many2one('product.product', string="Vendor Product Group", required=True)

    vendor_purchase_code = fields.Char(
        string='Vendor Purchase Code',
        required=False)

    vendor_barcode = fields.Char(
        string='Vendor EAU/UPC-Code (barcode)',
        required=False)

    vendor_description = fields.Char(
        string='Vendor Description',
        required=False)

    uom_po_id = fields.Many2one('uom.uom', 'Purchase UoM')

    unit_purchase_price = fields.Float(
        string='Unit Purchase Price',
        required=False)

    currency_id = fields.Many2one('res.currency', 'Currency', required=True)

    eta_at_supplier = fields.Integer(
        string='Eta At Supplier',
        required=False)

    box_qty_uom_id = fields.Many2one('uom.uom', 'Box Qty')
    box_ratio = fields.Float(
        string='Box Ratio',
        required=False, related='box_qty_uom_id.factor_inv')

    dimension = fields.Char(
        string='Dimension',
        required=False)

    pallet_qty_uom_id = fields.Many2one('uom.uom', 'Pallet Qty')
    pallet_ratio = fields.Float(
        string='Pallet Ratio',
        required=False, related='pallet_qty_uom_id.factor_inv')

    pallet_dimension = fields.Char(
        string='Dimension',
        required=False)

    weight = fields.Float(
        string='Weight',
        required=False)

    volume = fields.Float(
        string='Volume',
        required=False)

    country_of_origin = fields.Many2one('res.country', 'Origin of Goods')
    hs_code = fields.Many2one('hs.code', string="HS Code")

    uom_id_domain = fields.Char(
        compute="_compute_uom_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends('uom_po_id', 'product_id')
    def _compute_uom_id_domain(self):
        uom_ids = []
        for rec in self:
            if rec.product_id.uom_po_id.category_id:
                for line in rec.product_id.uom_po_id.category_id.uom_ids:
                    uom = self.env['uom.uom'].search([('name', '=', line.name)], limit=1)
                    uom_ids.append(uom.id)

            rec.uom_id_domain = json.dumps(
                [('id', 'in', uom_ids)])


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.vendor_barcode = self.product_id.barcode
            self.vendor_description = self.product_id.description_purchase
            self.weight = self.product_id.weight
            self.volume = self.product_id.volume
            self.country_of_origin = self.product_id.country_of_origin.id
            self.hs_code = self.product_id.hs_code.id
            self.uom_po_id = self.product_id.uom_po_id.id

    @api.onchange('supplier_line_id')
    def onchange_method(self):
        self.vendor_purchase_code = self.supplier_line_id.product_code



    @api.onchange('box_qty_uom_id', 'pallet_qty_uom_id')
    def onchange_method(self):
        for line in self.product_id.uom_po_id.category_id.uom_ids:
            if line.name == self.box_qty_uom_id:
                self.box_ratio = line.ratio

            if line.name == self.pallet_qty_uom_id:
                self.pallet_ratio = line.ratio



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id', 'product_template_id')
    def onchange_method(self):
        if self.product_id.id and self.order_id.partner_id and self.order_id.destination_id:
            pricelist = self.env['product.supplierinfo'].search([('destination_id', '=', self.order_id.destination_id.id),('product_tmpl_id', '=', self.product_id.product_tmpl_id.id), ('partner_id', '=', self.order_id.partner_id.id)]).filtered(lambda d: d.date_start != False).sorted(
                key=lambda x: x.date_start)
            print('pricelist >>', pricelist)
            for line in pricelist.supplier_line_ids:
                if line.product_id == self.product_id:
                    self.price_unit = line.unit_purchase_price
