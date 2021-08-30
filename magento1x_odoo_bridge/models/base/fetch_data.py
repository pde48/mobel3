# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import models, api, _
from odoo.addons.magento1x_odoo_bridge.tools.const import InfoFields
MageDateTimeFomat = '%Y-%m-%d %H:%M:%S'

class MultiChannelSale(models.Model):
    _inherit = 'multi.channel.sale'

    def _fetch_magento1x_product_attributes(self, session, client, set_id=None, attribute_id=None):
        message, data, args ='', None, []
        if set_id:args += [set_id]
        elif attribute_id:args += [attribute_id]
        try:
            if set_id:
                data = client.call(session, 'product_attribute.list',args)
            elif attribute_id:
                data= client.call(session, 'product_attribute.info',args)
        except Error as e:
            e =str(e).strip('<').strip('>')
            message+='<br/>%s'%(e)
        except Exception as e:
            message+='<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    def _fetch_magento1x_product_attributes_sets(self, session, client):
        message, data, args ='', None, []
        try:
            data = client.call(session, 'product_attribute_set.list',args)
        except Error as e:
            e =str(e).strip('<').strip('>')
            message+='<br/>%s'%(e)
        except Exception as e:
            message+='<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    
    def _fetch_magento1x_orders(self, client, session, **kwargs):
        result = dict(
            data=None,
            message=''
        )
        message, data, args ='', None, {}
        channel_id = kwargs.get('channel_id')
        if channel_id:
            if channel_id.is_child_store:
                pass
            args['store_id'] = channel_id.get_magento1x_store_id()
        args =  self.get_magento1x_filters(kwargs)     
        try:
            data =  client.call(session, 'order.list', [args])
        except Error as e:
            e = str(e).strip('>').strip('<')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    @staticmethod
    def _fetch_magento1x_order_data(client, session, increment_id, **kwargs):
        message, data = '', None
        try:
            data=  client.call(
                session,
                'order.info',
                [increment_id]
            )
        except Error as e:
            e =str(e).strip('>').strip('<')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    
    def _fetch_magento1x_partners(self, client, session, source='all', **kwargs):
        result = dict(
            data=None,
            message=''
        )
        message, data, args ='', None, {}
        if not source=='all':
            partner_ids = list(set(kwargs.get('partner_ids','').split(',')))
            args['customer_id'] ={'in':list(partner_ids)}
        else:
            channel_id = kwargs.get('channel_id')
            if channel_id:
                if channel_id.is_child_store:
                    pass
        args =  self.get_magento1x_filters(kwargs)
 
        try:
            data=  client.call(session, 'customer.list',[args])
        except Error as e:
            e =str(e).strip('>').strip('<')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    @staticmethod
    def _fetch_magento1x_customer_address(client, session, customer_id, **kwargs):
        message, data = '', None
        try:
            data=  client.call(
                session,
                'customer_address.list',
                [customer_id]
            )
        except Error as e:
            e =str(e).strip('<').strip('>')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    
    def _fetch_magento1x_products(self, client,session,**kwargs):
        result = dict(
            data=None,
            message=''
        )
        message, data, args = '', None, {}
        if kwargs.get('product_tmpl_ids'):
            product_ids  = list(set(kwargs.get('product_tmpl_ids').split(',')))
            args['product_id'] ={kwargs.get('condition_type'):list(product_ids)}
        else:
            args =  self.get_magento1x_filters(kwargs)
        args['type'] = {'neq':'configurable'}
        channel_id = kwargs.get('channel_id')
        store_code = channel_id.store_code
        try:
            data = client.call(session, 'product.list',[args,store_code])
        except Error as e:
            e =str(e).strip('>').strip('<')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        result['data'] = data
        result['message'] = message
        return result

    @staticmethod
    def _fetch_magento1x_product_media(client,session,product_id,**kwargs):
        message=''
        data= dict()
        try:
            data['media']=client.call(session, 'product_media.list',[product_id])
        except Error as e:
            e =str(e).strip('>').strip('<')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    @classmethod
    def _fetch_magento1x_product_data(cls,client,session,product_id,channel_id,**kwargs):
        message=''
        data= dict()
        store_code = channel_id.store_code
        try:
            data=  client.call(
                session,
                'product.info',
                [product_id ,store_code, InfoFields]
            )
            media_res = cls._fetch_magento1x_product_media(client=client,session=session,product_id=product_id)
            media = media_res.get('data')
            if media:
                data['media']=media#client.call(session, 'product_media.list',[product_id])
        except Error as e:
            e =str(e).strip('>').strip('<')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    def _fetch_magento1x_categories(self, session, client, source='all', store_category_id=None):
        message=''
        data= None
        args = []
        if source=='all' and store_category_id:
            args+=[store_category_id]
        try:
            data = client.call(session, 'category.tree',args)
        except Error as e:
            e =str(e).strip('<').strip('>')
            message+='<br/>%s'%(e)
        except Exception as e:
            message+='<br/>%s'%(e)
        return dict(
            data=data,
            message=message
        )

    @staticmethod
    def _fetch_magento1x_qty_data(client,session,product_ids,**kwargs):
        message=''
        data_list= []
        try:
            data_list=  client.call(
                session,
                'product_stock.list',
                [product_ids]
            )
        except Error as e:
            e =str(e).strip('>').strip('<')
            message += '<br/>%s'%(e)
        except Exception as e:
            message += '<br/>%s'%(e)
        data=dict(map(lambda item:(item.get('product_id'),item.get('qty')),data_list))
        return data
