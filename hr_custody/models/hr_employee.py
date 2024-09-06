# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_custody(self):
        """This compute the loan amount and total Custody count of an employee.
            """
        self.custody_count = self.env['hr.custody'].search_count([('employee_id', '=', self.id)])

    custody_count = fields.Integer(string="Custody Count", compute='_compute_employee_custody')

    def act_hr_employee_custody_request(self):
        custody_ids = self.env['hr.custody'].search([('employee_id', '=', self.id)])
        print('--------------', custody_ids)
        action_vals = {
            'name': _('HR Custody'),
            'domain': [('id', 'in', custody_ids.ids)],
            'view_type': 'form',
            'res_model': 'hr.custody',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(custody_ids) > 0:
            action_vals.update({'res_id': custody_ids[0].id, 'view_mode': 'tree,form'})
        else:
            action_vals.update({'view_mode': 'form',
                                'domain': [('employee_id', '=', self.id)],
                                'context': {
                                    "default_employee_id": self.id,

                                }})
        return action_vals
