from odoo import api, fields, models



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def button_confirm(self):
        res = super().button_confirm()
        self.create_po_version()

        return res

    def po_versions_action(self):
        return {
            'name': 'Po Versions',
            'view_mode': 'tree,form',
            'res_model': 'po.version',
            'type': 'ir.actions.act_window',
            'domain': [('purchase_order_id', '=', self.id)],
        }


    po_versions_count = fields.Integer(compute='compute_po_versions_count')

    def compute_po_versions_count(self):
        for rec in self:
            rec.po_versions_count = len(
                rec.env['po.version'].search([('purchase_order_id', '=', rec.id)]))





    def create_po_version(self):
        vals = {}
        po_history = self.env['po.version'].search([('purchase_order_id', '=', self.id)])
        print('len(po_history) >>>', len(po_history))
        po_ver_seq = 0
        if len(po_history) > 0:
            att = len(po_history)
            po_ver_seq = str(att + 1)
        if len(po_history) == 0:
            po_ver_seq = str(1)

        po_version = self.env['po.version'].create({
                'name': "V" + po_ver_seq,
                'purchase_order_id': self.id,
                'partner_id': self.partner_id.id,
                'partner_ref': self.partner_ref,
                'date_approve': self.date_approve,
                'date_planned': self.date_planned,
            })
        for line in self.order_line:
            po_version.order_line = [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_qty': line.product_qty,
                'qty_received': line.qty_received,
                'qty_invoiced': line.qty_invoiced,
                'price_unit': line.price_unit,
                'taxes_id': line.taxes_id,
                'price_subtotal': line.price_subtotal,
                'price_total': line.price_total,
                'price_tax': line.price_tax,
            })]



    def write(self, vals):
        res = super().write(vals)
        self.create_po_version()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.create_po_version()
        return res
