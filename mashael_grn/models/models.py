from odoo import api, fields, models



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    git_id = fields.Many2one(
        comodel_name='msh.git',
        string='GIT',
        required=False)

    piv_ids = fields.Many2many(
        comodel_name='purchase.piv',
        string='Piv', compute='_compute_piv_ids')

    piv_id = fields.Many2one(
        comodel_name='purchase.piv',
        string='Piv',
        required=False, domain="[('id', 'in', piv_ids)]")

    # picking_type_id must named to be "to wh"
    piv_partner_id = fields.Many2one('res.partner', string='Supplier', related='piv_id.partner_id')
    supplier_invoice_number = fields.Char(
        string='Supplier Invoice Number',
        required=False, related='piv_id.supplier_invoice_number')

    supplier_invoice_date = fields.Date(
        string='Supplier Invoice Date',
        required=False, related='piv_id.supplier_invoice_date')
    
    shortage_total_value = fields.Char(
        string='Shortage Total Value',
        required=False, compute='_compute_shortage_total_value')

    @api.depends('move_ids_without_package', 'move_ids_without_package.price_total')
    def _compute_shortage_total_value(self):
        for rec in self:
            total = 0
            for line in rec.move_ids_without_package:
                total += line.price_total
            rec.shortage_total_value = total


    # recipt_date frome module force date




    @api.depends('git_id')
    def _compute_piv_ids(self):
        for rec in self:
            pivs = []
            for line in rec.git_id.piv_line_ids:
                pivs.append(line.piv_id.id)
            print('pivs', pivs)
            rec.piv_ids = pivs
            print('rec.piv_ids >>', rec.piv_ids)



    @api.onchange('piv_id')
    def onchange_piv(self):
        receipt_lines = []
        self.move_ids_without_package = [(5, 0)]
        for piv_line in self.piv_id.purchase_piv_line_ids:
                    receipt_lines.append(
                        {
                            "product_id": piv_line.product_id.id,
                            "name": piv_line.product_id.name,
                            "purchase_order_id": piv_line.purchase_order_id.id,
                            "piv_qty": piv_line.qty_invoiced,
                            "piv_batch_no": piv_line.batch_no,
                            "price_total": piv_line.price_total,
                            "serial_no_id": piv_line.serial_no_id,
                            "serial_mts": piv_line.serial_mts,
                            "serial_calibration_cert": piv_line.serial_calibration_cert,
                        }
                    )
        for line in receipt_lines:
            self.move_ids_without_package = [(0, 0, line)]


class StockMove(models.Model):
    _inherit = 'stock.move'


    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=False,
        check_company=True,
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        auto_join=True, index=True, required=False,
        check_company=True,
        help="Location where the system will stock the finished products.")

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Po No.',
        required=False)

    code = fields.Char(
        string='Vendor Purchase Code',
        required=False, related='product_id.code')

    piv_qty = fields.Float(string="Piv/Git Qty", digits='Product Unit of Measure', store=True)
    product_uom_qty = fields.Float(
        'GRN Qty',
        digits='Product Unit of Measure',
        default=0, required=True,
        help="This is the quantity of product that is planned to be moved."
             "Lowering this quantity does not generate a backorder."
             "Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    
    shortage = fields.Float(
        string='Shortage Qty',
        required=False, compute='_compute_qty_shortage')

    shortage_value = fields.Float(
        string='Shortage Value',
        required=False, compute='_compute_shortage_value')

    serial_no = fields.Char(
        string='Serial NO',
        required=False)

    serial_no_id = fields.Many2one(
        comodel_name='piv.serial',
        string='Serial No',
        required=False)

    grn_serial_no_ids = fields.Many2one(
        comodel_name='piv.serial',
        string='Serial No',
        required=False, domain="[('id', 'in', serial_no_ids)]")


    serial_mts = fields.Binary('Serial MTC')
    serial_calibration_cert = fields.Binary('Serial Calibration Cert')
    piv_batch_no = fields.Char(
        string='Piv Patch NO.',
        required=False)

    price_total = fields.Float(
        string='Price_total',
        required=False)


    @api.depends('piv_qty', 'product_uom_qty')
    def _compute_qty_shortage(self):
        for rec in self:
            total = 0
            total = rec.piv_qty - rec.product_uom_qty
            rec.shortage = total

    @api.depends('piv_qty', 'product_uom_qty', 'price_total')
    def _compute_shortage_value(self):
        for rec in self:
            total = 0
            total = (rec.piv_qty - rec.product_uom_qty) * rec.price_total
            rec.shortage_value = total











