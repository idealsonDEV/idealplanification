# -*- coding: utf-8 -*-
from openerp import http

# class Idealplanitication(http.Controller):
#     @http.route('/idealplanitication/idealplanitication/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/idealplanitication/idealplanitication/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('idealplanitication.listing', {
#             'root': '/idealplanitication/idealplanitication',
#             'objects': http.request.env['idealplanitication.idealplanitication'].search([]),
#         })

#     @http.route('/idealplanitication/idealplanitication/objects/<model("idealplanitication.idealplanitication"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('idealplanitication.object', {
#             'object': obj
#         })