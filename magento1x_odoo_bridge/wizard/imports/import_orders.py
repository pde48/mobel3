# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.exceptions import UserError,RedirectWarning, ValidationError
from odoo.addons.odoo_multi_channel_sale.tools import chunks, ensure_string as ES
from odoo.addons.magento1x_odoo_bridge.tools.const import CHANNELDOMAIN
OrderStatus = [
    ('all','All'),
    ('canceled','Canceled'),
    ('closed','Closed'),
    ('complete','Complete'),
    ('processing','Processing'),
    ('holded','On Hold'),
    ('pending','Pending'),
    ('pending_payment','Pending Payment'),
]

class ImportOrders(models.TransientModel):
    _inherit = ['import.orders']

    def import_products(self,product_tmpl_ids,channel_id, res, kwargs):
        product_tmpl_ids =[str(pt) for pt in product_tmpl_ids]
        mapping_obj = self.env['channel.product.mappings']
        domain = [('store_product_id', 'in',product_tmpl_ids)]
        mapped = channel_id._match_mapping(mapping_obj,domain).mapped('store_product_id')
        product_tmpl_ids=list(set(product_tmpl_ids)-set(mapped))
        if len(product_tmpl_ids):
            feed_domain = [('store_id', 'in',product_tmpl_ids)]
            product_feeds = channel_id.match_product_feeds(domain=feed_domain,limit=0).mapped('store_id')
            product_tmpl_ids=list(set(product_tmpl_ids)-set(product_feeds))
            if len(product_tmpl_ids):
                feed_domain = [('store_id', 'in',product_tmpl_ids)]
                product_variant_feeds = channel_id.match_product_variant_feeds(domain=feed_domain,limit=0).mapped('store_id')
                product_tmpl_ids=list(set(product_tmpl_ids)-set(product_variant_feeds))
        message=''
        if len(product_tmpl_ids):
            message='For order product imported %s'%(product_tmpl_ids)
            import_product_obj=self.env['import.templates']
            product_tmpl_ids=','.join(product_tmpl_ids)
            context = dict(self._context)
            context['condition_type']= 'in'
            context['get_date']= False
            kwargs.update(
                product_tmpl_ids=product_tmpl_ids
            )

            product_feeds = import_product_obj.with_context(context)._magento1x_import_products(channel_id, res, kwargs)
            if product_feeds:
                s_ids,e_ids,feeds = self.env['product.feed'].with_context(
                                    channel_id=channel_id
                                )._create_feeds(product_feeds)

                if s_ids and not e_ids:
                    self._cr.commit()
                    if channel_id.auto_evaluate_feed:
                        mapping_ids = feeds.with_context(get_mapping_ids=True).import_items()
                        #add message for creating product
        return message

    @staticmethod
    def update_shipping_info(order_items,order_data,price):
        name = 'Mangeto %s'%(order_data.get('shipping_method'))
        order_items+=[dict(
            product_id=name,
            price=price,
            qty_ordered=1,
            name=name,
            line_source ='delivery',
            description=name,
            tax_amount ='0',
        )]
        return order_items

    @staticmethod
    def get_discount_line_info(price):
        name = '%s discount'%(price)
        return dict(
            product_id=name,
            price='%s'%(abs(float(price))),
            qty_ordered=1,
            name=name,
            line_source ='discount',
            description=name,
            tax_amount ='0',
        )
    @staticmethod
    def magento1x_get_tax_line(item,channel_id):
        tax_percent = float(item.get('tax_percent'))
        tax_type = 'percent'
        name = 'Tax {} % '.format(tax_percent)
        return {
            'rate':tax_percent,
            'name':name,
            'include_in_price':channel_id.default_tax_type== 'include'and True or False,
            'tax_type':tax_type
        }

    @staticmethod
    def magento1x_get_order_line_info(order_item,channel_id):
        line_price_unit = order_item.get('price')
        line_product_default_code = order_item.get('sku')
        if order_item.get('line_source') not in ['discount','delivery']:
            if channel_id.default_tax_type=='include'  :
                line_price_unit =  order_item.get('price_incl_tax') and order_item.get('price_incl_tax') or order_item.get('price')

        line=dict(
            line_product_uom_qty = order_item.get('qty_ordered'),
            line_product_id =order_item.get('product_id'),
            line_product_default_code=line_product_default_code,
            line_name = order_item.get('name'),
            line_price_unit=line_price_unit ,
            line_source = order_item.get('line_source','product'),
        )
        return line

    @staticmethod
    def manage_configurable_items(items):
        nitems = dict([(i.get('item_id'),i) for i in items])

        for k,v in nitems.items():
            if v.get('parent_item_id'):
                parent_id = nitems.get(v.get('parent_item_id'))
                v['price_incl_tax'] = parent_id.get('price_incl_tax')
                v['price'] = parent_id.get('price')
                v['tax_percent'] = parent_id.get('tax_percent')
                v['discount_amount'] = parent_id.get('discount_amount')
        return list(filter(lambda i:i.get('product_type')!='configurable',nitems.values()))

    def magento1x_get_order_line(self, order_id, carrier_id, order_data, channel_id, res, kwargs):
        data=dict()
        order_items=order_data.get('items')
        order_items = self.manage_configurable_items(order_items)
        message=''
        default_tax_type = channel_id.default_tax_type
        lines=[]
        lines += [(5,0,0)]
        if order_items:
            product_tmpl_ids = list(set(map(lambda item:item.get('product_id'),order_items)))
            message+=self.import_products(product_tmpl_ids=product_tmpl_ids,channel_id=channel_id, res=res, kwargs=kwargs) # this is essential and need to be include 

            shipping_amount = default_tax_type== 'include' and  order_data.get('shipping_amount') or  order_data.get('shipping_incl_tax')
            shipping_amount= order_data.get('shipping_incl_tax')

            if carrier_id and float(shipping_amount):
                order_items= self.update_shipping_info(
                    order_items,order_data,shipping_amount
                )
            if default_tax_type== 'include':
                discount_amount=order_data.get('discount_amount')
                if float(discount_amount):
                    order_items+= [self.get_discount_line_info(
                        discount_amount
                    )]
            size = len(order_items)
            if size==1:
                for order_item in order_items:
                    line=self.magento1x_get_order_line_info(order_item,channel_id)
                    if float(order_item.get('tax_percent','0.0')):
                        line['line_taxes'] = [self.magento1x_get_tax_line(order_item,channel_id)]
                    data.update(line)
            else:
                data['line_type'] ='multi'
                for order_item in order_items:
                    line=self.magento1x_get_order_line_info(order_item,channel_id)

                    if float(order_item.get('tax_percent','0.0')):
                        line['line_taxes'] = [self.magento1x_get_tax_line(order_item,channel_id)]
                    lines += [(0, 0, line)]
                    if default_tax_type!= 'include':
                        discount_amount = float(order_item.get('discount_amount','0'))
                        if discount_amount:
                            discount_data = self.get_discount_line_info(discount_amount)
                            discount_line=self.magento1x_get_order_line_info(discount_data,channel_id)
                            if float(order_item.get('tax_percent','0.0')):
                                discount_data['tax_percent'] = order_item.get('tax_percent','0.0')
                                discount_line['line_taxes'] = [self.magento1x_get_tax_line(discount_data,channel_id)]
                            lines += [(0, 0, discount_line)]

        data['line_ids'] = lines
        return dict(
            data=data,
            message=message
            )
    @staticmethod
    def get_mage_invoice_address(item,customer_email):
        name = item.get('firstname')
        if item.get('lastname'):
            name+=' %s'%(item.get('lastname'))
        email = item.get('email') or customer_email
        return dict(
            invoice_name=name,
            invoice_email=email,
            invoice_street=item.get('street'),
            invoice_phone=item.get('telephone'),
            invoice_city=item.get('city'),
            invoice_country_id=item.get('country_id'),
            invoice_zip=item.get('postcode'),
            invoice_partner_id=item.get('customer_address_id') or '0',
            invoice_state_name=item.get('region'),
        )
    @staticmethod
    def get_mage_shipping_address(item,customer_email):
        name = item.get('firstname')
        if item.get('firstname'):
            name+=' %s'%(item.get('lastname'))
        email = item.get('email') or customer_email

        return dict(
            shipping_name=name,
            shipping_email=email,
            shipping_street=item.get('street'),
            shipping_phone=item.get('telephone'),
            shipping_city=item.get('city'),
            shipping_country_id=item.get('country_id'),
            shipping_zip=item.get('postcode'),
            shipping_partner_id=item.get('customer_address_id') or '0',
            invoice_state_name=item.get('region'),
        )
    def get_order_vals(self, channel_id, increment_id, order_item_data, status, res, kwargs):
        message = ''
        pricelist_id = channel_id.pricelist_name
        item = order_item_data
        customer_name = item.get('customer_firstname')
        if item.get('customer_lastname'):
            customer_name+=" %s"%(item.get('customer_lastname'))
        customer_email=item.get('customer_email')

        vals = dict(
            channel_id=channel_id.id,
            order_state = status,
            name = increment_id,
            store_id = increment_id,
            partner_id=item.get('customer_id') or '0' ,
            customer_is_guest = int(item.get('customer_is_guest')),
            currency = item.get('order_currency_code'),
            customer_name=customer_name,
            customer_email=customer_email,
            payment_method = item.get('payment').get('method'),
        )
        created_at = item.get('created_at')
        if created_at:
            vals['date_order'] = created_at
            vals['confirmation_date'] = created_at
        shipping_method = item.get('shipping_method')
        vals['carrier_id']= shipping_method#shipping_mapping_id.shipping_service_id
        line_res= self.magento1x_get_order_line(
            increment_id,
            shipping_method,item,channel_id,res,kwargs
        ) #shipping_mapping_id.odoo_shipping_carrier
        if line_res.get('data'):
            vals.update(line_res.get('data'))

        billing_address=item.get('billing_address') or {}
        shipping_address = item.get('shipping_address')
        billing_hash = channel_id.get_magento1x_address_hash(billing_address)
        shipping_hash = channel_id.get_magento1x_address_hash(shipping_address or {})
        same_shipping_billing = billing_hash==shipping_hash
        vals['same_shipping_billing'] =same_shipping_billing
        billing_address['customer_address_id'] = billing_hash
        billing_addr_vals = self.get_mage_invoice_address(billing_address,customer_email)
        vals.update(billing_addr_vals)
        if shipping_address and not(same_shipping_billing):
            shipping_add_vals = self.get_mage_shipping_address(shipping_address,customer_email)
            shipping_add_vals['shipping_partner_id'] = shipping_hash
            vals.update(shipping_add_vals)

        return vals


    def _magento1x_import_order(self, channel_id, order_item_data, entity_id, increment_id, status, res, kwargs):
        vals =self.get_order_vals(
            channel_id, increment_id, order_item_data=order_item_data, status=status, res=res, kwargs=kwargs
        )
        return vals
 

    def _get_magento1x_import_orders(self, channel_id, res, kwargs):
        message=''
        order_ids = channel_id.match_order_mappings(limit=None).mapped('store_order_id')
        if not kwargs.get("filter_on"):
            if channel_id.import_order_date and channel_id.update_order_date:
                kwargs.update(
                    filter_on="date_range",
                    start_date=channel_id.import_product_date,
                    end_date=channel_id.update_product_date
                )

        fetch_res = channel_id._fetch_magento1x_orders(
            res.get('client'),
            res.get('session'),
            channel_id=channel_id,
            order_ids = order_ids,
            condition_type = kwargs.get('condition_type') or 'nin',
            **kwargs
        )
        items = fetch_res.get('data') or []
        message+= fetch_res.get('message','')
        if not items:
            message+="Orders data not received."
        return dict(item_ids=items,message=message)


    def _magento1x_import_orders_status(self, channel_id, **kwargs):
        update_ids=[]
        message = ''
        store_id = channel_id.get_magento1x_store_id()
        order_state_ids = channel_id.order_state_ids
        default_order_state = order_state_ids.filtered('default_order_state')
        store_order_ids = channel_id.match_order_mappings(limit=None).mapped('store_order_id')
        if not store_order_ids:
            message += 'No order mapping exits'
        else:
            for order_ids in chunks(store_order_ids,self.api_record_limit):
                fetch_res =channel_id._fetch_magento1x_orders(
                    channel_id=channel_id,
                    condition_type = 'in',
                    order_ids = order_ids,
                    **kwargs
                )
                items = fetch_res.get('data', {})
                message+= fetch_res.get('message','')
                for item in items:
                    if store_id!=item.get('store_id'):continue

                    increment_id = item.get('increment_id')
                    order_item_data = channel_id._fetch_magento1x_order_data(increment_id=increment_id,**kwargs).get('data')
                    payment_method = order_item_data.get('payment',{}).get('method')
                    res = channel_id.set_order_by_status(
                        channel_id= channel_id,
                        store_id = increment_id,
                        status = item.get('status'),
                        order_state_ids = order_state_ids,
                        default_order_state = default_order_state,
                        payment_method = payment_method
                    )
                    order_match = res.get('order_match')
                    if order_match:update_ids +=[order_match]
                self._cr.commit()
        time_now = fields.Datetime.now()
        all_imported , all_updated = 1,1
        if all_updated and len(update_ids):
            channel_id.update_order_date = time_now
        if not channel_id.import_order_date:
            channel_id.import_order_date = time_now
        if not channel_id.update_order_date:
            channel_id.update_order_date = time_now
        return dict(
            update_ids=update_ids,
        )


    def _magento1x_import_orders(self, channel_id, res, kwargs):
        message = ''
        error_count = 0
        orders = list()
        debug = channel_id.debug=='enable'
        store_id = channel_id.get_magento1x_store_id()
        
        order_ids_res = self._get_magento1x_import_orders(channel_id, res, kwargs)
        item_ids = order_ids_res.get('item_ids')
        message+=order_ids_res.get('message')
        if len(item_ids):
            for item in item_ids:
                if store_id!=item.get('store_id'):continue
                increment_id = item.get('increment_id')
                entity_id = item.get('order_id')
                status = item.get('status')
                order_item_data = channel_id._fetch_magento1x_order_data(increment_id=increment_id,**res).get('data')
                import_res =   self._magento1x_import_order(
                    channel_id=channel_id, order_item_data=order_item_data, entity_id=entity_id,increment_id=increment_id,
                    status=status, res=res, kwargs=kwargs
                )
                orders.append(import_res)
            return orders
        #add message in kwargs
        return False
        
