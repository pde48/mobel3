# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    url_product = fields.Char(string='Url',copy=False,)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
 
    @api.depends('product_variant_ids.url_product')
    def _compute_url_product(self):
        self.url_product = False
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.url_product = template.product_variant_ids.url_product

    def _set_url_product(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.url_product = self.url_product


    def _search_url_product(self, operator, value):
        templates = self.with_context(active_test=False).search([('product_variant_ids.url_product', operator, value)])
        return [('id', 'in', templates.ids)]


    url_product = fields.Char('Url', compute='_compute_url_product', inverse='_set_url_product',search='_search_url_product')




    #url_product = fields.Char(string='Url',
    #    related="product_variant_ids.url_product", readonly=False
    #)