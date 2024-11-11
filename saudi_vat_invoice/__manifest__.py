# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

{
    'name': 'Saudi VAT Invoice /Saudi E-Invoice /Saudi Electronic Invoice',
    'version': '17.0.0.1',
    'sequence': 1,
    'category': 'Accounting',
    'summary': 'Saudi VAT Invoice / E-Invoice / Saudi Electronic Invoice / Electronic Invoice KSA',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'price': 20,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """
Saudi VAT Invoice / E-Invoice / Saudi Electronic Invoice / Electronic Invoice KSA
        """,
    'depends': ['account', 'sa_uae_vat'],
    'data': [
        'views/vat_invoice_view.xml',
        'views/res_config_settings_view.xml',

    ],
    'images': ['images/main_screenshot.gif'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
