from odoo import models, fields


class PenaltyConfiguration(models.Model):
    _name = 'penalty.configuration'
    _description = 'Penalty Configuration'

    name = fields.Char(string='Configuration Name', default='Default Penalty Configuration')
    duration = fields.Integer(string='Duration (days)', required=True, default=30)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    penalty_line_ids = fields.One2many('hr.employee.penalty', 'employee_id')

    def _calculate_penalties(self, date_from, date_to):
        date_from = fields.Date.from_string(date_from)
        date_to = fields.Date.from_string(date_to)

        # Filter penalties for the employee within the specific date range (month)
        penalties = self.penalty_line_ids.filtered(
            lambda r: date_from <= r.date <= date_to and r.state == 'approved'
        )

        # Group penalties by rule line and calculate penalties
        penalty_occurrences = []
        for penalty in penalties:
            penalty_occurrences.append(penalty)
        print('penalty_occurrences::', penalty_occurrences)
        total_penalties = len(penalty_occurrences)

        # Check the last penalty and apply the correct penalty value based on its count
        last_penalty = penalty_occurrences[-1] if penalty_occurrences else None

        print('last_penalty::', last_penalty)
        if last_penalty:
            rule_line = last_penalty.rule_line_id
            if total_penalties == 1:
                penalty_value = rule_line.first
            elif total_penalties == 2:
                penalty_value = rule_line.second
            elif total_penalties == 3:
                penalty_value = rule_line.third
            elif total_penalties == 4:
                penalty_value = rule_line.fourth
            else:
                penalty_value = rule_line.fifth + (rule_line.fifth * (total_penalties - 5))

            print(
                f"Employee did {total_penalties} penalties, the last penalty is {rule_line.name} with value {penalty_value}%")
        else:
            penalty_value = 0
            print("No penalties found for the given period.")

        return penalty_value
