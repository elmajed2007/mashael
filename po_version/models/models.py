from odoo import api, fields, models


class PoVersion(models.Model):
    _name = 'po.version'
    _description = 'Po Version'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, change_default=True, tracking=True, help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    partner_ref = fields.Char('Vendor Reference', copy=False,
        help="Reference of the sales order or bid sent by the vendor. "
             "It's used to do the matching when you receive the "
             "products as this reference is usually written on the "
             "delivery order sent by your vendor.")
    date_approve = fields.Datetime('Confirmation Date', readonly=False, index=True, copy=False)
    date_planned = fields.Datetime(
        string='Expected Arrival', index=True, copy=False, compute='_compute_date_planned', store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")
    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        required=False)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)

    order_line = fields.One2many('po.version.line', 'order_id', string='Order Lines', copy=True)




class PoVersionLine(models.Model):
    _name = 'po.version.line'
    _inherit = 'analytic.mixin'
    _description = 'Po Version Line'

    order_id = fields.Many2one(
        comodel_name='po.version',
        string='order_id',
        required=False)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=False)


    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, index='btree_not_null')
    name = fields.Text(
        string='Description', required=True, store=True,
        readonly=False)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, store=True, readonly=False)

    qty_received = fields.Float("Received Qty", compute_sudo=True, store=True, digits='Product Unit of Measure')
    qty_invoiced = fields.Float(string="Billed Qty", digits='Product Unit of Measure', store=True)
    price_unit = fields.Float(
        string='Unit Price', required=True, digits='Product Price',
        readonly=False, store=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    price_subtotal = fields.Monetary(string='Subtotal', store=True)
    price_total = fields.Monetary(string='Total', store=True)
    price_tax = fields.Float(string='Tax', store=True)

