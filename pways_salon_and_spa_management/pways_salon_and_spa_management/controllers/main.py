import json
import pytz
from datetime import datetime, time
from pytz import timezone, UTC

from odoo import fields, http
from odoo.http import request


class SalonBookingWeb(http.Controller):

    @http.route('/page/salon_details', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
    def salon_details(self, **kwargs):
        name = kwargs['name']
        phone = kwargs['phone']
        email = kwargs['email']
        date = kwargs['date']
        time = kwargs['time']

        dates_time = date+" "+time+":00"
        date_and_time = pytz.timezone(request.env.user.tz).localize(datetime.strptime(dates_time, '%m/%d/%Y %H:%M:%S')).astimezone(pytz.UTC).replace(tzinfo=None)
        salon_booking = request.env['salon.booking']
        booking_data = {
                        'name': name,
                        'phone': phone,
                        'time': date_and_time,
                        'email': email,
                        }
        salon_booking.create(booking_data)
        return json.dumps({'result': True})

    @http.route('/page/pways_salon_and_spa_management/salon_booking_thank_you', type='http',auth="public", website=True)
    def thank_you(self, **post):
        return request.render('pways_salon_and_spa_management.salon_booking_thank_you', {})

    @http.route('/page/pways_salon_and_spa_management/salon_booking_form', type='http',auth="public", website=True)

    def chair_info(self, **post):
        tz = request.env.user.tz
        date_check = datetime.utcnow()
        date_start = pytz.timezone(request.env.user.tz).localize(datetime.combine(date_check, time(0, 0, 0))).astimezone(pytz.UTC).replace(tzinfo=None)
        date_end = pytz.timezone(request.env.user.tz).localize(datetime.combine(date_check, time(23, 59, 59))).astimezone(pytz.UTC).replace(tzinfo=None)
        order_obj = request.env['salon.order'].search([('chair_id.active_booking_chairs', '=', True), ('stage_id', 'in', [1, 2, 3]), ('start_time', '>=', date_start), ('start_time', '<=', date_end)])
        return request.render(
            'pways_salon_and_spa_management.salon_booking_form', {
                'order_details': order_obj,
                'date_search': date_check})
