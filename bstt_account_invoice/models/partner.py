#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    foreign_name = fields.Char('Name')
    arabic_street = fields.Char('Street')
    arabic_street2 = fields.Char('Street2')
    arabic_city = fields.Char('City')
    arabic_state = fields.Char('State')
    arabic_country = fields.Char('Country')
    arabic_zip = fields.Char('Zip')
