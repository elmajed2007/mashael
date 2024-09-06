from odoo import models, fields, api


class HrEmployeePenalties(models.Model):
    _inherit = 'hr.employee'

    def _calculate_penalties(self, date_from, date_to):
        date_from = fields.Date.from_string(date_from)
        date_to = fields.Date.from_string(date_to)

        # Filter penalties for the employee within the specific date range (month)
        penalties = self.penalty_line_ids.filtered(
            lambda r: date_from <= r.date <= date_to and r.state == 'approved'
        )

        penalty_occurrences = []
        for penalty in penalties:
            penalty_occurrences.append(penalty)
        print('penalty_occurrences::', penalty_occurrences)
        total_penalties = len(penalty_occurrences)

        total_penalty_value = 0
        if penalty_occurrences:
            for idx, penalty in enumerate(penalty_occurrences):
                rule_line = penalty.rule_line_id
                occurrence_count = idx + 1  # Penalty  count (based on index)

                # Calculate penalty value based on occurrence count
                if occurrence_count == 1:
                    penalty_value = rule_line.first
                elif occurrence_count == 2:
                    penalty_value = rule_line.second
                elif occurrence_count == 3:
                    penalty_value = rule_line.third
                elif occurrence_count == 4:
                    penalty_value = rule_line.fourth
                else:
                    penalty_value = rule_line.fifth + (rule_line.fifth * (occurrence_count - 5))

                total_penalty_value += penalty_value

                print(
                    f"Penalty {occurrence_count}: {rule_line.name} with value {penalty_value}%"
                )

            print(f"Total penalties value for the period: {total_penalty_value}%")
        else:
            print("No penalties found for the given period.")

        return total_penalty_value / 100
