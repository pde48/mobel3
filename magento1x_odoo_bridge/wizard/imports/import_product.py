# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _
from odoo.addons.odoo_multi_channel_sale.tools import chunks, ensure_string as ES

OdooType = [
    ('simple','product'),
    ('downloadable','service'),
    ('grouped','service'),
    ('virtual','service'),
    ('bundle','service'),
]

class Importmagento1xProducts(models.TransientModel):
    _inherit = ['import.templates']

    @staticmethod
    def get_product_vals(channel_id, product_data, qty_available, res, kwargs):
        product_id = product_data.get('product_id')
        category_ids=product_data.get('category_ids',[])
        extra_categ_ids =','.join(category_ids)
        vals = dict(
            channel_id=channel_id.id,
            name=product_data.get('name'),
            default_code=product_data.get('sku'),
            variants=list(),
            type = dict(OdooType).get(product_data.get('type'),'service'),
            store_id=product_id,
            qty_available=qty_available,
            extra_categ_ids=extra_categ_ids,
        )
        res = channel_id._fetch_magento1x_product_data(product_id=product_id,channel_id=channel_id,**res)
        data = res.get('data')
        if data:
            vals['name'] = data.get('name')
            vals['description_sale'] =data.get('description')
            vals['weight'] =data.get('weight')
            vals['list_price'] =data.get('price')
            vals['standard_price'] =data.get('cost')
            media = data.get('media',{})
            if len(media.get('media',[])):
                res_img= channel_id._magento1x_get_product_images_vals(media)
                vals['image'] = res_img.get('image') #this will be uncommented
                vals['image_url'] = res_img.get('image_url')
        return vals

    def _magento1x_create_product_categories(self, channel_id, data, res, kwargs):
        category_ids= data.get('category_ids')
        mapping_obj = self.env['channel.category.mappings']
        domain = [('store_category_id', 'in', category_ids)]
        mapped = channel_id._match_mapping(mapping_obj,domain).mapped('store_category_id')
        category_ids=list(set(category_ids)-set(mapped))
        if len(category_ids):
            message='For product category imported %s'%(category_ids)
            try:
                import_category_obj = self.env['import.categories']
                category_data = import_category_obj._magento1x_import_categories(channel_id, res, kwargs)
                s_ids,e_ids,feeds = self.env['category.feed'].with_context(
                                channel_id=channel_id
                            )._create_feeds(categ_import_res)
                if feeds and channel_id.auto_evaluate_feed:
                    mapping_ids = feeds.with_context(get_mapping_ids=True).import_items()
                #create ande evaluate category feeds.
            except Exception as e:
                message = "Error while  order product import %s"%(e)

    def _magento1x_import_product(self, channel_id, product_id, data, qty_available, res, kwargs):
        self._magento1x_create_product_categories(channel_id, data, res, kwargs)
        vals =self.get_product_vals(
            channel_id=channel_id,product_data=data,
            qty_available=qty_available, res=res, kwargs=kwargs
        )
        return vals


    def _get_mage1x_qty_data(self,channel_id,items,res,kwargs):
        store_product_ids =[ str(item.get('product_id')) for item in items]
        operation = self.operation
        match_store_product_ids = []
        product_ids = []
        if operation=='import':
            domain= [('store_product_id','in',store_product_ids)]
            match_store_product_ids = channel_id.match_product_mappings(domain=domain,limit=None).mapped('store_product_id')
            if len(match_store_product_ids):
                store_product_ids = set(store_product_ids)-set(match_store_product_ids)
        else:
            domain= [('store_product_id','not in',store_product_ids)]
            match_store_product_ids = channel_id.match_product_mappings(domain=domain,limit=None).mapped('store_product_id')
            if len(match_store_product_ids):
                store_product_ids = set(store_product_ids)-set(match_store_product_ids)
        qty_data = channel_id._fetch_magento1x_qty_data(product_ids=list(set(store_product_ids)),**res)
        return qty_data


    def _get_magento1x_import_products(self, channel_id, res, kwargs):
        message=''
        store_product_ids = ''
        if kwargs.get('product_tmpl_ids'):
            store_product_ids = kwargs.pop('product_tmpl_ids')
        condition_type = 'nin' 
        if self._context.get('condition_type'):
            condition_type = self._context.get('condition_type')
        if not store_product_ids:
            match = channel_id.match_product_mappings(limit=None)
            if match:
                store_product_ids =','.join(map(str,match.mapped('store_product_id')))
        if not kwargs.get("filter_on"):
            if channel_id.import_product_date and channel_id.update_product_date:
                kwargs.update(
                    filter_on="date_range",
                    start_date=channel_id.import_product_date,
                    end_date=channel_id.update_product_date
                )
        fetch_res = channel_id._fetch_magento1x_products(
            res.get('client'),
            res.get('session'),
            product_tmpl_ids=store_product_ids,
            condition_type = condition_type,
            channel_id=channel_id,
            **kwargs
        )
        items = fetch_res.get('data') or []
        if not items:
            message+=fetch_res.get('message')
        return dict(item_ids=items,message=message)

    def _magento1x_import_products(self, channel_id, res, kwargs):
        message =''
        condition_type = 'in'
        products = list()
        debug = channel_id.debug=='enable'        
        product_ids_res = self._get_magento1x_import_products(channel_id, res, kwargs)
        item_ids = product_ids_res.get('item_ids')
        message+=product_ids_res.get('message')
        if len(item_ids):
            qty_data = self._get_mage1x_qty_data(channel_id, item_ids, res, kwargs)
            for item in item_ids:
                product_id = item.get('product_id')
                qty_available =qty_data.get(product_id)
                import_res =   self._magento1x_import_product(
                    channel_id=channel_id,  product_id=product_id, data=item,
                    qty_available=qty_available,res=res,kwargs=kwargs
                )
                products.append(import_res)
            return products
        #add message in kwargs here
        return False
