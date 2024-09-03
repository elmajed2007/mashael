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

    # po_piv = fields.Integer(compute='compute_po_piv')
    #
    # def compute_po_piv(self):
    #     for rec in self:
    #         rec.po_piv = len(
    #             rec.env['purchase.piv'].search([('purchase_order_ids', 'in', rec.id)]))


    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('piv', 'Piv'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)


    def create_piv(self):
        po = []
        po.append(self.id)
        piv = self.env['purchase.piv'].create({
            'partner_id': self.partner_id.id,
            'destination_id': self.destination_id.id,
            # 'purchase_order_ids': po,
        })
        print('piv >>', piv)
        self.write({'state': 'piv'})

