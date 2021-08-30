# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.addons.magento1x_odoo_bridge.tools.const import CHANNELDOMAIN
from odoo.addons.odoo_multi_channel_sale.tools import ensure_string as ES



class ImportMagento1xpartners(models.TransientModel):
    _inherit = ['import.partners']

    @staticmethod
    def _get_magento1x_customer_address_vals(data, customer_id, channel_id):
        res=[]
        for item in data:
            name = item.get('firstname')
            if item.get('lastname'):
                name+=' %s'%(item.get('lastname'))
            _type = 'invoice'
            if item.get('is_default_shipping'):
                _type = 'delivery'
            store_id = channel_id.get_magento1x_address_hash(item)
            vals= dict(
                channel_id=channel_id.id,
                name=name,
                email=item.get('email'),
                street=item.get('street'),
                phone=item.get('telephone'),
                city=item.get('city'),
                state_name=item.get('region'),
                country_id=item.get('country_id'),
                zip=item.get('postcode'),
                store_id=store_id,
                parent_id = customer_id,
                type=_type
            )
            res+=[vals]
        return res

    @classmethod
    def _magento1x_manage_address(cls, channel_id, customer_id, res):
        res_address = channel_id._fetch_magento1x_customer_address(customer_id=customer_id,**res)
        data = res_address.get('data')
        if data:
            add_vals=cls._get_magento1x_customer_address_vals(data, customer_id, channel_id)
            return add_vals
        return False

    @classmethod
    def _magento1x_import_customer(cls, channel_id, customer_id, customer_data, res, kwargs):
        name = customer_data.get('firstname')
        if customer_data.get('lastname'):
            name+=' %s'%(customer_data.get('lastname'))
        vals = dict(
            channel_id=channel_id.id,
            name=name,
            store_id=customer_data.get('customer_id'),
            email=customer_data.get('email'),
            mobile=customer_data.get('telephone')
        )
        address = cls._magento1x_manage_address(channel_id, customer_id, res)
        if address:
            vals['contacts'] = address
        return vals


    def _magento1x_import_partners(self, channel_id, res, kwargs):
        message=''
        debug = channel_id.debug=='enable'
        if channel_id.is_child_store:
            default_store_id = channel_id.default_store_id
            if not default_store_id:
                message+='No default channel set in configurable .'
        if not kwargs.get("filter_on"):
            if channel_id.import_customer_date and channel_id.update_customer_date:
                kwargs.update(
                    filter_on="date_range",
                    start_date=channel_id.import_customer_date,
                    end_date=channel_id.update_customer_date
                )
        fetch_res = channel_id._fetch_magento1x_partners(**res,**kwargs)
        partners = fetch_res.get('data') or []
        message += fetch_res.pop('message','')
        if not(partners and len(partners)):
            message+="Partners data not received."
        else:
            import_res_list = list()
            for item in partners:
                customer_id = item.get('customer_id')
                import_res =   self._magento1x_import_customer(
                channel_id, customer_id, item, res, kwargs)
                import_res_list.append(import_res)
            return import_res_list
        #add message in kwargs
        return False

