from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    confirmation_movement_ids = fields.One2many(
        comodel_name='po.confirmed.move',
        inverse_name='confirmation_movement_id',
        string='Confirmation_movement_ids',
        required=False)


    @api.constrains('confirmation_movement_ids')
    def check_confirmation_movement_ids(self):
        for line in self.confirmation_movement_ids:
            for po_line in self.order_id:
                if line.product_id.id == po_line.product_id.id:
                    if line.product_qty > po_line.product_qty:
                        raise ValidationError(_('You Cannot Confirm Qty More Than Requested'))


class PoConfirmedMove(models.Model):
    _name = 'po.confirmed.move'

    confirmation_movement_id = fields.Many2one(
        comodel_name='purchase.order',
        string='',
        required=False)


    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, index='btree_not_null')

    product_ids_domain = fields.Char(
        compute="_compute_product_ids_domain",
        readonly=True,
        store=False,
    )

    def _compute_product_ids_domain(self):
        for rec in self:
            rec.product_ids_domain = json.dumps([('id', 'in', self.env['purchase.order'].search([('id', '=', rec.confirmation_movement_id.id)]).mapped('order_line.product_id'))])

    product_qty = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id')
    confirmed_date = fields.Date(
        string='Confirmed Date',
        required=False)
