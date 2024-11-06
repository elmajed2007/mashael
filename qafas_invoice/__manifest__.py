# -*- coding: utf-8 -*-
{
    'name': "Qafas",

    'summary': "Qafas",

    'description': """
    """,

    'author': "6sigmacode",
    'website': "",

    # for the full list
    'category': '',
    'version': '17.0.1.2',

    # any module necessary for this one to work correctly
    'depends': ['base','mail', 'account','sale','account_invoice_fixed_discount'
        , 'l10n_gcc_invoice','stock'],

    # always loaded
    'data': [
        "views/account_move_view.xml",
        "report/report.xml",
        "report/qafas_invoice_report.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}