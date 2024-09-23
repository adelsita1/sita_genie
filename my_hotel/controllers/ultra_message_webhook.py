# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

{'event_type': 'message_received', 'instanceId': '94494', 'id': '', 'referenceId': '', 'hash': '906161c96882bbaeeae558880691231b', 'data': {'id': 'false_201229693795@c.us_E752BEE3B04403484D82379B2C010640', 'from': '201229693795@c.us', 'to': '201223663325@c.us', 'author': '', 'pushname': 'Cathy 😊', 'ack': '', 'type': 'chat', 'body': 'Hello', 'media': '', 'fromMe': False, 'self': False, 'isForwarded': False, 'isMentioned': False, 'quotedMsg': {}, 'mentionedIds': [], 'time': 1727079905}}
{'event_type': 'message_received', 'instanceId': '94494', 'id': '', 'referenceId': '', 'hash': '382e54eb899c161c5ac816d63a23cd78', 'data': {'id': 'false_201229693795@c.us_63759B4BFBBFE1E4F347E29039162324', 'from': '201229693795@c.us', 'to': '201223663325@c.us', 'author': '', 'pushname': 'Cathy 😊', 'ack': '', 'type': 'chat', 'body': 'Thank you', 'media': '', 'fromMe': False, 'self': False, 'isForwarded': False, 'isMentioned': False, 'quotedMsg': {'id': 'true_201229693795@c.us_3EB08E787B7B3073673D58', 'body': 'this image', 'fromMe': True}, 'mentionedIds': [], 'time': 1727079958}}

class WhatsappUltraMessage(http.Controller):
    @http.route('/whatsapp_ultra_message/receiving_messages', auth='public',method=["POST","GET"],type='json',csrf=False)
    def handling_receiving_message(self, **kw):
        print("kw:",kw)
        try:
            data = json.loads(request.httprequest.data)
            print(data)
            message_created=request.env["whatsapp_message_log"].sudo().create_message_received(data)
            print("message_created",message_created)
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

