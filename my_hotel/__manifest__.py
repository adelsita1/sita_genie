# -*- coding: utf-8 -*-
{
    'name': "my_hotel",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'whatsapp_ultra_message'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/reservation_keywords_data.xml',
        'views/hotel.xml',
        'views/pdf_file.xml',
        'views/room.xml',
        'views/room_types.xml',
        'views/room_rates.xml',
        'views/rate_rules.xml',
        'views/reservation_keyword.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'application': True,
    'installable': True
}
