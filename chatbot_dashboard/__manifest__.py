# -*- coding: utf-8 -*-
{
    'name': "chatbot_dashboard",

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
    'depends': ['base','whatsapp_ultra_message','my_hotel',],

    # always loaded
    'data': [
       'views/bot_dashboard_view.xml',
    ],
    'assets':{
        'web.assets_backend':[
            'chatbot_dashboard/static/src/css/dashboard.css',
            'chatbot_dashboard/static/src/js/dashboard.js',
            'chatbot_dashboard/static/src/xml/dashboard.xml',

        ],
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

