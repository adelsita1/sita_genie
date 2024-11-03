# -*- coding: utf-8 -*-
from odoo import http
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request
import json
class WhatsappUltraMessage(http.Controller):
    @http.route('/view/chat/<int:id>', auth='user',methods=["GET"],type='http',csrf=False)
    def handling_receiving_message(self, **kw):

        try:
            partner=request.env['res.partner'].sudo().search([('id','=',kw['id'])])
            chats=partner.whatsapp_message_ids.filtered(lambda m:m.status!='queue').sorted('sent_datetime')

        except Exception as e:
            _logger.info("except in render message %s",e)

        else:
            values={
                "chats":chats,
            }


            return request.render("whatsapp_ultra_message.whatsapp_chat",values)

