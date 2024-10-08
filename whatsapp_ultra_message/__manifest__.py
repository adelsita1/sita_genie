# -*- coding: utf-8 -*-
{
    'name': "whatsapp_ultra_message",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Automated Whats app Message
    """,

    'author': "SITA-EGYPT",
    'website': "https://www.sita-eg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/res_config_settings.xml',
        'views/ultra_message_account.xml',
        'views/predefined_custom_message.xml',
        'wizards/custom_message_wizard.xml',
        'views/partner_server_action.xml',
        'views/messages_log.xml',
        'views/res_partner.xml',
        'views/question_answers.xml',
        'views/template_view_chat.xml',

    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
