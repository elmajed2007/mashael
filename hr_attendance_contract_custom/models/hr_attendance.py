# -*- coding: utf-8 -*-

import pytz
from odoo import models, fields
from datetime import datetime, timedelta, time


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    _description = 'Hr Attendance Custom'

    att_date = fields.Date("Attendance Date")
    overtime_hours = fields.Float("Over Time")
    late_in = fields.Float("Late In")
    act_late_in = fields.Float("Actual Late")
    diff_time = fields.Float("Diff Time")
    act_diff_time = fields.Float("Actual Diff")
    is_weekend = fields.Integer("Weekend")
    is_public_holiday = fields.Integer("Public Holiday")
    is_tamper = fields.Integer("Tamper")

    def get_attendances(self):
        # Get a list of unique employee IDs from the 'self' records
        employee_ids = self.env['hr.employee'].search([('id', 'in', self.mapped('employee_id.id'))])
        for employee_id in employee_ids:
            # Get employee's resource calendar, contract, and attendance policy
            calendar_id = employee_id.resource_calendar_id
            calendar_attendance_ids = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', calendar_id.id)])
            contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id),
                                                          ('state', '=', 'open')], limit=1)
            policy_id = contract_id.att_policy_id if contract_id else False

            # Get employee's time zone for accurate time calculations
            tz = pytz.timezone(employee_id.tz)

            # Filter the 'self' records to those belonging to the current employee
            employee_records = self.filtered(lambda x: x.employee_id.id == employee_id.id).sorted(
                key=lambda x: x.check_in)

            late_cnt = []
            diff_cnt = []
            for rec in employee_records:

                if not rec.check_in or not rec.check_out:
                    continue

                # Convert check-in/out times to the employee's time zone for accurate comparison
                actual_check_in_tz = pytz.utc.localize(rec.check_in).astimezone(tz)
                actual_check_out_tz = pytz.utc.localize(rec.check_out).astimezone(tz)
                actual_check_in = actual_check_in_tz.time()
                actual_check_out = actual_check_out_tz.time()

                # Calculate Attendance Date
                if calendar_id.is_2days and actual_check_out.hour < 12:
                    att_date = actual_check_out_tz.date() - timedelta(days=1)
                else:
                    att_date = actual_check_in_tz.date()

                # Extract the weekday (0-6) from the check-out time
                day_num = att_date.weekday()

                start_month = att_date.replace(day=1)
                next_month = att_date.replace(day=28) + timedelta(days=4)
                end_month = next_month - timedelta(days=next_month.day)

                check_in_list = []
                check_out_list = []
                # Find matching attendance records from the calendar for the current day
                for calendar_attendance_id in calendar_attendance_ids:
                    if calendar_attendance_id.day_period == 'lunch':
                        continue

                    if att_date == self._compute_last_saturday_date(start_month, end_month):
                        if calendar_attendance_id.dayofweek == str(day_num + 1):
                            check_in_list.append(calendar_attendance_id.hour_from)
                            check_out_list.append(calendar_attendance_id.hour_to)
                    elif calendar_attendance_id.date_from and calendar_attendance_id.date_to:
                        if (calendar_attendance_id.dayofweek == str(day_num)
                                and att_date >= calendar_attendance_id.date_from and att_date <= calendar_attendance_id.date_to):
                            check_in_list.append(calendar_attendance_id.hour_from)
                            check_out_list.append(calendar_attendance_id.hour_to)
                        else:
                            continue
                    elif calendar_attendance_id.date_from:
                        if calendar_attendance_id.dayofweek == str(
                                day_num) and att_date >= calendar_attendance_id.date_from:
                            check_in_list.append(calendar_attendance_id.hour_from)
                            check_out_list.append(calendar_attendance_id.hour_to)
                        else:
                            continue
                    else:
                        if calendar_attendance_id.dayofweek == str(day_num):
                            check_in_list.append(calendar_attendance_id.hour_from)
                            check_out_list.append(calendar_attendance_id.hour_to)
                        else:
                            continue

                # Determine planned check-in/out times based on calendar attendance
                if len(check_in_list) > 1:
                    if not calendar_id.is_2days:
                        planned_check_in = self._float_to_time(min(check_in_list))
                        planned_check_out = self._float_to_time(max(check_out_list))
                    else:
                        planned_check_in = self._float_to_time(max(check_in_list))
                        planned_check_out = self._float_to_time(min(check_out_list))
                else:
                    planned_check_in = self._float_to_time(check_in_list[0]) if check_in_list else None
                    planned_check_out = self._float_to_time(check_out_list[0]) if check_out_list else None

                leave_obj = rec.env['hr.leave'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                               ('request_date_from', '=', att_date),
                                                               ('request_date_to', '=', att_date),
                                                               ('state', '=', 'validate')], limit=1)
                leave_hours_late = 0
                leave_hours_diff = 0
                if leave_obj and planned_check_in and int(leave_obj.request_hour_from) == check_in_list[0]:
                    leave_hours_late = int(leave_obj.request_hour_to) - int(leave_obj.request_hour_from)
                elif leave_obj and planned_check_out and int(leave_obj.request_hour_from) >= (check_out_list[0] - 2):
                    leave_hours_diff = int(leave_obj.request_hour_to) - int(leave_obj.request_hour_from)

                # Calculate late arrival (considering midnight edge case)
                if planned_check_in is not None and actual_check_in > planned_check_in:
                    if actual_check_in_tz.date() == att_date:
                        late_in = (datetime.strptime(str(actual_check_in), "%H:%M:%S") -
                                   datetime.strptime(str(planned_check_in), "%H:%M:%S")).seconds / 3600
                    else:
                        late_in = 0
                else:
                    late_in = 0

                # Calculate early departure (if applicable)
                if planned_check_out is not None and planned_check_out > actual_check_out:
                    if actual_check_out_tz.date() == att_date or calendar_id.is_2days:
                        diff_time = (datetime.strptime(str(planned_check_out), "%H:%M:%S") -
                                     datetime.strptime(str(actual_check_out), "%H:%M:%S")).seconds / 3600
                    else:
                        diff_time = 0
                else:
                    diff_time = 0

                # Calculate Overtime Hours
                if planned_check_out is not None:
                    if planned_check_out < actual_check_out and (
                            actual_check_out_tz.date() == att_date or calendar_id.is_2days):
                        over_time = (datetime.strptime(str(actual_check_out), "%H:%M:%S") -
                                     datetime.strptime(str(planned_check_out), "%H:%M:%S")).seconds / 3600
                    elif actual_check_out_tz.date() != att_date:
                        over_time = (actual_check_out.hour + 24 + (actual_check_out.minute / 60)) - (
                                planned_check_out.hour + (planned_check_out.minute / 60))
                    else:
                        over_time = 0
                else:
                    over_time = 0

                # Identify weekend based on missing planned times with actual check-in/out
                if planned_check_in is None:
                    is_weekend = 1
                    over_time = rec.worked_hours
                else:
                    is_weekend = 0

                # Identify public holiday
                public_holidays = rec.env['resource.calendar.leaves'].search(
                    [('company_id', '=', rec.employee_id.company_id.id), ('holiday_id', '=', None),
                     '|', ('calendar_id', '=', calendar_id.id), ('calendar_id', '=', None)])
                is_public_holiday = 0
                for ph in public_holidays:
                    if not is_weekend:
                        if att_date >= ph.date_from.date() and att_date <= ph.date_to.date():
                            is_public_holiday = 1
                            over_time = rec.worked_hours
                            late_in = 0
                            diff_time = 0
                            break

                # Identify check-in/out tamper
                if (actual_check_in.hour == actual_check_out.hour
                        or actual_check_out.hour - actual_check_in.hour == 1
                        or (actual_check_in.hour == 23 and actual_check_out.hour == 0)):
                    is_tamper = 1
                    if planned_check_in and planned_check_out:
                        closest_hour = self._closest_hour(actual_check_in.hour, planned_check_in.hour,
                                                          planned_check_out.hour)
                        if closest_hour == planned_check_out.hour:
                            late_in = 0
                        else:
                            diff_time = 0
                else:
                    is_tamper = 0

                # Delegate calculations to attendance policy for potential grace periods, etc.
                late_in -= leave_hours_late
                diff_time -= leave_hours_diff
                if late_in < 0:
                    late_in = 0
                if diff_time < 0:
                    diff_time = 0

                if policy_id:
                    float_late, late_cnt = policy_id.get_late(late_in, late_cnt)
                    float_diff, diff_cnt = policy_id.get_diff(diff_time, diff_cnt)
                else:
                    float_late = 0
                    float_diff = 0
                # Update attendance record with calculated values
                values = {
                    'att_date': att_date,
                    'overtime_hours': over_time,
                    'act_late_in': late_in,
                    'act_diff_time': diff_time,
                    'late_in': float_late,
                    'diff_time': float_diff,
                    'is_weekend': is_weekend,
                    'is_public_holiday': is_public_holiday,
                    'is_tamper': is_tamper,
                }
                rec.write(values)

    def _float_to_time(self, hours_float):
        midnight = datetime.combine(datetime.today(), time.min)
        time_delta = timedelta(hours=hours_float)
        time_obj = (midnight + time_delta).time()
        return time_obj

    def _closest_hour(self, hour, num1, num2):
        # Calculate the absolute difference between each number and hour
        diff1 = abs(num1 - hour)
        diff2 = abs(num2 - hour)
        # Check which difference is smaller and return the corresponding number
        if diff1 < diff2:
            return num1
        else:
            return num2

    def _compute_last_saturday_date(self, start_date, end_date):
        if start_date and end_date:
            # Finding the last Saturday date within the date range
            current_date = end_date
            while current_date.weekday() != 5:  # Saturday is represented by 5 in Python's datetime module
                current_date -= timedelta(days=1)
            last_saturday_date = current_date
        else:
            last_saturday_date = False

        return last_saturday_date

    # def _get_all_dates(self, start_date, end_date):
    #     all_dates = []
    #     for n in range((end_date - start_date).days + 1):
    #         date_to_add = start_date + timedelta(days=n)
    #         all_dates.append(date_to_add)
    #     return all_dates
