from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError, ValidationError, AccessError

class CreateCommisionInvoice(models.Model):
    _name = 'create.invoice.commission'
    _description = 'create invoice commission'

    def invoice_create(self):
        pass