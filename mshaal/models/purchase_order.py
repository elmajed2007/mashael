from odoo import models, fields, api
from datetime import timedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, change_default=True, tracking=True, help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    destination_id = fields.Many2one('destination',string='Destination',domain="[('partner_id', '=', partner_id)]")

    @api.onchange('order_line','destination_id')
    def _onchange_order_line(self):
        for line in self.order_line:
            if self.date_planned:
                line.expected_arrival_date = self.date_planned

    date_planned = fields.Datetime(
        string='Expected Arrival', index=True, copy=False, compute='_compute_custome_date_planned', store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")

    def _compute_custome_date_planned(self):
        for rec in self:
            rec.date_planned = rec.date_order + timedelta(days=rec.destination_id.duration)


    # @api.onchange('partner_id','destination_id','date_order')
    # def compute_date(self):
    #     for record in self:
    #         for rec in record.destination_id:
    #             if rec.duration and record.date_order:
    #                 record.date_planned = record.date_order + timedelta(days=rec.destination_id.duration)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    expected_arrival_date=fields.Datetime("Expected Arrival")
    hs_code = fields.Many2one('hs.code', string="HS Code", related='product_id.hs_code')
    discount = fields.Float(
        string='Discount', 
        required=False)



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    purchase_id=fields.Many2one('purchase.order',"PO",store=True)

class srProductWarranty(models.Model):
    _inherit = "sr.product.warranty"

    sale_order_id = fields.Many2one('sale.order', "PO")
    purchase_id=fields.Many2one('purchase.order',"PO",compute="compute_po")

    def compute_po(self):
        sale_id = self.env["sale.order"].search(
            [("partner_id", "=", self.partner_id.id)]
        )
        for record in self:
            for rec in sale_id:
                if rec.partner_id:
                    record.purchase_id = rec.order_line.purchase_id

