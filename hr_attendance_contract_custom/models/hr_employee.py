# -*- coding: utf-8 -*-

from odoo import models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    def _late_hours(self, date_from, date_to, act_hour_period):
        for rec in self:
            attendance_obj = self.env['hr.attendance'].search(
                [('employee_id', '=', rec.id), ('att_date', '>=', date_from), ('att_date', '<=', date_to),
                 ('late_in', '>', 0)])
            act_hours = attendance_obj.search(
                [('employee_id', '=', rec.id), ('att_date', '>=', date_from), ('att_date', '<=', date_to),
                 ('act_late_in', '>', act_hour_period)])
            total_hours = sum(attendance_obj.mapped('late_in')) + sum(act_hours.mapped('act_late_in'))
            return total_hours

    def _diff_hours(self, date_from, date_to, act_hour_period):
        for rec in self:
            attendance_obj = self.env['hr.attendance'].search(
                [('employee_id', '=', rec.id), ('att_date', '>=', date_from), ('att_date', '<=', date_to),
                 ('diff_time', '>', 0)])
            act_hours = attendance_obj.search(
                [('employee_id', '=', rec.id), ('att_date', '>=', date_from), ('att_date', '<=', date_to),
                 ('act_diff_time', '>', act_hour_period)])
            total_hours = sum(attendance_obj.mapped('diff_time')) + sum(act_hours.mapped('act_diff_time'))
            return total_hours

    def _working_hours(self, date_from, date_to, hour_period):
        for rec in self:
            attendance_obj = self.env['hr.attendance'].search(
                [('employee_id', '=', rec.id), ('att_date', '>=', date_from), ('att_date', '<=', date_to),
                 ('is_weekend', '=', 0), ('is_public_holiday', '=', 0), ('overtime_hours', '>', hour_period)])
            overtime_request_obj = self.env['hr.overtime.request'].sudo().search([('employee_id', '=', rec.id),
                                                                                  ('overtime_date', '>=', date_from),
                                                                                  ('overtime_date', '<=', date_to),
                                                                                  ('state', '=', 'done')])
            calculated_hours1 = attendance_obj.filtered(
                lambda x: (
                                  x.att_date.day > 5 or x.att_date.day < 26) and x.att_date in overtime_request_obj.mapped(
                    'overtime_date'))
            calculated_hours2 = attendance_obj.filtered(lambda x: x.att_date.day > 25 or x.att_date.day < 6)
            total_hours = sum(calculated_hours1.mapped('overtime_hours')) + sum(
                calculated_hours2.mapped('overtime_hours'))
            return total_hours

    def _weekend_hours(self, date_from, date_to, fri_rate, sat_rate):
        for rec in self:
            attendance_obj = self.env['hr.attendance'].search(
                [('employee_id', '=', rec.id), ('att_date', '>=', date_from), ('att_date', '<=', date_to),
                 ('is_weekend', '=', True)])
            overtime_request_obj = self.env['hr.overtime.request'].sudo().search([('employee_id', '=', rec.id),
                                                                                  ('overtime_date', '>=', date_from),
                                                                                  ('overtime_date', '<=', date_to),
                                                                                  ('state', '=', 'done')])
            fri_hours1 = attendance_obj.filtered(lambda
                                                     x: x.att_date.weekday() == 4 and (
                    x.att_date.day > 5 or x.att_date.day < 26) and x.att_date in overtime_request_obj.mapped(
                'overtime_date')).mapped(
                'overtime_hours')
            fri_hours2 = attendance_obj.filtered(
                lambda x: x.att_date.weekday() == 4 and x.att_date.day > 25 or x.att_date.day < 6).mapped(
                'overtime_hours')
            sat_hours1 = attendance_obj.filtered(lambda
                                                     x: x.att_date.weekday() == 5 and (
                    x.att_date.day > 5 or x.att_date.day < 26) and x.att_date in overtime_request_obj.mapped(
                'overtime_date')).mapped(
                'overtime_hours')
            sat_hours2 = attendance_obj.filtered(
                lambda x: x.att_date.weekday() == 5 and x.att_date.day > 25 or x.att_date.day < 6).mapped(
                'overtime_hours')
            total_hours = (sum(fri_hours1) * fri_rate) + (sum(sat_hours1) * sat_rate) + (sum(fri_hours2) * fri_rate) + (
                    sum(sat_hours2) * sat_rate)
            return total_hours

    def _public_holiday_hours(self, date_from, date_to):
        for rec in self:
            attendance_obj = self.env['hr.attendance'].search(
                [('employee_id', '=', rec.id), ('att_date', '>=', date_from), ('att_date', '<=', date_to),
                 ('is_public_holiday', '=', 1)])
            overtime_request_obj = self.env['hr.overtime.request'].sudo().search([('employee_id', '=', rec.id),
                                                                                  ('overtime_date', '>=', date_from),
                                                                                  ('overtime_date', '<=', date_to),
                                                                                  ('state', '=', 'done')])
            calculated_hours1 = attendance_obj.filtered(
                lambda x: (
                                  x.att_date.day > 5 or x.att_date.day < 26) and x.att_date in overtime_request_obj.mapped(
                    'overtime_date'))
            calculated_hours2 = attendance_obj.filtered(lambda x: x.att_date.day > 25 or x.att_date.day < 6)
            total_hours = sum(calculated_hours1.mapped('overtime_hours')) + sum(
                calculated_hours2.mapped('overtime_hours'))
            return total_hours

    def _absence_days(self, date_from, date_to, payslip_id):
        for rec in self:
            attendance_obj = self.env['hr.attendance'].search(
                [('employee_id', '=', rec.id), ('att_date', '>=', date_from), ('att_date', '<=', date_to),
                 ('is_weekend', '=', 0), ('is_public_holiday', '=', 0)])
            payslip_obj = self.env['hr.payslip'].search([('id', '=', payslip_id)])
            actual_days = len(attendance_obj)
            planned_days = payslip_obj.worked_days_line_ids.filtered(lambda x: x.work_entry_type_id.id == 1)
            total_days = (planned_days.number_of_days + 1) - actual_days
            return total_days

    def _absence_penalties(self, date_from, date_to, payslip_id):
        for rec in self:
            contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.id),
                                                          ('state', 'in', ['open', 'close'])])
            policy_id = contract_id[-1].att_policy_id if contract_id else False
            absence_rule_id = policy_id.absence_rule_id if policy_id else False

            total = 0
            if absence_rule_id:
                count = self._absence_days(date_from, date_to, payslip_id)

                if count == 0:
                    total = 0
                elif count == 1:
                    total = absence_rule_id.first
                elif count == 2:
                    total = absence_rule_id.first + absence_rule_id.second
                elif count == 3:
                    total = absence_rule_id.first + absence_rule_id.second + absence_rule_id.third
                elif count == 4:
                    total = absence_rule_id.first + absence_rule_id.second + absence_rule_id.third + absence_rule_id.fourth
                elif count == 5:
                    total = absence_rule_id.first + absence_rule_id.second + absence_rule_id.third + absence_rule_id.fourth + absence_rule_id.fifth
                else:
                    total = absence_rule_id.first + absence_rule_id.second + absence_rule_id.third + absence_rule_id.fourth + absence_rule_id.fifth + (
                            absence_rule_id.fifth * (count - 5))
            return total
