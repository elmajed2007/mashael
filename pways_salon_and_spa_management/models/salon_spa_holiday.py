from odoo import api, fields, models

class SalonHoliday(models.Model):
    _name = 'salon.holiday'
    _description = 'Salon Holiday'

    name = fields.Char(string="Name")
    holiday = fields.Boolean(string="Holiday")