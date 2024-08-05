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
    'depends': ['base','mail','purchase','account','stock','stock_delivery'],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        "views/freight_mode.xml",
        "views/destination_view.xml",
        "views/purchase_order_view.xml",
        "views/hs_code.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}