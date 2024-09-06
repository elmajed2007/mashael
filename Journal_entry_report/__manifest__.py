# -*- coding: utf-8 -*-
{
    'name': "Journal Entry Report",
    'summary': """Journal Entry Report""",
    'description': """create journal report""",
    'version': '17.0.0.1',
    'category': 'Accounting',
    'author': "6Sigmacode",
    'website': "",
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'account',],
    'qweb': [],
    'data': [
        'report/report.xml',
        'report/journal_report.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
