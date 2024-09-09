from odoo import api, fields, models


class stockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'


    git_landed_id = fields.Many2one(
        comodel_name='git.landed.cost',
        string='Git Landed Cost',
        required=False)

    @api.onchange('git_landed_id')
    def onchange_method(self):
        line_value = []
        glc_product = self.env['product.product'].search([('is_glc_product', '=', True)], limit=1)
        self.cost_lines = [(5, 0)]
        total = 0
        for piv_line in self.piv_id.piv_custom_ids:
            total += piv_line.total
        line_value.append(
            {
                "product_id": glc_product.id,
                # "": total,
            }
        )
        for line in line_value:
            self.cost_linesc = [(0, 0, line)]
