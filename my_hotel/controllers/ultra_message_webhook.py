# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from datetime import datetime
import werkzeug.wrappers
# from memory_profiler import memory_usage,profile
log_file=open("memory.log","w+")
# from ..project_api.models.common import invalid_response, valid_response
# {'event_type': 'message_received', 'instanceId': '94494', 'id': '', 'referenceId': '', 'hash': '906161c96882bbaeeae558880691231b', 'data': {'id': 'false_201229693795@c.us_E752BEE3B04403484D82379B2C010640', 'from': '201229693795@c.us', 'to': '201223663325@c.us', 'author': '', 'pushname': 'Cathy 😊', 'ack': '', 'type': 'chat', 'body': 'Hello', 'media': '', 'fromMe': False, 'self': False, 'isForwarded': False, 'isMentioned': False, 'quotedMsg': {}, 'mentionedIds': [], 'time': 1727079905}}
# {'event_type': 'message_received', 'instanceId': '94494', 'id': '', 'referenceId': '', 'hash': '382e54eb899c161c5ac816d63a23cd78', 'data': {'id': 'false_201229693795@c.us_63759B4BFBBFE1E4F347E29039162324', 'from': '201229693795@c.us', 'to': '201223663325@c.us', 'author': '', 'pushname': 'Cathy 😊', 'ack': '', 'type': 'chat', 'body': 'Thank you', 'media': '', 'fromMe': False, 'self': False, 'isForwarded': False, 'isMentioned': False, 'quotedMsg': {'id': 'true_201229693795@c.us_3EB08E787B7B3073673D58', 'body': 'this image', 'fromMe': True}, 'mentionedIds': [], 'time': 1727079958}}
import gc
class WhatsappUltraMessage(http.Controller):

    @http.route('/whatsapp_ultra_message/receiving_messages', auth='public',methods=["POST","GET"],type='json',csrf=False)
    def handling_receiving_message(self, **kw):
        start_time= datetime.now()

        # try:

        data = json.loads(request.httprequest.data)
        print("data given in controller",data)
        message_hash=request.env["whatsapp_message_log"].sudo().search([("message_hash","=",data["hash"])])
        if message_hash:
            print("message_hash exist",message_hash)
            return valid_response(status=200,data="ok")
        if not data:
            return
        message_created=request.env["whatsapp_message_log"].sudo().with_context(prefetch_fields=False).create_message_received(data)
        print("message_created",message_created)
        end_time= datetime.now()
        print("total_time=",(end_time-start_time))
            # if data["data"]["body"]:
        print(valid_response(status=200,data="ok"))

        return {
            "status":200,"data":"ok"}

        # except Exception as e:
            # print("exception is",e)

        # return valid_response(status=200)
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

def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    data = {"count": len(data) if not isinstance(data, str) else 1, "data": data}

    return werkzeug.wrappers.Response(
        status=status, content_type="application/json; charset=utf-8", response=json.dumps(data),
    )
