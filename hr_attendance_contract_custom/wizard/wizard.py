# -*- coding: utf-8 -*-

from odoo import fields, models
from datetime import datetime, timedelta
import pytz


class AttendanceReportWizard(models.TransientModel):
    _name = "attendance.report.wizard"
    _description = "Attendance Report Wizard"

    start_date = fields.Date(string="Start Date", default=fields.Date.today().replace(day=1), required=True)
    end_date = fields.Date(string="End Date",
                           default=fields.Date.today().replace(day=28) + timedelta(days=4) - timedelta(
                               days=(fields.Date.today().replace(day=28) + timedelta(days=4)).day),
                           required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees', required=True)

    def _generate_dates(self, start_date, end_date):
        all_dates = []
        for n in range((end_date - start_date).days + 1):
            date_to_add = start_date + timedelta(days=n)
            all_dates.append(date_to_add)
        return all_dates

    def _get_data(self):

        emp_list = []
        data = []
        for emp in self.employee_ids:
            tz = pytz.timezone(emp.tz)
            all_dates = self._generate_dates(self.start_date, self.end_date)
            calendar_id = emp.resource_calendar_id
            calendar_attendance_ids = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', calendar_id.id)])
            att_obj = self.env['hr.attendance'].sudo().search(
                [('employee_id', '=', emp.id), ('att_date', '>=', self.start_date), ('att_date', '<=', self.end_date)])
            leave_obj = self.env['hr.leave'].sudo().search([('employee_id', '=', emp.id), ('state', '=', 'validate')])
            ph_obj = self.env['resource.calendar.leaves'].sudo().search(
                [('company_id', '=', emp.company_id.id), ('holiday_id', '=', None),
                 '|', ('calendar_id', '=', calendar_id.id), ('calendar_id', '=', None)])

            list = []
            for d in all_dates:
                day_num = d.weekday()
                d_date = d
                d_name = d.strftime("%A")

                if self.env.user.lang == 'ar_001':
                    if d_name == 'Saturday':
                        d_name_ar = 'السبت'
                    elif d_name == 'Sunday':
                        d_name_ar = 'الاحد'
                    elif d_name == 'Monday':
                        d_name_ar = 'الاثنين'
                    elif d_name == 'Tuesday':
                        d_name_ar = 'الثلاثاء'
                    elif d_name == 'Wednesday':
                        d_name_ar = 'الاربعاء'
                    elif d_name == 'Thursday':
                        d_name_ar = 'الخميس'
                    else:
                        d_name_ar = 'الجمعة'
                    d_name = d_name_ar

                start_month = d_date.replace(day=1)
                next_month = d_date.replace(day=28) + timedelta(days=4)
                end_month = next_month - timedelta(days=next_month.day)

                check_in_list = []
                check_out_list = []
                for ca_id in calendar_attendance_ids:
                    if ca_id.day_period == 'lunch':
                        continue
                    elif ca_id.dayofweek == str(day_num):
                        check_in_list.append(ca_id.hour_from)
                        check_out_list.append(ca_id.hour_to)
                    elif d == att_obj._compute_last_saturday_date(start_month, end_month):
                        if ca_id.dayofweek == str(day_num + 1):
                            check_in_list.append(ca_id.hour_from)
                            check_out_list.append(ca_id.hour_to)
                    else:
                        continue

                if len(check_in_list) > 1:
                    planned_check_in = att_obj._float_to_time(max(check_in_list))
                    planned_check_out = att_obj._float_to_time(min(check_out_list))
                else:
                    planned_check_in = att_obj._float_to_time(check_in_list[0]) if check_in_list else None
                    planned_check_out = att_obj._float_to_time(check_out_list[0]) if check_out_list else None

                att_record = att_obj.filtered(lambda x: x.att_date == d_date)

                if att_record:
                    actual_check_in_tz = pytz.utc.localize(att_record.check_in).astimezone(tz)
                    actual_check_out_tz = pytz.utc.localize(att_record.check_out).astimezone(tz)
                    actual_check_in = actual_check_in_tz.time()
                    actual_check_out = actual_check_out_tz.time()
                else:
                    actual_check_in = None
                    actual_check_out = None

                work_hours = att_record.worked_hours
                overtime_hours = att_record.overtime_hours
                act_late = att_record.act_late_in
                act_diff = att_record.act_diff_time
                pen_late = att_record.late_in
                pen_diff = att_record.diff_time

                ph_record = ph_obj.filtered(lambda x: x.date_from.date() <= d_date <= x.date_to.date())
                lv_record = leave_obj.filtered(lambda x: x.request_date_from <= d_date <= x.request_date_to)

                if (not planned_check_in or ph_record) and actual_check_in:
                    if not self.env.user.lang == 'ar_001':
                        note = 'Over Time'
                    else:
                        note = 'وقت اضافي'
                elif planned_check_in and actual_check_in:
                    note = ''
                elif not planned_check_in and not actual_check_in:
                    note = ''
                elif ph_record:
                    note = ph_record[0].name
                elif lv_record:
                    note = lv_record[0].holiday_status_id.name
                else:
                    if not self.env.user.lang == 'ar_001':
                        note = 'Absence'
                    else:
                        note = 'غياب'

                line = {
                    'd_name': d_name,
                    'd_date': d_date,
                    'planned_check_in': planned_check_in,
                    'actual_check_in': actual_check_in,
                    'planned_check_out': planned_check_out,
                    'actual_check_out': actual_check_out,
                    'work_hours': round(work_hours, 2),
                    'overtime_hours': round(overtime_hours, 2),
                    'act_late': round(act_late, 2),
                    'act_diff': round(act_diff, 2),
                    'pen_late': round(pen_late, 2),
                    'pen_diff': round(pen_diff, 2),
                    'note': note,
                }
                list.append(line)
            emp_list.append([emp.device_id, emp.name] + [list])

        data.append(emp_list)
        return data

    # def button_export_pdf(self):
    #     data = {
    #         'records': self._get_data(),
    #     }
    #
    #     return self.env.ref('hr_attendance_contract_custom.action_report_attendance_pdf').report_action(self, data=data)

    def button_export_xlsx(self):
        data = {
            'records': self._get_data(),
        }

        return self.env.ref('hr_attendance_contract_custom.action_report_attendance_excel').report_action(self,
                                                                                                          data=data)
