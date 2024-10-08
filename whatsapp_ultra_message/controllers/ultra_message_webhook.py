# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
class WhatsappUltraMessage(http.Controller):
    @http.route('/view/chat/<int:id>', auth='user',method=["GET"],type='http',csrf=False)
    def handling_receiving_message(self, **kw):
        print("kw:",kw)
        try:
            # data = json.loads(request.httprequest.data)
            # print(data)
        #     todo add secruity:
            partner=request.env['res.partner'].sudo().search([('id','=',kw['id'])])
            print("partner",partner)
            print(partner.whatsapp_message_ids.sorted('sent_datetime').read())
        except Exception as e:
            print("exception is",e)
        else:
            values={
                "chats":partner.whatsapp_message_ids.sorted('sent_datetime')
            }

            print("herrrr")
            return request.render("whatsapp_ultra_message.whatsapp_chat",values)
        # finally:
        #     return "hello Youssef"
