# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging

from odoo import api, fields, models, _
from odoo.addons.magento1x_odoo_bridge.tools.const import CHANNELDOMAIN

_logger = logging.getLogger(__name__)

class response_object:

    def __init__(self,rid):
        self.id = rid


class exportmagento1xcategories(models.TransientModel):
    _inherit = ['export.categories']

    @api.model
    def magento1x_get_category_data(self, category_id, channel_id,store_parent_id=None): #store_parent_id remove
        store_parent_id = 2
        if category_id.parent_id:
            store_parent_id = self.channel_id.match_category_mappings(
                odoo_category_id =category_id.parent_id.id
            ).store_category_id
        data = {
          "parent_id": int(store_parent_id),
          "name": category_id.name,
          "is_active": True,
          'include_in_menu':True,
          'available_sort_by':'position',
          'default_sort_by':'position'

        }
        return data


    @api.model
    def magento1x_create_category_data(self, category_id,  channel_id, res, kwargs):
        # mapping_obj = self.env['channel.category.mappings']
        result=dict(
            mapping_id=None,
            message=''
        )
        message=''
        store_parent_id = 2
        data_res = self.magento1x_get_category_data(
            category_id = category_id,
            channel_id = channel_id,
            store_parent_id=store_parent_id
        )
        categories_res = channel_id.magento1x_create_category(data=data_res,**res)
        if categories_res.get('message'):
            result['message']+=categories_res.get('message')
            return result
        else:
            store_id  = categories_res.get('obj_id')
            result['store_id'] = store_id
        return result

    @api.model
    def magento1x_update_category_data(self,channel_id,category_id, res, kwargs):
        result=dict(
            mapping_id=None,
            message=''
        )
        message=''
        match = self.channel_id.match_category_mappings(
            odoo_category_id =category_id.id
        )
        if not match:
            message+='Mapping not exits for category %s [%s].'%(category_id.name,category_id.id)
        else:
            data_res = self.magento1x_get_category_data(
                category_id = category_id,
                channel_id = channel_id,
            )
            data_res['store_id'] = match.store_category_id
            categories_res =channel_id.magento1x_update_category(data=data_res,**res)
            msz = categories_res.get('message','')
            if msz: message+='While Categories %s Export %s'%(data_res.get('name'),categories_res.get('message',''))
            # mapping_id=match
            # match.need_sync='no'
            if msz: result['message'] = msz
        result['store_id'] = match.store_category_id
        return result



    @api.model
    def magento1x_post_categories_data(self, channel_id, category_id, operation, res, kwargs):
        message = ''
        category_dict = dict()
        post_res = dict()
        if operation == 'export':
            post_res=self.magento1x_create_category_data(category_id,channel_id, res, kwargs)
        else:
            post_res=self.magento1x_update_category_data(channel_id,category_id, res, kwargs)
        sync_vals = dict(
                    status ='error',
                    action_on ='category',
                    action_type ='export',
                )
        if post_res.get('store_id'):
                sync_vals['status'] = 'success'
                sync_vals['ecomstore_refrence'] = post_res.get('store_id')
                sync_vals['odoo_id'] = category_id.id
                sync_vals['summary'] = post_res.get('message') or '%s %sed'%(category_id.name,operation)
                channel_id._create_sync(sync_vals)
        
        if post_res.get('message'):
            return False,False
        return True,response_object(post_res.get('store_id'))
