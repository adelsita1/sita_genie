# -*- coding: utf-8 -*-
# from odoo import http


# class AppOne(http.Controller):
#     @http.route('/app_one/app_one', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/app_one/app_one/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('app_one.listing', {
#             'root': '/app_one/app_one',
#             'objects': http.request.env['app_one.app_one'].search([]),
#         })

#     @http.route('/app_one/app_one/objects/<model("app_one.app_one"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('app_one.object', {
#             'object': obj
#         })

