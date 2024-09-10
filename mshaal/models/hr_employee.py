
from werkzeug.urls import url_encode
from dateutil.relativedelta import relativedelta
from markupsafe import Markup

from odoo import api, fields, models, _


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    code = fields.Char('Code')


class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char('Code')


class HRWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    code = fields.Char('Code')



class HREmployee(models.Model):
    _inherit = 'hr.employee'

    first_name = fields.Char()
    second_name = fields.Char()
    third_name = fields.Char()
    name = fields.Char(
        string="Employee Name",
        related='resource_id.name',
        store=True,
        readonly=False,
        tracking=True,
        compute='_compute_name',
        inverse='_inverse_name'
    )

    full_name = fields.Char('Full Name')
    arabic_name = fields.Char('Arabic Name')

    @api.depends('first_name', 'second_name', 'third_name')
    def _compute_name(self):
        for rec in self:
            # Ensure the name is only generated if all fields are present
            if rec.first_name or rec.second_name or rec.third_name:
                rec.name = ' '.join(filter(None, [rec.first_name, rec.second_name, rec.third_name]))
            else:
                rec.name = False  # Set to empty if no names are provided

    @api.onchange('first_name', 'second_name', 'third_name')
    def _onchange_name(self):
        self._compute_name()


