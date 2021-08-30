# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)


class response_object:
    def __init__(self, model_name, template_id, variant_ids, default_code, flag=True):
        if model_name == 'product.template':
            self.id = template_id 
            variants = []
            if flag:
                self.default_code = default_code
                for i in variant_ids:
                    variants.append(response_object(model_name, i, False, False, False))
            self.variants = variants


    @api.model
    def default_get(self,fields):
        res = super(MagentoAttributesSet,self).default_get(fields)
        if self._context.get('wk_channel_id'):
            res['channel_id']=self._context.get('wk_channel_id')
        return res

class MultiChannelSale(models.Model):
    _inherit = 'multi.channel.sale'

    def export_magento1x(self, exp_obj, **kwargs):
        result = None,None
        debug = self.debug == 'enable'
        res = self.get_magento1x_session()
        session = res.get('session')
        if not session:
            return result
        model_name = exp_obj._name

        if model_name == "product.category":
            result = self.env['export.categories'].magento1x_post_categories_data(self, exp_obj, "export", res, kwargs)
        
        elif model_name == 'product.template':
            res = self.env['export.templates'].with_context(base_operation='export').magento1x_post_products_data(self, exp_obj, **res)
            store_template_id = res.get('create_ids',{}).get('template_id') if res.get('create_ids') else False
            store_variants_id = res.get('create_ids',{}).get('variant_ids') if res.get('create_ids')  else False #[1] if len(res.get('create_ids')) == 2 else res.get('create_ids')
            store_default_code = res.get('create_ids',{}).get('default_code') if res.get('create_ids')  else False

            if store_template_id and store_variants_id:
                result = True,response_object(model_name, store_template_id, store_variants_id, store_default_code),
        if debug:
            _logger.debug('====EXPORT RESULT==========%r++++++++++++++++++++++',result)
        return result
