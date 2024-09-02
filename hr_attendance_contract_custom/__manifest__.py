# -*- coding: utf-8 -*-
{
    'name': "Hr Attendance Custom",

    'summary': "Hr Attendance Custom",

    'description': """
Attendance Python Code Rules:
    result = -employee._late_hours(payslip.date_from, payslip.date_to, 1)\n
    result = -employee._diff_hours(payslip.date_from, payslip.date_to, 0)\n
    result =  employee._working_hours(payslip.date_from, payslip.date_to, 0.5)\n
    result =  employee._weekend_hours(payslip.date_from, payslip.date_to, 2, 1.5)\n
    result =  employee._public_holiday_hours(payslip.date_from, payslip.date_to)\n
    result =  -employee._absence_days(payslip.date_from, payslip.date_to, payslip.id)\n
    result =  -employee._absence_penalties(payslip.date_from, payslip.date_to, payslip.id)\n
Egypt Taxes Python Code Rules:
    Employee social insurance => result = -contract._compute_employee_taxes(contract.id)[0]\n
    Company social insurance  => result = contract._compute_employee_taxes(contract.id)[1]\n
    Employee income tax       => result = -contract._compute_employee_taxes(contract.id)[2]\n
    """,

    'author': "Mahmoud Kousa",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '17.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_attendance', 'hr_contract', 'resource', 'hr_holidays', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/wizard.xml',
        'views/hr_attendance.xml',
        'views/hr_contract.xml',
        'views/hr_attendance_policy.xml',
        'views/resource_calendar.xml',
        # 'report/template.xml',
        'report/reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
