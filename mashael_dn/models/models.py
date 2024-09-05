from odoo import api, fields, models , _
from odoo.http import request
from odoo.exceptions import UserError


class DebitNote(models.Model):
    _name = 'debit.note'
    _description = 'Debit Note'

    name = fields.Char()
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('confirm', 'Confirm')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)


    grn_id = fields.Many2one(
        comodel_name='stock.picking',
        string='GRN',
        required=False)

    @api.onchange('grn_id')
    def onchange_method(self):
        dn_lines = []
        self.debit_note_line_ids = [(5, 0)]
        print('grn_id >>', self.grn_id)
        for line in self.grn_id.move_ids_without_package:
            if line.shortage > 0:
                dn_lines.append(
                    {
                        "purchase_order_id": line.purchase_order_id.id,
                        "code": line.code,
                        "name": line.name,
                        "git_qty": line.piv_qty,
                        "grn_qty": line.product_uom_qty,
                        "shortage": line.shortage,
                        "shortage_value": line.shortage_value,
                        "product_id": line.product_id.id,

                    }
                )
        for line in dn_lines:
            self.debit_note_line_ids = [(0, 0, line)]


    git_id = fields.Many2one(
        comodel_name='msh.git',
        string='GIT NO',
        required=False, related='grn_id.git_id')

    piv_id = fields.Many2one(
        comodel_name='purchase.piv',
        string='Piv',
        required=False, related='grn_id.piv_id')

    piv_partner_id = fields.Many2one('res.partner', string='Supplier', related='grn_id.piv_partner_id')
    supplier_invoice_number = fields.Char(
        string='Supplier Invoice Number',
        required=False, related='grn_id.supplier_invoice_number')

    supplier_invoice_date = fields.Date(
        string='Supplier Invoice Date',
        required=False, related='grn_id.supplier_invoice_date')

    shortage_total_value = fields.Char(
        string='Vendor CN NO.',
        required=False, related='grn_id.shortage_total_value')
    
    vendor_cn_date = fields.Date(
        string='Vendor CN Date',
        required=False)

    cn_attach_doc = fields.Binary('CN Attach Doc')

    debit_note_line_ids = fields.One2many(
        comodel_name='debit.note.line',
        inverse_name='debit_note_line_id',
        string=' debit_note_line_ids',
        required=False)

    refund_id = fields.Many2one(
        comodel_name='account.move',
        string='refund_id',
        required=False)

    def button_confirm(self):
        self.write({'state': 'confirm'})
        invoice = self.env['account.move'].create({
            'move_type': 'in_refund',
            'partner_id': self.piv_partner_id.id,
            # 'partner_id': self.partner_id.id,
            'invoice_date': fields.date.today(),
        })
        print('invoice>>', invoice)
        self.refund_id = invoice.id
        refund_lines = []
        for line in self.debit_note_line_ids:
                refund_lines.append(
                    {
                        "product_id": line.product_id.id,
                        "quantity": line.shortage,

                    }
                )
        for line in refund_lines:
            invoice.invoice_line_ids = [(0, 0, line)]
        invoice.action_post()
        self.send_email(self.dn_page())
        self.create_piv()

    def dn_page(self):
        menu_id = self.env.ref('mashael_dn.mashael_dn_menu')
        action_id = self.env.ref('mashael_dn.mashael_dn_action')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        base_url += '&menu_id=%d&action=%d' % (menu_id.id, action_id.id)
        return base_url

    def send_email(self, dn_page):
        message = """ Refund Created For DN: """ + self.name + '<br>' + """
        <br> You can access Debit Note details from here: <br>""" + """<a href="%s">Link</a> """ % (dn_page)

        try:
            Mail = self.env['mail.mail']
            outgoing_mail = self.env['ir.mail_server'].search([], limit=1)
            if not outgoing_mail or not outgoing_mail.smtp_port or not outgoing_mail.smtp_user or not outgoing_mail.smtp_pass:
                raise UserError(
                    _('Outgoing email should be configured well,please contact us!'))

            # mail values
            mail_values = {
                'subject': 'Debit Note - ' + self.name,
                'author_id': 1,
                'email_from': 'Mshael' + ' <' + outgoing_mail.smtp_user + '>',
                'email_to': self.piv_partner_id.email,
                'body_html': message,
            }

            # create mail, that will create it in odoo mails
            created_mail = Mail.create(mail_values)

            # send mail
            created_mail.send()

            return "sent"
        except Exception as e:
            return str(e)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('debit.note') or _('New')
        result = super(DebitNote, self).create(vals)
        return result

    
class DebitNoteLine(models.Model):
    _name = 'debit.note.line'

    debit_note_line_id = fields.Many2one(
        comodel_name='debit.note',
        string=' debit_note_line_id',
        required=False)

    product_id = fields.Many2one('product.product', string='Product')

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Po No.',
        required=False)

    code = fields.Char(
        string='Vendor Purchase Code',
        required=False, related='product_id.code')

    name = fields.Char(
        string='Description',
        required=False)

    git_qty = fields.Float(string='Git Qty', required=False)
    grn_qty = fields.Float(string='Grn Qty', required=False)
    shortage = fields.Float(string='Shortage Qty', required=False)
    shortage_value = fields.Float(string='Shortage value', required=False)


