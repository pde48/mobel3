# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

MageDateTimeFomat = '%Y-%m-%d %H:%M:%S'
from odoo import models, api
import  xmlrpc.client
from  xmlrpc.client import Error
from odoo.addons.odoo_multi_channel_sale.tools import get_hash_dict

class MultiChannelSale(models.Model):
    _inherit = 'multi.channel.sale'

    @api.model
    def get_magento1x_store_id(self):
        return eval(self.store_config).get('store_id')

    @api.model
    def get_magento1x_client(self):
        data_uri ='{base_uri}/index.php/api/xmlrpc/'.format(base_uri = self.url)
        client = xmlrpc.client.ServerProxy(data_uri)
        return client

    @api.model
    def get_magento1x_session(self):
        message = ''
        session = None
        client = None
        try:
            client = self.get_magento1x_client()
            session = client.login(
                self.email,
                self.api_key
            )
        except Error as e:
            e = str(e).strip('>').strip('<')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        return dict(
            session = session,
            client = client,
            message = message,
        )

    @api.model
    def get_channel(self):
        result = super(MultiChannelSale, self).get_channel()
        result.append(("magento1x", "Magento v1.9"))
        return result

    @api.model
    def get_info_urls(self):
        urls = super(MultiChannelSale,self).get_info_urls()
        urls.update(
            magento1x = {
                'blog' : 'https://webkul.com/blog/multi-channel-magento-1-x-odoo-bridgemulti-channel-mob',
                'store': 'https://store.webkul.com/Multi-Channel-Magento-1-x-Odoo-Bridge-Multi-Channel-MOB.html',
            },
        )
        return urls

    @staticmethod
    def get_magento1x_address_hash(itemvals):
        templ_add = {
            "city":itemvals.get("city"),
            "region_code":itemvals.get("region_code"),
            "firstname":itemvals.get("firstname"),
            "lastname":itemvals.get("lastname"),
            "region":itemvals.get("region"),
            "country_id":itemvals.get("country_id"),
            "telephone":itemvals.get("telephone"),
            "street":itemvals.get("street"),
            "postcode":itemvals.get("postcode"),
            # "customer_address_id":itemvals.get("customer_address_id") or itemvals.get('customer_id')
        }
        return get_hash_dict(templ_add)

    @staticmethod
    def get_magento1x_filters(kwargs):
        args = dict()
        filter_on = kwargs.get("filter_on")
        if kwargs.get('order_ids'):
            args['increment_id'] ={kwargs.get('condition_type'):kwargs.get('order_ids')}
        if filter_on == "date_range":
            if kwargs.get('start_data') or kwargs.get('end_date'):
                args['created_at'] = dict()
            if kwargs.get('start_date') and kwargs.get('end_date'):
                fromDate = kwargs.get('start_date').strftime(MageDateTimeFomat)
                toDate = kwargs.get('end_date').strftime(MageDateTimeFomat)
                args['created_at'].update(
                {'from':fromDate, 'to':toDate})
            else:
                if kwargs.get('start_date'):
                    fromDate = kwargs.get('start_date').strftime(MageDateTimeFomat)
                    args['created_at'].update(dict(gt=fromDate))
                if kwargs.get('end_date'):
                    toDate = kwargs.get('end_date').strftime(MageDateTimeFomat)
                    args['created_at'].update({'lt':toDate})
        elif filter_on == "id_range":
            if kwargs.get('start_id') or kwargs.get('end_id')  :
                args['entity_id'] = dict()
            if kwargs.get('start_id') and kwargs.get('end_id'):
                from_id = kwargs.get('start_id')
                to_id = kwargs.get('end_id')
                args['entity_id'].update(
                {'from':from_id, 'to':to_id})
        elif filter_on == "order_state":
            if kwargs.get('order_state'):
                args['status'] = "processing"
        return args
