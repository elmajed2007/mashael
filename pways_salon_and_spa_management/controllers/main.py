import json
import pytz
from datetime import datetime, time, timedelta
from pytz import timezone, UTC

from odoo import fields, http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


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

    # def chair_info(self, **post):
    #     tz = request.env.user.tz
    #     date_check = datetime.utcnow()
    #     date_start = pytz.timezone(request.env.user.tz).localize(datetime.combine(date_check, time(0, 0, 0))).astimezone(pytz.UTC).replace(tzinfo=None)
    #     date_end = pytz.timezone(request.env.user.tz).localize(datetime.combine(date_check, time(23, 59, 59))).astimezone(pytz.UTC).replace(tzinfo=None)
    #     order_obj = request.env['salon.order'].search([('chair_id.active_booking_chairs', '=', True), ('stage_id', 'in', [1, 2, 3]), ('start_time', '>=', date_start), ('start_time', '<=', date_end)])
    #     return request.render(
    #         'pways_salon_and_spa_management.salon_booking_form', {
    #             'order_details': order_obj,
    #             'date_search': date_check})

    def chair_info(self, **post):
        tz = request.env.user.tz
        date_check = datetime.utcnow()
        date_start = pytz.timezone(request.env.user.tz).localize(
            datetime.combine(date_check, time(0, 0, 0))).astimezone(pytz.UTC).replace(tzinfo=None)
        date_end = pytz.timezone(request.env.user.tz).localize(
            datetime.combine(date_check, time(23, 59, 59))).astimezone(pytz.UTC).replace(tzinfo=None)
        order_obj = request.env['salon.order'].search(
            [('chair_id.active_booking_chairs', '=', True), ('stage_id', 'in', [1, 2, 3]),
             ('start_time', '>=', date_start), ('start_time', '<=', date_end)])

        chairs = request.env['salon.chair'].search([])

        return request.render(
            'pways_salon_and_spa_management.salon_booking_form', {
                'order_details': order_obj,
                'date_search': date_check,
                'chairs': chairs,
            })

    @http.route('/salon_booking_submit', type='http', auth="public", website=True)
    def salon_booking_submit(self, **post):
        # Create a new salon booking record with the submitted information
        name = post.get('name')
        phone = post.get('phone')
        email = post.get('email')
        chair_id = post.get('chair')
        time = post.get('date') + ' ' + post.get('time')

        if not name or not phone or not email or not chair_id or not time:
            return request.redirect('/page/pways_salon_and_spa_management/salon_booking_form')

        salon_booking_vals = {
            'name': name,
            'phone': phone,
            'email': email,
            'chair_id': int(chair_id),
            'time': time,
            'booking_for': 'for_salon',  # Assuming default value
        }

        request.env['salon.booking'].sudo().create(salon_booking_vals)

        # Redirect to a thank you page after successful submission
        # return request.redirect('/page/pways_salon_and_spa_management/salon_booking_thank_you')
        return request.redirect('/page/pways_salon_and_spa_management/salon_booking_form')


class SalonOrders(http.Controller):
    """Returns the chairs for dashboard"""

    # @http.route('/salon/chairs', type='json', auth='public')
    # def get_salon_chairs(self, **kwargs):
    #     today_date = datetime.today().date()
    #     formatted_date = today_date.strftime("%Y-%m-%d")
    #
    #     # Generate working hours
    #     working_hours = []
    #     current_time = datetime.strptime("07:00", "%H:%M")
    #     while current_time.strftime("%H:%M") != "23:30":
    #         working_hours.append(current_time.strftime("%H:%M"))
    #         current_time = (current_time + timedelta(minutes=30))
    #     working_hours.append(current_time.strftime("%H:%M"))
    #
    #     chairs = []
    #     salon_chairs = request.env['salon.chair'].sudo().search([])
    #     for chair in salon_chairs:
    #         orders_info = []
    #         orders = request.env['salon.order'].sudo().search([('chair_id', '=', chair.id)])
    #         for order in orders:
    #             order_lines = []
    #             for line in order.order_line_ids:
    #                 order_lines.append({
    #                     'service_name': line.product_id.name,
    #                     'price': line.price,
    #                 })
    #             orders_info.append({
    #                 'customer_name': order.customer_name,
    #                 'services': order_lines,
    #                 'date': order.date.strftime('%Y-%m-%d'),
    #                 'order_time': order.date.strftime("%H:%M"),
    #                 'formatted_date': formatted_date,
    #             })
    #         chair_image = chair.chair_image.decode('utf-8') if chair.chair_image else None
    #         chairs.append({
    #             'id': chair.id,
    #             'name': chair.name,
    #             'orders': orders_info,
    #             'chair_image': chair_image,
    #             'orders_count': len(orders_info),
    #         })
    #     return {'chairs': chairs, 'working_hours': working_hours}

    @http.route('/salon/chairs', type='json', auth='public')
    def get_salon_chairs(self, **kwargs):
        today_date = datetime.today().date()
        formatted_date = today_date.strftime("%Y-%m-%d")
        chairs = []
        salon_chairs = request.env['salon.chair'].sudo().search([])
        for chair in salon_chairs:
            orders_info = []
            # orders = request.env['salon.order'].sudo().search([('chair_id', '=', chair.id),('stage_id', 'in', [2, 3])])
            orders = request.env['salon.order'].sudo().search([('chair_id', '=', chair.id)])
            for order in orders:
                order_lines = []
                for line in order.order_line_ids:
                    order_lines.append({
                        'service_name': line.product_id.name,
                        'price': line.price,
                    })
                orders_info.append({
                    'customer_name': order.customer_name,
                    'services': order_lines,
                    'date': order.date.strftime('%Y-%m-%d'),
                    'order_time': order.date.strftime("%H:%M"),
                    'formatted_date': formatted_date,
                    # 'start_time': order.start_hour,
                    # 'end_time': order.end_hour,
                })
            chair_image = chair.chair_image.decode('utf-8') if chair.chair_image else None
            chairs.append({
                'id': chair.id,
                'name': chair.name,
                'orders': orders_info,
                'chair_image': chair_image,
                'orders_count': len(orders_info),
            })
        return chairs

    # @http.route('/salon/chairs', type='json', auth='public')
    # def get_salon_chairs(self, **kwargs):
    #     chairs = []
    #     salon_chairs = request.env['salon.chair'].sudo().search([])
    #     for chair in salon_chairs:
    #         orders_info = []
    #         orders = request.env['salon.order'].sudo().search([
    #             ('chair_id', '=', chair.id),
    #             ('stage_id', 'in', [2, 3])
    #         ])
    #         for order in orders:
    #             order_lines = []
    #             for line in order.order_line_ids:
    #                 order_lines.append({
    #                     'service_name': line.product_id.name,
    #                     'price': line.price,
    #                 })
    #             orders_info.append({
    #                 'customer_name': order.customer_name,
    #                 'services': order_lines,
    #                 'date': order.date.strftime('%Y-%m-%d'),
    #                 # 'start_time': order.start_hour,
    #                 # 'end_time': order.end_hour,
    #             })
    #         chair_image = chair.chair_image.decode('utf-8') if chair.chair_image else None
    #         chairs.append({
    #             'id': chair.id,
    #             'name': chair.name,
    #             'orders': orders_info,
    #             'chair_image': chair_image,
    #             'orders_count': len(orders_info),
    #         })
    #     return chairs


    @http.route(['/salon/chairs2'], auth="public", type='json',
                website=True)
    def elearning_snippet2(self, **kwargs):
        if len(kwargs) > 0:
            date = kwargs['date']
            print(date)
        chairs = []
        salon_chairs = request.env['salon.chair'].sudo().search([])
        number_of_orders = {}
        counter = 0
        searcheddate = fields.Date.today()
        afterserachdate = searcheddate
        if date:
            searcheddate = datetime.strptime(date, '%Y-%m-%d')
            afterserachdate = searcheddate
        afterserachdate = afterserachdate + timedelta(days=1)
        for i in salon_chairs:
            orders_data = []
            number_of_orders.update({i.id: len(request.env['salon.order'].search(
                [("chair_id", "=", i.id),
                 ("stage_id", "in", [2, 3])]))})
            orders = request.env['salon.order'].search(
                [("chair_id", "=", i.id),
                 ("stage_id", "in", [2, 3]), ("date", ">=", searcheddate), ("date", "<", afterserachdate)])
            chairs.append(
                {'name': i.name, 'id': i.id, 'orders': number_of_orders[i.id]})

            for j in orders:
                year = j.date.year
                month = j.date.month
                day = j.date.day
                hour = j.date.hour
                minute = 00
                sec = j.date.second
                if j.date.minute >= 30:
                    minute = 30
                order_date = datetime.now()
                order_date = order_date.replace(year=year, month=month, day=day, hour=hour, minute=minute, second=sec)
                str_date = datetime.strftime(order_date, "%Y-%m-%d %H:%M:%S")
                date = fields.Datetime.context_timestamp(
                    request.env['salon.order'], datetime.strptime(str_date, DEFAULT_SERVER_DATETIME_FORMAT))
                orders_data.append({'customer_name': j.partner_id.name, 'date': datetime.strftime(date, "%H:%M")
                                    })
                cell_numbers = 1
                if j.time_taken_total > 0.5:
                    string_number = str(j.time_taken_total)
                    split_number = string_number.split(".")
                    integer_part = int(split_number[0])
                    fractional_part = float(split_number[1])
                    cell_numbers = integer_part * 2
                    if fractional_part > 0:
                        cell_numbers += 1
                cell_content = ""
                customer_name = ""
                time_taken = timedelta(hours=j.time_taken_total)
                cells = []

                for x in range(cell_numbers):
                    if date.hour > 12:
                        date = date - timedelta(hours=12)
                        cells.append(datetime.strftime(date, "%H:%M") + " pm")
                        date = date + timedelta(minutes=30)
                    else:
                        cells.append(datetime.strftime(date, "%H:%M"))
                        date = date + timedelta(minutes=30)
                serviecs = ""
                # for ol in j.order_line_ids:
                #     if len(serviecs) > 0:
                #         serviecs = serviecs + " , " + ol.service_id.display_name
                #     else:
                #         serviecs = ol.service_id.display_name
                if j.partner_id.name:
                    customer_name = j.partner_id.name
                special = ""
                # if j.speical:
                #     special = "specialtrue"
                if cell_numbers == 1:
                    cell_content = j.name + "/" + str(
                        j.id) + special + "\n Customer: " + customer_name + "\n Amount: " + str(
                        j.price_subtotal) + "\n Total Time Taken: " + str(time_taken) + "\n Services: " + serviecs
                else:
                    cell_content = j.name + "/" + str(
                        j.id) + special + "\n Customer: " + customer_name + "\n Cost: " + str(
                        j.price_subtotal) + "\n Total Time Taken: " + str(time_taken) + "\n Services: " + serviecs
                for cell in cells:
                    chairs[counter].update({cell: cell_content})
                    cell_content = ""

            counter += 1
            print(orders)
            # print(i.id)

        print(number_of_orders, 'main')
        values = {
            's_chairs': chairs
        }
        print(values)

        # response = http.Response(
        #     template='salon_management.dashboard_salon_chairs', qcontext=values)
        # # print(response.render())
        # return response.render()
        return chairs