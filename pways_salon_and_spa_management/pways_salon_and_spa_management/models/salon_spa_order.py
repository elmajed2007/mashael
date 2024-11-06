# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class SalonOrder(models.Model):
    _name = 'salon.order'
    _description = 'Salon Order'
    _inherit = ['mail.thread']
    _order = "id DESC"

    name = fields.Char(string='Salon', required=True, copy=False, readonly=True, default='Draft Order')
    phone = fields.Char(string="Phone")
    start_time = fields.Datetime(string="Start time", default=fields.Datetime.now, required=True)
    end_time = fields.Datetime(string="End time")
    date = fields.Datetime(string="Date", required=True, default=fields.Datetime.now)
    color = fields.Integer(string="Color", default=6)
    partner_id = fields.Many2one(
        'res.partner', string="Customer", required=False,
        help="If the customer is a regular customer, then you can add the"
             " customer in your database")
    # partner_id = fields.Many2one('res.partner', string="Customer", readonly=True, help="""If the customer is a regular customer, then you can add the customer in your database""")
    # partner_id = fields.Many2one('res.partner', string="Customer", help="""If the customer is a regular customer, then you can add the customer in your database""")
    # customer_name = fields.Char(string="Name", required=True)
    # customer_name = fields.Char(string="Name", required=True, compute='_compute_customer_name', store=True)
    #
    # @api.onchange('partner_id')
    # def _compute_customer_name(self):
    #     if self.partner_id:
    #         self.customer_name = self.partner_id.name

    customer_name = fields.Char(string="Name", required=True,
                                help="Name of salon customer")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    chair_id = fields.Many2one('salon.chair', string="Chair", required=True)
    price_subtotal = fields.Monetary(string='Total', readonly=True, store=True, compute='_compute_price_subtotal')
    time_taken_total = fields.Float(string='Total time',
                                    help='Total time taken')
    note = fields.Text('Terms and conditions')
    # order_line_ids = fields.One2many('salon.order.line', 'salon_order_id', string="Order Lines")
    order_line_ids = fields.One2many(comodel_name='salon.order.line',
                                     inverse_name='salon_order_id',
                                     string="Order Lines", copy=True,
                                     help='Salon order line for add '
                                          'list of services', required=True)
    # stage_id = fields.Many2one('salon.stage', string="Stages", default=1, group_expand='_read_group_stage_ids')
    stage_id = fields.Many2one(comodel_name='salon.stage', string="Stages",
                               group_expand='_read_group_stage_ids', default=1,
                               copy=False, help="state for the salon order(user"
                                                " can add dynamic state from"
                                                " the kanban view)")
    # inv_stage_identifier = fields.Boolean(string="Stage Identifier")
    inv_stage_identifier = fields.Boolean(string="Stage Identifier",
                                          help="Field to detect stage")
    # validation_controller = fields.Boolean(string="Validation controller", default=False)
    validation_controller = fields.Boolean(
        string="Validation controller", default=False,
        help="Start time of the order")
    # booking_identifier = fields.Boolean(string="Booking Identifier")
    booking_identifier = fields.Boolean(string="Booking Identifier",
                                        help="Field to identify booking")

    # salon_order_created_user = fields.Integer(string="Salon Order Created User", default=lambda self: self._uid)
    salon_order_created_user = fields.Integer(string="Salon Order Created User",
                                              default=lambda self: self._uid,
                                              help="The user whom the salon"
                                                   " order created.")
    count = fields.Integer(string='Delivery Orders', compute='_compute_count',
                           help="The count of the delivery")

    booking_for = fields.Selection([('for_salon','Salon'),('for_spa','Spa')], string="Booking For")
    is_spa_product = fields.Boolean(string="Spa Order")
    is_salon_product = fields.Boolean(string="Salon Order")

    user_id = fields.Many2one(related="chair_id.user_id")

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    employee_work_id = fields.Many2one('employee.work', string="Employee Work", compute="_default_employee_work_id")

    def _default_employee_work_id(self):
        employees = self.env['employee.work'].search([("employee_id", "=", self.user_id.id)])
        self.employee_work_id =  employees.id

    @api.depends('order_line_ids.price_subtotal')
    def _compute_price_subtotal(self):
        amount_untaxed = 0.0
        total_time_taken = 0.0
        for order in self:
            for line in order.order_line_ids:
                amount_untaxed += line.price_subtotal
                total_time_taken += line.time_taken
        self.price_subtotal = amount_untaxed
        time_takes = total_time_taken
        hours = int(time_takes)
        minutes = (time_takes - hours) * 60
        start_time_store = datetime.strptime(
            str(self.start_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
        self.write(
            {
                'end_time': start_time_store + timedelta(hours=hours, minutes=minutes),
                'time_taken_total': total_time_taken,
            })

    def _compute_count(self):
        """Compute invoice count of salon orders"""
        for orders in self:
            orders.count = self.env['account.move'].search_count(
                [('invoice_origin', '=', self.name)])

    def action_view_invoice_salon(self):
        return {
            'name': 'Invoices',
            'domain': [('invoice_origin', '=', self.name)],
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """
        return the stages to stage_ids
        """
        stage_ids = self.env['salon.stage'].search([])
        return stage_ids

    def write(self, values):
        """
        manage drag and drop in salon order kanban view
        """
        if 'stage_id' in values.keys():
            if self.stage_id.id == 3:
                if values['stage_id'] != 4:
                    raise ValidationError(_("You can't perform that move!"))
                else:
                    time_taken_chair = self.chair_id.total_time_taken_chair
                    self.chair_id.total_time_taken_chair = (
                            time_taken_chair - self.time_taken_total)
            if self.stage_id.id == 4:
                raise ValidationError(
                    _("You can't move a salon order from Closed stage!"))
            if self.stage_id.id == 5:
                raise ValidationError(
                    _("You can't move a salon order from Cancel stage!"))
            if self.stage_id.id == 1:
                if values['stage_id'] not in [2, 5]:
                    raise ValidationError(_("You can't perform that move!"))
            if self.stage_id.id == 2:
                if values['stage_id'] == 5:
                    time_taken_chair = self.chair_id.total_time_taken_chair
                    self.chair_id.total_time_taken_chair = (
                            time_taken_chair - self.time_taken_total)
                elif values['stage_id'] == 1 or values['stage_id'] == 4:
                    raise ValidationError(_("You can't perform that move!"))
                elif values['stage_id'] == 3 and not self.inv_stage_identifier:
                    self.action_create_invoice()
        if 'stage_id' in values.keys() and self.name == "Draft Salon Order":
            if values['stage_id'] == 2:
                self.action_validate()
                self.action_confirm()
        # write_values = super(SalonOrder, self).write(values)
        self.update_number_of_orders()
        return super(SalonOrder, self).write(values)

    def listToString(self, list1):
        str1 = " ,"
        return (str1.join(list1))

    def action_confirm(self):
        sequence_code = 'salon.order.sequence'
        order_date = str(self.date)
        order_date = order_date[0:10]
        self.name = self.env['ir.sequence'].with_context(
            ir_sequence_date=order_date).next_by_code(sequence_code)
        if self.partner_id:
            self.partner_id.partner_salon = True
        self.stage_id = 2
        self.update_number_of_orders()
        self.chair_id.total_time_taken_chair += self.time_taken_total
        self.user_id = self.chair_id.user_id

        if self.is_salon_product:
            print("If part..............salon...........")
            commission_rules = self.env['commission.rules'].search([('is_salon_product','=', True)], order='id desc', limit=1)

        elif self.is_spa_product:
            print("elIf part..............spa...........")
            commission_rules = self.env['commission.rules'].search([('is_spa_product','=', True)], order='id desc', limit=1)

        else:
            print("else part.........................")
            commission_rules = self.env['commission.rules'].search([('is_salon_product','=', True), ('is_spa_product', '=', True)], order='id desc', limit=1)

        employee_work = self.env['employee.work'].search([('employee_id','=',self.user_id.id)])
        if commission_rules:
            if commission_rules.target_price <= employee_work.total_amount:
                if commission_rules.based_on == 'percentage':
                    commission_amount = (commission_rules.percentage / 100) * self.price_subtotal
                if commission_rules.based_on == 'fix':
                    commission_amount = self.commission_amount + commission_rules.fix  
            else:
                commission_amount = 0
        else:
            commission_amount = 0

        employee_work_lines_ids = self.env['employee.work.lines']
        product_names = False
        if self.order_line_ids:
            list1 = []
            for line in self.order_line_ids:
                list1.append(line.product_id.name)
            product_names = self.listToString(list1)
        vals = {
                "employee_work_id" : self.order_line_ids.employee_work_id.id,
                "employee_id" : self.chair_id.user_id.id,
                "date" : self.date,
                "chair_id" : self.chair_id.id,
                "partner_id" : self.partner_id.id,
                "product_names" : product_names,
                "price_subtotal" : self.price_subtotal,
                "currency_id" : self.currency_id.id,
                "time_taken_total": self.time_taken_total,
                'commission_amount': commission_amount,
                }
        employee_work_lines = employee_work_lines_ids.create(vals)

    def action_validate(self):
        if self.order_line_ids:
            self.validation_controller = True
            self.update_number_of_orders()
            check_if_exist = self.env['res.partner'].search([('phone','=', self.phone)], limit=1)
            self.partner_id = check_if_exist.id
        else:
            raise ValidationError("Please Select The Product.")

    def action_close(self):
        self.stage_id = 4
        self.update_number_of_orders()

    def action_cancel(self):
        self.stage_id = 5
        self.update_number_of_orders()

    def action_update_total(self):
        for order in self:
            amount_untaxed = 0.0
            for line in order.order_line_ids:
                amount_untaxed += line.price_subtotal
            order.price_subtotal = amount_untaxed

    @api.onchange('chair_id')
    def _onchange_chair_id(self):
        if 'active_id' in self._context.keys():
            self.chair_id = self._context['active_id']

    def action_create_invoice(self):
        lines = []
        if self.partner_id:
            supplier = self.partner_id
        else:
            supplier = self.env['res.partner'].search(
                [("name", "=", "Salon Default Customer")], limit=1)

        product_id = self.env['product.product'].search(
            [("name", "=", "Salon Service")], limit=1)

        for record in self.order_line_ids:
            income_account = False
            if product_id.property_account_income_id:
                income_account = product_id.property_account_income_id.id
            elif product_id.categ_id.property_account_income_categ_id:
                income_account = product_id.categ_id.property_account_income_categ_id.id
            if not income_account:
                raise UserError(
                    _("Please define income account for product: '%s' (id:%d).") % (product_id.name, product_id.id))

            value = (0, 0, {
                'name': record.product_id.name,
                'account_id': income_account,
                'price_unit': record.price,
                'quantity': 1,
                'product_id': product_id.id,
            })
            lines.append(value)

        move_values = {
            'move_type': 'out_invoice',
            'partner_id': supplier.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'invoice_line_ids': lines,
        }

        invoice = self.env['account.move'].create(move_values)

        action = self.env.ref('account.action_move_out_invoice_type', raise_if_not_found=False)
        result = {
            'name': action.name,
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': invoice.id,
            'res_model': 'account.move',
        }

        self.inv_stage_identifier = True
        self.stage_id = 3

        invoiced_records = self.env['salon.order'].search(
            [('stage_id', 'in', [3, 4]), ('chair_id', '=', self.chair_id.id)])
        total = 0
        for row in invoiced_records:
            invoiced_date = row.date.strftime('%Y-%m-%d')[:10]
            if invoiced_date == str(date.today()):
                total += row.price_subtotal
        self.chair_id.collection_today = total
        self.update_number_of_orders()

        return result

    def unlink(self):
        for order in self:
            if order.stage_id.id == 3 or order.stage_id.id == 4:
                raise UserError(_("You can't delete an invoiced salon order!"))
        return super(SalonOrder, self).unlink()

    def update_number_of_orders(self):
        # self.chair_id.number_of_orders = len(self.env['salon.order'].search(
        #     [("chair_id", "=", self.chair_id.id), ("stage_id", "in", [2, 3])]))

        """ Function to update the number of active orders for the chair."""
        self.chair_id.number_of_orders = len(self.env['salon.order'].search([
        ]).filtered(lambda order: order.chair_id.id == self.chair_id.id
                                  and order.stage_id in [2, 3]))
class SalonOrderLine(models.Model):
    _name = 'salon.order.line'
    _description = 'Salon Order Lines'

    product_id = fields.Many2one("product.product", string="Service")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,default=lambda self: self.env.user.company_id.currency_id.id)
    price = fields.Monetary(string="Price")
    salon_order_id = fields.Many2one('salon.order', string="Salon Order", required=True, ondelete='cascade', index=True, copy=False)
    price_subtotal = fields.Monetary(string='Subtotal')
    time_taken = fields.Float(string='Time Taken')
    employee_work_id = fields.Many2one('employee.work', related="salon_order_id.employee_work_id")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.price = self.product_id.list_price
        self.price_subtotal = self.product_id.list_price

    @api.onchange('price')
    def _onchange_price(self):
        self.price_subtotal = self.price

    @api.onchange('price_subtotal')
    def _onchange_price_subtotal(self):
        self.price = self.price_subtotal

