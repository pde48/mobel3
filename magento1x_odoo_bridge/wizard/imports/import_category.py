# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from  xmlrpc.client import Error
import logging
import itertools
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.addons.magento1x_odoo_bridge.tools.const import CHANNELDOMAIN


class ImportMagento1xCategories(models.TransientModel):
    _inherit = ['import.categories']

    def magento1x_extract_categ_data(self, data, channel_id):
        parent_id = data.get('parent_id')
        return [(
            data.get('category_id'),
            dict(
            channel_id=channel_id,
            name=data.get('name'),
            store_id=data.get('category_id'),
            parent_id=parent_id not in ['0',0,None,False] and parent_id
            )
        )]
    def magento1x_get_product_categ_data(self, data, channel_id):
        res=[]
        child =len(data.get('children'))
        index = 0
        while len(data.get('children'))>0:
            item = data.get('children')[index]
            res += self.magento1x_get_product_categ_data(item, channel_id)
            res += self.magento1x_extract_categ_data(data.get('children').pop(index), channel_id.id)
        return res
    
    def _magento1x_import_categories(self, channel_id, res, kwargs):
        message=''
        res.pop('message')
        fetch_res = channel_id._fetch_magento1x_categories(**res)
        categories = fetch_res.get('data', {})
        message += fetch_res.get('message','')
        if not categories:
            message+="Category data not received."
        else:
            categ_items=dict(self.magento1x_get_product_categ_data(categories, channel_id)+self.magento1x_extract_categ_data(categories, channel_id.id))
            return list(categ_items.values())
        #add message in kwargs
        return False

