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


        message_obj = request.env['whatsapp_message_log'].sudo()

        message_sent=message_obj.search_count([("direction", "=", 'sent')])
        message_sent_ids=message_obj.search([("direction", "=", 'sent')])

        message_receive=message_obj.search_count([("direction", "=", 'received')])
        message_receive_ids=message_obj.search([("direction", "=", 'received')])

        faqs=request.env['question_answer'].sudo().search([])



        values={
            'total_message_sent':message_sent,
            'total_message_received': message_receive,
            'message_sent_ids':message_sent_ids.mapped("id"),
            'message_received_ids':message_receive_ids.mapped("id"),
            'faq':faqs.mapped("id"),
            'total_faq':len(faqs),

        }


        return values
