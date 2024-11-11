# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import api, fields, models

class SalonSequenceUpdater(models.Model):
    _name = 'salon.sequence.updater'
    _description = 'Salon Sequence Updater'

    salon_sequence = fields.Char(string="Salon Sequence")

class SalonChair(models.Model):
    _name = 'salon.chair'
    _description = 'Salon Chair'

    name = fields.Char(string="Chair", required=True, default=lambda self: self.env['salon.sequence.updater'].browse(1).salon_sequence or "Chair-1")
    number_of_orders = fields.Integer(string="No.of Orders")
    collection_today = fields.Float(string="Today's Collection")
    # user_id = fields.Many2one('res.users', string="User", readonly=True,help="""You can select the user from the Users Tab. Last user from the Users Tab will be selected as the Current User.""")
    # user_id = fields.Many2one('res.users', string="User", readonly=True, default=lambda self: self.env.user)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)
    # date = fields.Datetime(string="Date", readonly=True)
    date = fields.Datetime(string="Date", readonly=True, default=lambda self: fields.Datetime.now())
    user_line = fields.One2many('salon.chair.user', 'salon_chair_id', string="Users")
    total_time_taken_chair = fields.Float(string="Time Reserved(Hrs)")
    active_booking_chairs = fields.Boolean(string="Active booking chairs")
    chair_created_user = fields.Integer(string="Salon Chair Created User", default=lambda self: self._uid)
    employee_id = fields.Many2one("hr.employee", string="Employee")
    chair_image = fields.Binary()

    @api.model
    def create(self, values):
        sequence_code = 'salon.chair.sequence'
        sequence_number = self.env['ir.sequence'].next_by_code(sequence_code)
        self.env['salon.sequence.updater'].browse(1).write(
            {'salon_sequence': sequence_number})
        if 'user_line' in values.keys():
            if values['user_line']:
                date_changer = []
                for elements in values['user_line']:
                    date_changer.append(elements[2]['start_date'])
                number = 0
                for elements in values['user_line']:
                    number += 1
                    if len(values['user_line']) == number:
                        break
                    elements[2]['end_date'] = date_changer[number]
                values['user_id'] = values['user_line'][len(
                    (values['user_line'])) - 1][2]['user_id']
                values['date'] = values['user_line'][len(
                    (values['user_line'])) - 1][2]['start_date']
        return super(SalonChair, self).create(values)

    def write(self, values):
        """
        add sequence for chair, start date and end date on editing record
        """
        if 'user_line' in values.keys():
            if values['user_line']:
                date_changer = []
                for elements in values['user_line']:
                    if str(elements[1]).startswith('v'):
                        date_changer.append(elements[2]['start_date'])
                number = 0
                num = 0
                for records in self.user_line:
                    if records.end_date is False:
                        if date_changer:
                            records.end_date = date_changer[0]
                for elements in values['user_line']:
                    number += 1
                    if elements[2] is not False:
                        num += 1
                        if len(values['user_line']) == number:
                            break
                        elements[2]['end_date'] = date_changer[num]
                values['user_id'] = values['user_line'][len(
                    (values['user_line'])) - 1][2]['user_id']
                values['date'] = values['user_line'][len(
                    (values['user_line'])) - 1][2]['start_date']
        return super(SalonChair, self).write(values)

    def clear_chair(self):
        for rec in self.user_line:
            rec.read_only_checker = False
            rec.user_id.user_salon_active = False
        self.user_id = False
        self.user_line.unlink()

    def free_user(self):
        for rec in self.user_line:
            if rec.user_id.user_salon_active:
                rec.read_only_checker = False
                rec.user_id.user_salon_active = False
                rec.unlink()
        self.user_id = False

class SalonChairUser(models.Model):
    _name = 'salon.chair.user'
    _description = 'Salon Chair User'

    read_only_checker = fields.Boolean(string="Checker", default=True)
    user_id = fields.Many2one('res.users', string="User", required=True)
    start_date = fields.Datetime(string="Start Date", default=fields.Datetime.now, required=True)
    end_date = fields.Datetime(string="End Date")
    salon_chair_id = fields.Many2one('salon.chair', string="Chair", required=True, ondelete='cascade', index=True, copy=False)

    @api.model
    def create(self, val):
        chairs = self.env['salon.chair'].search([])
        all_active_users = []
        for records in chairs:
            if records.user_id:
                all_active_users.append(records.user_id.id)
                records.user_id.write({'user_salon_active': True})
        users = self.env['res.users'].search(
            [('id', 'not in', all_active_users)])
        for records in users:
            records.write({'user_salon_active': False})
        val['read_only_checker'] = True
        return super(SalonChairUser, self).create(val)




