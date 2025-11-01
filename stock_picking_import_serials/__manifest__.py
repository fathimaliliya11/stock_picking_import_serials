# -*- coding: utf-8 -*-
{
    'name': "Stock Picking Import Serials",
    'summary': """
        Easily import lot/serial numbers from Excel into stock pickings""",
    'description': """
         This module allows users to bulk import serial or lot numbers directly into a stock picking via an Excel file. It simplifies handling serialized products during receipts or deliveries.
    """,
    'author': "Fathima Liliya",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/picking_import_import_wizard_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
