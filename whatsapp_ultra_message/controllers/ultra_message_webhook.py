# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
class WhatsappUltraMessage(http.Controller):
    @http.route('/whatsapp_ultra_message/receiving_messages', auth='public',method=["POST","GET"],type='json',csrf=False)
    def handling_receiving_message(self, **kw):
        print("kw:",kw)
        try:
            data = json.loads(request.httprequest.data)
            print(data)
        except Exception as e:
            print("exception is %s",e)

        return "Hello Youssef"
        # message_return = json.loads(request.body)
        #
        # bot = ultraChatBot(message_return)

        # y = bot.Processingـincomingـmessages()
        # if request.method == 'POST':
        #     message_return = json.loads(request.body)
        #
        #     bot = ultraChatBot(message_return)
        #
        #     y = bot.Processingـincomingـmessages()
        #     print("ke")
        #     return "Hello, world"

#     @http.route('/whatsapp_ultra_message/whatsapp_ultra_message/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('whatsapp_ultra_message.listing', {
#             'root': '/whatsapp_ultra_message/whatsapp_ultra_message',
#             'objects': http.request.env['whatsapp_ultra_message.whatsapp_ultra_message'].search([]),
#         })

#     @http.route('/whatsapp_ultra_message/whatsapp_ultra_message/objects/<model("whatsapp_ultra_message.whatsapp_ultra_message"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('whatsapp_ultra_message.object', {
#             'object': obj
#         })
