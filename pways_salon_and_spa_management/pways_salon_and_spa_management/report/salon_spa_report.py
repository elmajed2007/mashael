from odoo import api, fields, models
from datetime import date

class SalonSpaReport(models.AbstractModel):
    _name = "report.pways_salon_and_spa_management.report_salon_spa"
    _description = "Salon Spa Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        report_of = data.get('report_of')
        if report_of == "employee":
            print("Its Employee report")
            employee = self.env['employee.work.lines'].browse(data.get("employee"))
            docs = {
                    "data" : data,
                    "docids": docids,
                    'employee': employee,
                    'start_date': start_date,
                    'end_date': end_date,
                    }

        elif report_of == "customer":
            print("Its Customer Report")
            customer = self.env['employee.work.lines'].browse(data.get("customer"))
            customer_membership = self.env['membership.membership_line'].browse(data.get("customer_membership"))
            total_customers = self.total_customers(customer)
            total_cutomer_orders = self.total_cutomer_orders(customer)
            docs = {
                    "data" : data,
                    "docids": docids,
                    'customer': customer,
                    'start_date': start_date,
                    'end_date': end_date,
                    'customer_membership': customer_membership,
                    'total_customers' : total_customers,
                    'total_cutomer_orders': total_cutomer_orders,
                    }
        else:
            income_sales = self.env['employee.work.lines'].browse(data.get("income_sales"))
            total_orders = self.total_orders(income_sales)
            total_orders_amount = self.total_orders_amount(income_sales)
            total_commission_amount = self.total_commission_amount(income_sales)

            docs = {
                    "data" : data,
                    "docids": docids,
                    'income_sales': income_sales,
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_orders' : total_orders,
                    'total_orders_amount' : total_orders_amount,
                    'total_commission_amount' : total_commission_amount,
                    }
        return docs

    def total_orders(self, income_sales):
        total = []
        if income_sales:
            for rec in income_sales:
                total.append(rec.id)
            total_orders = len(total)
            return total_orders
        else: 
            return 0 

    def total_orders_amount(self, income_sales):
        total = []
        if income_sales:
            for rec in income_sales:
                total.append(rec.price_subtotal)
            total_orders_amount = sum(total)
            print("total_orders_amount............", total_orders_amount)
            return total_orders_amount
        else: 
            return 0 

    def total_commission_amount(self, income_sales):
        total = []
        if income_sales:
            for rec in income_sales:
                total.append(rec.commission_amount)
                total_commission_amount = sum(total)
            return total_commission_amount
        else: 
            return 0  

    def total_customers(self, customer):
        total = []
        for rec in customer:
            total.append(rec.id)
        total_customers = len(total)
        if total_customers:
            return total_customers
        else:
            return 0

    def total_cutomer_orders(self, customer): 
        total = []
        for rec in customer:
            total.append(rec.price_subtotal)
        total_cutomer_orders = sum(total)
        if total_cutomer_orders:
            return total_cutomer_orders 
        else:
            return 0


