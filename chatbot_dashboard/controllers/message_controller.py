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

        partners=request.env['res.partner'].sudo()
        total_agents=partners.search_count([("is_life_agent","=",True)])
        free_agents=partners.search_count([("is_life_agent","=",True),("life_agent_state","=","free")])




        values={
            'total_message_sent':message_sent,
            'total_message_received': message_receive,
            'message_sent_ids':message_sent_ids.mapped("id"),
            'message_received_ids':message_receive_ids.mapped("id"),
            'faqs':faqs.mapped("id"),
            'total_faq':len(faqs),
            "total_agents":total_agents,
            "free_agents":free_agents,


        }
        # todo add agents ids
        # todo add questions answered by ai/live agents
        # todo add crm leads
        # todo rates table




        return values
