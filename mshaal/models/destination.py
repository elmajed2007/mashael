from odoo import models, fields, api


class Destination(models.Model):
    _name = 'destination'

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, change_default=True, tracking=True,help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    goods_dipatch_add= fields.Text('Goods Dipatch Address')
    city= fields.Text('City')
    name = fields.Many2one('freight.mode',string='Freight Mode')
    country_id = fields.Many2one('res.country',string='Country')
    duration=fields.Integer('Duration')
    category_id = fields.Many2one('uom.category', 'Category')
    uom_id = fields.Many2one('uom.uom', "UoM", required=True, domain="[('category_id', '=', category_id)]")
    sec_category_id = fields.Many2one('uom.category', 'Category')
    sec_uom_id = fields.Many2one('uom.uom', "UoM", required=True, domain="[('category_id', '=', sec_category_id)]")
    cost_per_volume=fields.Float('Cost Per Volume (m³)')
    cost_per_weight=fields.Float('Cost Per Weight (km³)',help='Distance in kilometers')

    related_contact_id = fields.Many2one('res.partner', string='Related Contact'
                                      , domain="[('id', '=', related_con_ids)]")
    related_con_ids = fields.Many2many('res.partner', string='Related Contact')
    @api.onchange('partner_id')
    def compute_contact(self):
        for rec in self:
            contact = []
            if rec.partner_id.type:
                for record in rec.partner_id.child_ids:
                    contact.append( record.id)
                    rec.related_con_ids = contact
