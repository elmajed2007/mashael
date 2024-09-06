# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class HolidaysTypes(models.Model):
    _inherit = "hr.leave.type"

    is_sick_timeOff = fields.Boolean('Sick Timeoff', default=False)


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    is_travel_chk = fields.Boolean('There is a travel allowance', default=False)
    is_travel_done = fields.Boolean('The travel allowance is done', default=False)
    is_check_compute = fields.Boolean(default=False)

    # @api.constrains("attachment_ids", "supported_attachment_ids", "holiday_status_id")
    def check_supported_attachment(self):
        for leave in self:
            if leave.leave_type_support_document and not leave.supported_attachment_ids:
                raise UserError(_("You have to include attachments for this leave type."))

    def _get_sick_duration(self):
        for rec in self.env['hr.leave'].sudo().search([('state', '=', 'validate'), ('is_check_compute', '=', False)]):
            if rec.holiday_status_id.is_sick_timeOff:
                rec.employee_id.sick_timeoff_duration += rec.number_of_days
                rec.is_check_compute = True

    def write(self, values):
        if 'supported_attachment_ids' in values:
            attachment = values['supported_attachment_ids'][0][2]
            if not attachment and self.leave_type_support_document:
                raise UserError(_("You have to include attachments for this leave type."))
        res = super(HolidaysRequest, self).write(values)
        return res

    @api.model
    def create(self, vals):
        leave = super(HolidaysRequest, self).create(vals)
        leave.check_supported_attachment()
        return leave
