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
        string='Shipping Mode',
        required=False)

    purchase_order_ids = fields.Many2many(
        comodel_name='purchase.order',
        string='Purchase Orders',
        domain = "[('partner_id', '=', partner_id), ('destination_id', '=', destination_id)]",

    )

    purchase_order_ids_domain = fields.Char(
        compute="_compute_purchase_order_ids_domain",
        readonly=True,
        store=False,
    )

    ready_line_ids = fields.One2many(
        comodel_name='purchase.ready.line',
        inverse_name='po_ready_line_id',
        string='Ready_line_ids',
        required=False)

    @api.onchange('purchase_order_ids')
    def onchange_purchase_order_ids(self):
        po_lines = []
        ready_lines = []
        self.purchase_piv_line_ids = [(5, 0)]
        self.ready_line_ids = [(5, 0)]
        for po in self.purchase_order_ids:
            for line in po.order_line:
                    po_lines.append(
                        {
                            "product_id": line.product_id.id,
                            "currency_id": line.currency_id.id,
                            "name": line.name,
                            "product_qty": line.product_qty,
                            "qty_received": line.qty_received,
                            "qty_invoiced": line.qty_invoiced,
                            "price_unit": line.price_unit,
                            "taxes_id": line.taxes_id,
                            "price_subtotal": line.price_subtotal,
                            "price_total": line.price_total,
                            "product_uom": line.product_uom,
                            "price_tax": line.price_tax,
                            "purchase_order_id": po.id,

                        }
                    )
        for line in po_lines:
            self.purchase_piv_line_ids = [(0, 0, line)]
        #
        # for po in self.purchase_order_ids:
        #     products = []
        #     for line in po.order_line:
        #         if line.product_id.id not in products:
        #             products.append(line.product_id.id)
        #     for line in po.order_line:
        #         for product in products:
        #             total_piv_qty = 0
        #             for line in self.purchase_piv_line_ids:
        #                 if line.product_id.id == product and line.purchase_order_id.id == po.id:
        #                     total_piv_qty += line.qty_invoiced
        #             qty = 0
        #             price = 0
        #             if line.product_id.id == product:
        #                 qty += line.product_qty
        #                 price = line.price_unit
        #             ready_lines.append(
        #                 {
        #                     "product_id": product,
        #                     "pending_qty": qty,
        #                     "purchase_order_id": po.id,
        #                     "piv_qty": total_piv_qty,
        #                     "unit_price": price,
        #                 }
        #             )
        # for line in ready_lines:
        #     self.ready_line_ids = [(0, 0, line)]

    @api.onchange('purchase_piv_line_ids')
    def onchange_purchase_piv_line_ids(self):
        ready_lines = []
        piv_pos = []
        piv_pos_products = []
        self.ready_line_ids = [(5, 0)]
        for line in self.purchase_piv_line_ids:
            piv_pos.append(line.purchase_order_id)
        for po in piv_pos:
            for line in po.order_line:
                if line.product_id.id not in piv_pos_products:
                    piv_pos_products.append(line.product_id)
        for product in piv_pos_products:
            total_piv_qty = 0
            qty = 0
            price = 0
            for purchase in piv_pos:
                for line in self.purchase_piv_line_ids:
                    if line.product_id.id == product.id and line.purchase_order_id.id == purchase.id:
                        total_piv_qty += line.qty_invoiced
                        qty += line.product_qty
                        price = line.price_unit
            ready_lines.append(
                {
                    "product_id": product.id,
                    "pending_qty": qty,
                    "purchase_order_id": po.id,
                    "piv_qty": total_piv_qty,
                    "unit_price": price,
                }
            )
        for line in ready_lines:
            self.ready_line_ids = [(0, 0, line)]

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

    #supplier data
    supplier_invoice_number = fields.Char(
        string='Supplier Invoice Number',
        required=False)

    supplier_invoice_date = fields.Date(
        string='Supplier Invoice Date',
        required=False)

    packing_list = fields.Char(
        string='Packing List Ref',
        required=False)

    packing_date = fields.Date(
        string='Packing List Date',
        required=False)

    attach = fields.Binary('Attached')
    
    ready_total = fields.Float(
        string='Total', 
        required=False, compute='_compute_ready_total')

    total_discount = fields.Float(
        string='Total Discount',
        required=False, compute='_compute_ready_total')
    total_vat = fields.Float(
        string='Vat Amount',
        required=False, compute='_compute_ready_total')
    total_net = fields.Float(
        string='Net Total',
        required=False, compute='_compute_ready_total')

    grand_total = fields.Float(
        string='Grand Total SR',
        required=False, compute='_compute_ready_total')

    @api.depends('ready_line_ids')
    def _compute_ready_total(self):
        for rec in self:
            total = 0
            discount = 0
            vat = 0
            for line in rec.ready_line_ids:
                total += line.total
                discount += (line.total * line.disc)
                vat += (line.total * line.vat)
            rec.ready_total = total
            rec.total_discount = discount
            rec.total_net = total - discount
            rec.total_vat = vat
            rec.grand_total = (total - discount) + vat

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

    purchase_order_id = fields.Many2one(comodel_name='purchase.order', string='Purchase_order_id', required=False)
    oc_no = fields.Char(string='Oc No', required=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, index='btree_not_null')
    partner_id = fields.Many2one('res.partner', related="purchase_piv_line_id.partner_id")
    coll_no = fields.Char(string='Coil NO', required=False)
    package_delivery_position = fields.Char(
        string='Package Delivery Position',
        required=False)
    package_description = fields.Char(
        string='Package Description',
        required=False)

    dimensions = fields.Char(
        string='Dimensions(mm)',
        required=False)

    vendor_purchase_code = fields.Char(
        string='Vendor_purchase_code',
        required=False, compute="_compute_vendor_purchase_code")

    name = fields.Text(string='Description', required=False, store=True, readonly=False)
    product_qty = fields.Float(string='Po Quantity', store=True)
    qty_invoiced = fields.Float(string="Billed Qty", store=True)
    product_uom = fields.Many2one('uom.uom', string='Unit', store=True)
    net_weight = fields.Char(string='Net Weight', required=False)
    gross_weight = fields.Char(string='Gross Weight', required=False)
    batch_no = fields.Char(string='Batch NO', required=False)
    serial_no_id = fields.Many2one(comodel_name='piv.serial', string='Serial No', required=False)
    expiry_date = fields.Date(string='Expiry Date', required=False)
    production_date = fields.Date(string='Production Date', required=False)

    @api.depends('product_id', 'partner_id')
    def _compute_vendor_purchase_code(self):
        for rec in self:
            value = False
            for line in rec.product_id.seller_ids:
                if line.partner_id.id == rec.partner_id.id:
                    value = line.product_code
            rec.vendor_purchase_code = value


    # currency_id = fields.Many2one(store=True, string='Currency', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    # product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    # product_uom_category_id = fields.Many2one()
    qty_received = fields.Float("Received Qty", compute_sudo=True, store=True, digits='Product Unit of Measure')
    qty_invoiced = fields.Float(string="Billed Qty", digits='Product Unit of Measure', store=True)
    price_unit = fields.Float(
        string='Unit Price', required=False, digits='Product Price', readonly=False, store=True)
    price_subtotal = fields.Monetary(string='Subtotal', store=True)
    price_total = fields.Monetary(string='Total', store=True)
    # product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    price_tax = fields.Float(string='Tax', store=True)
    company_id = fields.Many2one('res.company', 'Company', required=False, index=True, default=lambda self: self.env.company.id)
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    serial_no = fields.Char(
        string='Serial NO',
        required=False)
    serial_mts = fields.Binary('Serial MTC')
    serial_calibration_cert = fields.Binary('Serial Calibration Cert')


class PurchaseReadyLines(models.Model):
    _name = 'purchase.ready.line'
    _description = 'PurchaseReadyLines'

    name = fields.Char()
    po_ready_line_id = fields.Many2one(comodel_name='purchase.piv', string='po_ready_line_id', required=False)

    partner_id = fields.Many2one('res.partner', related="po_ready_line_id.partner_id")
    purchase_order_id = fields.Many2one(comodel_name='purchase.order', string='Purchase_order_id', required=False)
    product_id = fields.Many2one('product.product', string='Vendor Purchase Code', domain=[('purchase_ok', '=', True)], change_default=True, index='btree_not_null')
    product_uom = fields.Many2one('uom.uom', string='Unit', store=True)
    pending_qty = fields.Float(string='Pending QTY', required=False)
    piv_qty = fields.Float(string='PIV QTY', required=False)
    unit_price = fields.Float(string='Unit Price', required=False)
    disc = fields.Float(string='Disc', required=False)
    vat = fields.Float(string='Vat', required=False)
    total = fields.Float(string='Total', required=False, compute="_compute_total")


    @api.depends('piv_qty', 'unit_price')
    def _compute_total(self):
        for rec in self:
            total = 0
            total = rec.piv_qty * rec.unit_price
            rec.total = total