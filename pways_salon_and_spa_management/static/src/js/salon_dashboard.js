/** @odoo-module */
import { jsonrpc } from "@web/core/network/rpc_service";
import { Component, onMounted, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");
import { _t } from "@web/core/l10n/translation";
const { useRef } = owl;
/* Create a component named 'SalonDashboard' with extending Component*/
export class SalonDashboard extends Component {
        setup() {
            super.setup(...arguments);
            var self = this;
            this.bookings_count = useRef("bookings_count");
            this.recent_count = useRef("recent_count");
            this.orders_count = useRef("orders_count");
            this.clients_count = useRef("clients_count");
            this.chairs_dashboard_view = useRef("chairs_dashboard_view");
            this.dashboard_salon_chairs= useRef("dashboard_salon_chairs");
            this.salon_chair = useRef("Salon-Chair");
            this.order_click = useRef("order_details");
            this.state = useState({list : []});
            this.orm = useService('orm');
               onMounted(() => {
                                   this.render_dashboards();
               });
        }
        /** Function that works that render values into dashboard **/
     async render_dashboards (ev) {
              var self = this
             var result = await this.orm.call('salon.booking', 'get_booking_count', [0], {})
             $(this.bookings_count.el).append("<span class='stat-digit'>" + result.bookings + "</span>");
             $(this.recent_count.el).append("<span class='stat-digit'>" + result.sales + "</span>");
             $(this.orders_count.el).append("<span class='stat-digit'>" + result.orders + "</span>");
             $(this.clients_count.el).append("<span class='stat-digit'>" + result.clients + "</span>");
             this.state.list = await jsonrpc("/salon/chairs", {});
//             const jsonString = JSON.stringify(this.state.list);
//             this.state.list=JSON.stringify(this.state.list)
//             alert(jsonString);
             $(self.chairs_dashboard_view.el).append(this.state.list)
//               var values = await jsonrpc("/salon/chairs", {});
//               $('#chairs_dashboard_view').append(values);

        }
    /** Click function of 'Bookings' card and open bookings list view**/
    show_bookings(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        this.env.services.action.doAction({
            name: _t("Salon Bookings"),
            type: 'ir.actions.act_window',
            res_model: 'salon.booking',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'approved']],
            target: 'current'
        });
    }
    /** Click function of 'Recent Works' card in dashboard**/
    show_sales (ev) {
    ev.stopPropagation();
    ev.preventDefault();
    this.env.services.action.doAction({
        name: _t("Recent Works"),
        type: 'ir.actions.act_window',
        res_model: 'salon.order',
        view_mode: 'tree,form',
        views: [[false, 'list'], [false, 'form']],
        domain: [['stage_id', 'in', [3, 4]]],
        target: 'current'
        });
    }
    /** Click function of 'Salon Client' card**/
    show_clients(e) {
    var self = this;
    e.stopPropagation();
    e.preventDefault();
     this.env.services.action.doAction({
        name: _t("Clients"),
        type: 'ir.actions.act_window',
        res_model: 'res.partner',
        view_mode: 'tree,form',
        views: [[false, 'list'], [false, 'form']],
        domain: [['partner_salon', '=', true]],
        target: 'current'
        });
    }
    /** Click function of 'Salon Orders' card**/
    show_orders(ev) {
    var self = this;
    ev.stopPropagation();
    ev.preventDefault();
    this.env.services.action.doAction({
        name: _t("Salon Orders"),
        type: 'ir.actions.act_window',
        res_model: 'salon.order',
        view_mode: 'tree,form,calendar',
        views: [[false, 'list'], [false, 'form']],
        target: 'current'
        });
    }
    /** Click function of dashboard chairs **/
    chairs_click(ev) {
    var self = this;
    ev.stopPropagation();
    ev.preventDefault();
    var active_id = event.target.id
     this.env.services.action.doAction({
        name: _t("Chair Orders"),
        type: 'ir.actions.act_window',
        res_model: 'salon.order',
        view_mode: 'kanban,tree,form',
        views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
        domain: [['chair_id', '=', parseInt(active_id)]],
        context: {
            default_chair_id: parseInt(active_id)
        },
        target: 'current'
    });
    }
    /** Click function of dashboard chair's settings icon **/
    settings_click (ev) {
        var self = this;
        ev.stopPropagation();
        ev.preventDefault();
        var active_id = event.target.id
         this.env.services.action.doAction({
            name: _t("Chair Orders"),
            type: 'ir.actions.act_window',
            res_model: 'salon.chair',
            view_mode: 'form',
            views: [[false, 'form']],
            context: {
                default_name: active_id
            },
            target: 'current'
        });
    }
    order_click (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            var param = event.target.id
            var active_id = param.split('/')[3];
//            alert(param)
//            alert(active_id)
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            if (param!="")
            {
            this.do_action({
                name: _t("Chair Orders"),
                type: 'ir.actions.act_window',
                res_model: 'salon.order',
                res_id: parseInt(active_id),
                view_mode: 'form',
                views: [[false, 'form']],
                domain: [['id', '=', parseInt(active_id)]],
                context: {
                    default_id: parseInt(active_id)
                },
                target: 'current'
            }, options);
            }
        }

    order_click_new(ev) {
        var self = this;
        ev.stopPropagation();
        ev.preventDefault();
        var param = event.target.id;
        var active_id = param.split(',')[1];
        var time = param.split(',')[0];
        time = time.replace("(", "");
        time = time.replace("'", "");
        time = time.replace("'", "");
        time = time + ":00";
        var offset = new Date().getTimezoneOffset();
        offset = offset / 60;
        var pmdiff = 0;
        if (time.includes("pm")) {
            time = time.replace(' pm', '');
            pmdiff = 12;
        }
        var hour = time.split(':')[0];
        hour = parseInt(hour) + parseInt(pmdiff);
        var minute = time.split(':')[1];
        var sec = time.split(':')[2];
        hour = parseInt(hour) + offset;
        var timeformat;
        if (hour < 10) {
            timeformat = "0" + String(hour) + ":" + minute + ":" + sec;
        } else {
            timeformat = String(hour) + ":" + minute + ":" + sec;
        }

        // Construct the datetime string in the required format
        var now = new Date();
        var year = now.getFullYear();
        var month = ('0' + (now.getMonth() + 1)).slice(-2);
        var day = ('0' + now.getDate()).slice(-2);
        var date = year + '-' + month + '-' + day + ' ' + timeformat;

        // Access the action service through env
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        if (param != "") {
            // Create a context object and add default_date and default_chair_id to it
            var context = {
                default_id: parseInt(active_id),
                default_chair_id: parseInt(active_id)
            };
            context['default_date'] = date; // Add default_date dynamically

            self.env.services.action.doAction({
                name: _t("Chair Orders"),
                type: 'ir.actions.act_window',
                res_model: 'salon.order',
                view_mode: 'form',
                views: [[false, 'form']],
                domain: [['id', '=', parseInt(active_id)]],
                context: context, // Use the context object with default_date
                target: 'current'
            }, options);
        }
    }


    async onFileChanged(ev) {

     var myInput = document.getElementById("order_date");
     var inputValue = myInput.value;
     var booking_record = { 'date': inputValue};
      const jsonString = JSON.stringify(booking_record);
//      alert(jsonString);
       var jsonStrin = await jsonrpc("/salon/chairs2", {'date':inputValue});
      jsonStrin = JSON.stringify(jsonStrin);
//      alert(jsonStrin);
//      $('#chairs_dashboard_view').html("");
      $(this.chairs_dashboard_view.el).append(jsonStrin)

//     await jsonrpc("/salon/chairs2", "call", {'date':inputValue}).then(function (values) {
//     const jsonString = JSON.stringify(values);
//      alert(jsonString);
//     this.state.list=values
//                 $('#chairs_dashboard_view').html("");
//                $('#chairs_dashboard_view').append(this.state.list);
//            });
            }
}
SalonDashboard.template = "SalonSpaDashBoard";
actionRegistry.add("salon_dashboard", SalonDashboard);
