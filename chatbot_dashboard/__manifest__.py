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
    'depends': ['base', 'whatsapp_ultra_message', 'my_hotel', 'web'],

    # always loaded
    'data': [
        'views/bot_dashboard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.min.js',
            # 'https://www.jsdelivr.com/package/npm/chart.js',
            # 'https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js',
            'chatbot_dashboard/static/src/js/helper_color_generator.js',
            'chatbot_dashboard/static/src/css/dashboard.css',
            'https://cdn.jsdelivr.net/npm/chart.js',
            'chatbot_dashboard/static/src/js/dashboard.js',
            'chatbot_dashboard/static/src/xml/dashboard.xml',

        ],
        'web.assets_frontend': [
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css',

        ]
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
