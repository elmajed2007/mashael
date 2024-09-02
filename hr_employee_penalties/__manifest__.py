# -*- coding: utf-8 -*-
{
    'name': "Hr Employee Penalties",

    'summary': "Hr Employee Penalties Addon",

    'description': """
Python Code Rules:
    result = -employee._calculate_penalties(payslip.date_from, payslip.date_to)
    """,

    'author': "Mahmoud Kousa",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '17.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_penalty_policy.xml',
        'views/hr_employee_penalty.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
