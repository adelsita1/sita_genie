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
    'depends': ['base', 'mail', 'whatsapp_ultra_message', 'crm'],
    'external_dependencies': {
        'python': ['PyPDF2', 'langchain',"langchain_community","python-dotenv","openai","langchain_openai","torch",
                   "requests","dotenv","uuid","sentence_transformers","spacy","numpy"],  # List any required Python libraries here
    },
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
        'views/reservation_lead.xml',
        'views/translation_rule.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'application': True,
    'installable': True
}
