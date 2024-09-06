# -*- coding: utf-8 -*-
{
    'name': "HR Custody",

    'summary': """
       HR Custody Request for tangable and non-tangable types of custodies""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'images': ['static/description/logo.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'account_asset', 'mail', 'digest', 'bstt_hr', 'fleet'],

    # always loaded
    'data': [
        'security/access_group.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_custody_report_action.xml',
        'views/views.xml',
        'views/templates.xml',
        'report/hr_custody_report.xml',
        'report/hr_custody_return_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
