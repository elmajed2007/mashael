from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class ResPartner(models.Model):
    _inherit = 'res.partner'

    destination_line_ids = fields.One2many(
        comodel_name='res.partner.destination',
        inverse_name='destination_line_id',
        string='Destination_line_ids',
        required=False)


    @api.constrains('destination_line_ids.is_default')
    def check_phone(self):
        count = 0
        for line in self.destination_line_ids:
            if line.is_default == True:
                count+= 1
        if count > 1:
            raise ValidationError(_('You Must Select One Destination'))




class ResPartnerDestination(models.Model):
    _name = 'res.partner.destination'



    destination_line_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner_id',
        required=False)


    destination_id = fields.Many2one(comodel_name='destination', string='Shipping Mode')

    is_default = fields.Boolean(
        string='Is Default',
        required=False)