# -*- coding: utf-8 -*-
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class Partner(models.Model):
    _inherit = 'res.partner'

    salon_spa = fields.Boolean(string="Salon Or spa")
    partner_salon = fields.Boolean(string="Is a Salon Partner")
    is_salon_product = fields.Boolean(string="Salon Product")
    is_spa_product = fields.Boolean(string="Spa Product")
    membership_end_date = fields.Date(string='End Date')
    membershiplines_ids = fields.Many2one('membership.membership_line', string="Membership Lines")

class MembershipLines(models.Model):
    _inherit = "membership.membership_line"

    membership_end_date = fields.Datetime(string='End Date', compute="_calculate_end_date")

    @api.depends('date')
    def _calculate_end_date(self):
        for rec in self:
            for member in rec:
                membership = self.env['product.template'].search([('name', '=', member.membership_id.name)])
                for memberships in membership:
                    if memberships.membership_time == '12_months':
                        membership_duration = 12
                    if memberships.membership_time == '6_months':
                        membership_duration = 6
                    if memberships.membership_time == '3_months':
                        membership_duration = 3
                    end_date = member.date +  relativedelta(months=membership_duration)
                    member.membership_end_date = end_date
