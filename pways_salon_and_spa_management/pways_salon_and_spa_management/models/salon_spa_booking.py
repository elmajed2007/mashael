# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, time, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SalonBooking(models.Model):
    _name = 'salon.booking'
    _description = 'Salon Booking'
    _rec_name = 'name'
    _inherit = ['mail.thread']
    _order = "id DESC"

    seq = fields.Char(default='New',readonly=True, string="Uniqe Numebr", copy=False)
    name = fields.Many2one('res.partner', required=True) #(MG)
    state = fields.Selection(string="State", default="draft", selection=[('draft', 'Draft'), ('conform','Booking Conform'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    time = fields.Datetime(string="Date", required=True)
    phone = fields.Char(string="Phone", required=True)
    email = fields.Char(string="E-Mail", required="1")
    chair_id = fields.Many2one('salon.chair', string="Chair")
    booking_for = fields.Selection([('for_salon','Salon'),('for_spa','Spa')], string="Booking For", default="for_salon")
    salon_booking_line_ids = fields.One2many("salon.booking.lines", "salon_booking_id", string="Salon Booking lines")

    language_id = fields.Many2one('res.lang', 'Language',default=lambda self: self.env['res.lang'].browse(1))
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user,readonly=1)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    # @api.model
    # def create(self, vals):
    #     if vals.get('seq', 'New') == 'New':
    #         vals['seq'] = self.env['ir.sequence'].next_by_code('salon.booking') or '/'
    #     return super(SalonBooking, self).create(vals)

    def action_conform(self):
        self.state = 'conform'
        template_id = self.env['ir.model.data']._xmlid_lookup('pways_salon_and_spa_management.mail_template_salon_conformed')[2]
        email_template_id = self.env['mail.template'].sudo().browse(template_id)
        email_template_id.send_mail(self.id)
        msg_body = _('mail is send to manager for approval.')
        self.message_post(body=msg_body)

    def action_draft(self):
        self.state = 'draft'

    def create_employee_in_employee_work(self):
        employees = self.env['res.users'].search([])
        for emp in employees:
            employees_work = self.env['employee.work'].search([('employee_id', '=', emp.id)], limit=1)
            if not employees_work:
                vals = {"employee_id" : emp.id}
                new_employee = employees_work.create(vals) 

    def action_approve_booking(self):
        if self.chair_id:
            if self.booking_for == 'for_salon':
                order_data = {
                    'customer_name': self.name,
                    'phone' : self.phone,
                    'chair_id': self.chair_id.id,
                    'start_time': self.time,
                    'date': fields.Datetime.now(),
                    'stage_id': 1,
                    'booking_identifier': True,
                    'booking_for': self.booking_for,
                    'is_salon_product' : True,
                }
            if self.booking_for == 'for_spa':
                order_data = {
                    'customer_name': self.name,
                    'phone' : self.phone,
                    'chair_id': self.chair_id.id,
                    'start_time': self.time,
                    'date': fields.Datetime.now(),
                    'stage_id': 1,
                    'booking_identifier': True,
                    'booking_for': self.booking_for,
                    'is_spa_product' : True,
                }
            order = self.env['salon.order'].create(order_data)
            partner_data = {
                            "name" : self.name,
                            "phone" : self.phone,
                            "email" : self.email, 
                            }
            check_if_exist = self.env['res.partner'].search([('phone','=', self.phone)])
            if not check_if_exist:
                partner = self.env['res.partner'].create(partner_data)

            template = self.env.ref('pways_salon_and_spa_management.mail_template_salon_approved')
            self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
            self.state = "approved"

            self.create_employee_in_employee_work()
        else:
            raise ValidationError("Please Select The Chair for customer.")

    def action_reject_booking(self):
        template = self.env.ref('pways_salon_and_spa_management.mail_template_salon_rejected')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        self.state = "rejected"

    def button_view_booking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("pways_salon_and_spa_management.salon_order_action")
        action['domain'] = [('phone', '=', self.phone)]
        return action

class SalonBookingLines(models.Model):
    _name = 'salon.booking.lines'
    _description = 'Salon Booking Lines'

    salon_booking_id = fields.Many2one("salon.booking", string="Salon Booking")
    product_id = fields.Many2one("product.product", string="Product", domain="[('is_salon_product', '=', True)]")
    price = fields.Float(related="product_id.list_price")
    time_taken = fields.Float(string ="Time")