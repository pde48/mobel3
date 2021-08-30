# -*- coding: utf-8 -*-
# from odoo import http


# class Mobel(http.Controller):
#     @http.route('/mobel/mobel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mobel/mobel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mobel.listing', {
#             'root': '/mobel/mobel',
#             'objects': http.request.env['mobel.mobel'].search([]),
#         })

#     @http.route('/mobel/mobel/objects/<model("mobel.mobel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mobel.object', {
#             'object': obj
#         })
