import json

from odoo import http
from odoo.http import request

# make controller for api to get the values of messages_sent
class MessageDashBoard(http.Controller):
    # this message is called from js so type will be json
    """
    when user click on the project dashboard menu, this method will be called
    return a dict of messageData
    """

    @http.route('/get/messages/data', type="json", auth="none")

    def fetch_messages(self):
        values = {}

        message_obj = request.env['whatsapp_message_log'].sudo()

        message_sent=message_obj.search_count([("direction", "=", 'sent')])
        message_sent_ids=message_obj.search([("direction", "=", 'sent')])
        print("message_sent",message_sent)
        message_receive=message_obj.search_count([("direction", "=", 'received')])
        print("message_receive", message_receive)
        values={
            'total_message_sent':message_sent,
            'message_sent_ids':message_sent_ids.mapped("id"),
            'message_receive_count':message_receive,
        }
        print("values",values)

        # if message_sent:
        #     values['success'] = True
        #     values['return'] = "Something"
        # else:
        #     values['success'] = False
        #     values['error_code'] = 1
        #     values['error_data'] = 'No data found!'

        return values
