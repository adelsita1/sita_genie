# -*- coding: utf-8 -*-
# from odoo import http


# class ChatbotDashboard(http.Controller):
#     @http.route('/chatbot_dashboard/chatbot_dashboard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/chatbot_dashboard/chatbot_dashboard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('chatbot_dashboard.listing', {
#             'root': '/chatbot_dashboard/chatbot_dashboard',
#             'objects': http.request.env['chatbot_dashboard.chatbot_dashboard'].search([]),
#         })

#     @http.route('/chatbot_dashboard/chatbot_dashboard/objects/<model("chatbot_dashboard.chatbot_dashboard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('chatbot_dashboard.object', {
#             'object': obj
#         })

