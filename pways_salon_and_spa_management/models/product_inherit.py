# -*- coding: utf-8 -*-
from odoo import fields, models, api

class InheritProduct(models.Model):
    _inherit = 'product.template'

    salon_spa = fields.Boolean(string="Salon spa")
    is_salon_product = fields.Boolean(string="Salon Product")
    is_spa_product = fields.Boolean(string="Spa Product")
    salon_booking_id = fields.Many2one('salon.booking',string="Salon Bookings")
    is_combo = fields.Boolean('Combo Product', default=False)
    combo_product_ids = fields.One2many('product.combo', 'product_template_id', 'Combo Item')
    total = fields.Float(string="Total", compute='_compute_total_quantity')
    display_name = fields.Char('Display Name')
    product_ids = fields.Many2many('product.product', string="Select Products", domain="['|', ('is_salon_product', '=', True), ('is_spa_product', '=', True)]")
    membership_time = fields.Selection([('12_months','12 Months'), ('6_months','6 Months'), ('3_months','3 Months')], default="12_months", string="TIme")
    discount = fields.Float(string="Discount %", default=10)

    @api.depends('combo_product_ids.price')
    def _compute_total_quantity(self):
        total = 0
        if self.combo_product_ids:
            for rec in self.combo_product_ids:
                total += rec.price
            self.total = total
        else:
            self.total = 0 

    @api.onchange('combo_product_ids')
    def _compute_list_price_quantity(self):
        if self.is_combo:
            self.list_price = self.total

class Product(models.Model):
    _inherit = "product.product"


    def name_get(self):
        result = []
        res = super(Product, self).name_get()
        for rec in self:
            if rec.is_combo:
                product_names = rec.name + ' - '
                for combo in self.combo_product_ids:
                    product_names += ' ( '+ combo.product_id.name + ')'
                    print("Name...................", product_names)
                result.append((rec.id, product_names))
                print("result...", result)
            else:
                result.append((rec.id, rec.name))
        return result

class ComboProduct(models.Model):
    _name = "product.combo"
    _description = "Product packs"

    name = fields.Char('name')
    product_template_id = fields.Many2one('product.template', 'Item')
    product_quantity = fields.Float('Quantity', default='1', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id')
    price = fields.Float(string="Price", related="product_id.list_price", store=True)
