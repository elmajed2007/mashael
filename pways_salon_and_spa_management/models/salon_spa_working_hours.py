from odoo import api, fields, models

class SalonWorkingHours(models.Model):
    _name = 'salon.working.hours'
    _description = 'Salon Working Hours'

    name = fields.Char(string="Name")
    from_time = fields.Float(string="Starting Time")
    to_time = fields.Float(string="Closing Time")
    total_slots = fields.Integer(string="Total Slots")
    salon_booking_hours_lines_ids = fields.One2many("salon.working.hours.lines", 'salon_working_hours_id', string="Salon Working Hours Lines")
    available_slots = fields.Char(string="Available Slots")

    @api.onchange('from_time', 'to_time', 'total_slots')
    def generate_time_slots(self):
        self.salon_booking_hours_lines_ids = False
        if self.from_time and self.to_time and self.total_slots:
            duration = abs((self.to_time - self.from_time) / self.total_slots)
            slot_start = self.from_time
            slot_end = slot_start + duration
            slots = []
            for slot_no in range(1, self.total_slots + 1):
                slot_vals = {
                    'slot_no': slot_no,
                    'slot_start': slot_start,
                    'slot_end': slot_end,
                    'slot_time': duration,
                    'max_slots': 0,
                }
                slots.append((0, 0, slot_vals))
                slot_start = slot_end
                slot_end += duration
            self.salon_booking_hours_lines_ids = slots


class SalonWorkingHoursLines(models.Model):
    _name = 'salon.working.hours.lines'
    _description = 'Salon Working Hours Lines'

    slot_no = fields.Integer(string="Slot Number")
    slot_time = fields.Float(string="Slot Time")
    slot_start = fields.Float(string="Slot Start")
    slot_end = fields.Float(string="Slot End")
    max_slots = fields.Integer(string="Max No of Slots")
    salon_working_hours_id = fields.Many2one('salon.working.hours', string="Salon Working Hours")



access_salon_working_hours_manager,salon.working.hours,model_salon_working_hours,pways_salon_and_spa_management.group_salon_manager,1,1,1,1
access_salon_working_hours_lines_manager,salon.working.hours.lines,model_salon_working_hours_lines,pways_salon_and_spa_management.group_salon_manager,1,1,1,1
access_salon_working_hours_public,salon.working.hours,model_salon_working_hours,base.group_public,1,0,0,0
access_salon_working_hours_portal,salon.working.hours,model_salon_working_hours,base.group_portal,1,1,0,0

# from odoo import api, fields, models
# from datetime import datetime, date

# class SalonWorkingHours(models.Model):
#     _name = 'salon.working.hours'
#     _description = 'Salon Working Hours'

#     name = fields.Char(string="Name")
#     from_time = fields.Float(string="Starting Time")
#     to_time = fields.Float(string="Closing Time")
#     total_slots = fields.Integer(string="Total Slots")
#     salon_booking_hours_lines_ids = fields.One2many("salon.working.hours.lines",'salon_working_hours_id', string="Salon Working Hours Lines")
#     available_slots = fields.Char(string="Available Slots")

# class SalonWorkingHoursLines(models.Model):
#     _name = 'salon.working.hours.lines'
#     _description = 'Salon Working Hours lines'

#     slot_no = fields.Integer(string="Slot Number")
#     slot_time = fields.Float(string="Slot Time")
#     slot_start = fields.Float(string="Slot Start")
#     slot_end = fields.Float(string="Slot End")
#     max_slots = fields.Integer(string="Max No of slot")
#     salon_working_hours_id = fields.Many2one('salon.working.hours')