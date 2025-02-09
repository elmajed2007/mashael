from odoo import models, fields, api,_
from odoo.tools import frozendict, format_date, float_compare, Query

# class ProductTemplate(models.Model):
#     _inherit = "product.template"

#     @api.depends('product_variant_ids.barcode')
#     def _compute_barcode(self):
#         self.barcode = False
#         for template in self:
#             # TODO master: update product_variant_count depends and use it instead
#             variant_count = len(template.product_variant_ids)
#             if variant_count == 1:
#                 template.barcode = template._ensure_barcode_format(template.product_variant_ids.barcode)
#             elif variant_count == 0:
#                 archived_variants = template.with_context(active_test=False).product_variant_ids
#                 if len(archived_variants) == 1:
#                     template.barcode = template._ensure_barcode_format(archived_variants.barcode)

#     def _search_barcode(self, operator, value):
#         query = self.with_context(active_test=False)._search([('product_variant_ids.barcode', operator, value)])
#         return [('id', 'in', query)]

#     def _set_barcode(self):
#         variant_count = len(self.product_variant_ids)
#         if variant_count == 1:
#             self.product_variant_ids.barcode = self._ensure_barcode_format(self.barcode)
#         elif variant_count == 0:
#             archived_variants = self.with_context(active_test=False).product_variant_ids
#             if len(archived_variants) == 1:
#                 archived_variants.barcode = self._ensure_barcode_format(self.barcode)

#     def _ensure_barcode_format(self, barcode):
#         """Ensure the barcode starts with '00'."""
#         if barcode and not barcode.startswith('00'):
#             return '00' + barcode
#         return barcode

class AccountMove(models.Model):
    _inherit = "account.move"



    # qr_code = fields.Binary(string='QR code', copy=False)
    discount_type = fields.Selection([
        ("percentage", "Percentage"),
        ("fixed", "Fixed")], string="Discount Type", default="percentage")
    discount_rate = fields.Float(string='Discount Value', digits='Account', default=0.0)
    price = fields.Float(string='Price Before Tax', digits='Account', default=0.0, compute='_compute_amount_discount')
    tax = fields.Float(string='Tax Amount', digits='Account', default=0.0, compute='_compute_amount_discount')
    amount_discount = fields.Monetary('Amount After Discount', compute='_compute_amount_discount')
    amount_disc = fields.Monetary('Disc Amount', compute='_compute_total_disc')
    discount_val = fields.Monetary('Price After Tax', compute='_compute_amount_discount')

    @api.onchange("discount_rate","invoice_line_ids.discount_fixed","invoice_line_ids.product_id","discount_fixed")
    def _compute_amount_discount(self):
        for order in self:
            for line in order.invoice_line_ids:
                if order.discount_type == "percentage":
                    order.amount_discount = (order.amount_residual - (order.amount_residual*order.discount_rate)/100)
                    order.discount_val = order.tax + order.price
                else:
                    order.amount_discount = (order.amount_residual - order.discount_rate)
                    order.discount_val = order.tax + order.price

                order.price = order.amount_discount/1.15
                order.tax = (order.amount_discount*0.15)/1.15
                order.discount_val = order.tax + order.price

            print('sssssssssssssssss',order.amount_disc)


    # def _onchangediscount(self):
    #     for rec in self:
    #         for record in rec.invoice_line_ids:
    #             if record.discount_fixed:
    #                 rec.discount_value = record.discount_fixed
    #             if record.discount:
    #                 rec.discount_value = (record.discount * record.price_unit)/100
    #             rec.price_unit_dub = record.price_unit
    total_discount = fields.Float('Discount Total', default=0.0, compute='_compute_total_disc')
    total_price_unit = fields.Float('Total Price Unit', default=0.0, compute='_compute_total_disc')

    def _compute_total_disc(self):
        amount = 0
        total = 0
        disc = 0
        sdisc = 0
        for line in self.invoice_line_ids:
            amount += line.discount_fixed + self.amount_discount
            total += line.price_unit * line.quantity
            disc += line.discount_fixed + ((line.discount/100)*line.quantity*line.price_unit)
            if line.product_id.name =='Special discount':
                sdisc += line.price_subtotal
        self.total_discount = amount
        self.total_price_unit = total
        self.amount_disc = self.discount_rate + disc - sdisc



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_value = fields.Float(
        string='Disc Value ',store=True
    )

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False
            # Compute 'price_subtotal'.
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0)) - line.discount_value
            subtotal = line.quantity * line_discount_price_unit

            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded']
                line.price_total = taxes_res['total_included']
            else:
                line.price_total = line.price_subtotal = subtotal

