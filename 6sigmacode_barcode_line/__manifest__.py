# -*- coding: utf-8 -*-
{
    'name': '6sigmacode Barcode',
    'version': '15.0.0',
    'author': "6SigmaCode",
    'summary': '',
    'description': """ This module for add barcode field in invoice""",
    'category': 'Inventory',
    'depends': ['base_setup', 'stock', 'account', 'purchase', 'sale_management',
                ],
    'data': [
        'views/account_move_views.xml',
        'views/invoice_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
