from odoo import api, fields, models



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'



    def piv_action(self):
        return {
            'name': 'Piv',
            'view_mode': 'tree,form',
            'res_model': 'purchase.piv',
            'type': 'ir.actions.act_window',
            'domain': [('purchase_order_ids', 'in', self.id)],
        }

    po_piv = fields.Integer(compute='compute_po_piv')

    def compute_po_piv(self):
        for rec in self:
            rec.po_piv = len(
                rec.env['purchase.piv'].search([('purchase_order_ids', 'in', rec.id)]))


    # state = fields.Selection([
    #     ('draft', 'RFQ'),
    #     ('sent', 'RFQ Sent'),
    #     ('piv', 'Piv'),
    #     ('to approve', 'To Approve'),
    #     ('purchase', 'Purchase Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled')
    # ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    #
    state = fields.Selection(selection_add=[ ('piv', 'Piv'),
        ('to approve', 'To Approve')])



    def create_piv(self):
        po = []
        po_lines = []
        po.append(self.id)
        for line in self.order_line:
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
                    "price_tax": line.price_tax,
                    "purchase_order_id": self.id,

                }
            )
        piv = self.env['purchase.piv'].create({
            'partner_id': self.partner_id.id,
            'destination_id': self.destination_id.id,
            'purchase_order_ids': po,
        })
        for line in po_lines:
            piv.purchase_piv_line_ids = [(0, 0, line)]

        print('piv >>', piv)
        self.write({'state': 'piv'})

