# -*- coding: utf-8 -*-
{
    'name': "Masha3eel",

    'summary': "Masha3eel",

    'description': """
    """,

    'author': "6sigmacode",
    'website': "",

    # for the full list
    'category': '',
    'version': '17.0.1.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'purchase', 'account', 'stock', 'sr_warranty_management', 'dev_hr_loan','hr_end_service_benefits','hr'],

    # always loaded
    'data': [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/freight_mode.xml",
        "views/destination_view.xml",
        "views/purchase_order_view.xml",
        "views/hs_code.xml",
        "report/warrently_report.xml",
        "views/hr_loan.xml",
        "views/hr_employee.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
