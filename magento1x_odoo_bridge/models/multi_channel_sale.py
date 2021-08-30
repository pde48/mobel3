# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
import re
from datetime import date, datetime,timedelta
_logger = logging.getLogger(__name__)
from odoo.addons.magento1x_odoo_bridge.tools.const import InfoFields
from odoo.addons.odoo_multi_channel_sale.tools import extract_list as EL
from odoo import api,fields, models,_
from odoo.exceptions import UserError
Boolean = [
    ('1', 'True'),
    ('0', 'False'),
]
Visibility = [
    ('1', 'Not Visible Individually'),
    ('2', 'Catalog'),
    ('3', 'Catalog'),
    ('4', 'Catalog, Search'),

]
Type = [
    ('simple','Simple Product'),
    ('downloadable','Downloadable Product'),
    ('grouped','Grouped Product'),
    ('virtual','Virtual Product'),
    ('bundle','Bundle Product'),
]
ShortDescription = [
    ('same','Same As Product Description'),
    ('custom','Custom')
]


class MultiChannelSale(models.Model):
    _inherit = "multi.channel.sale"

    @api.model
    def match_category_mappings(self, store_category_id=None, odoo_category_id=None, domain=None, limit=1):
        if self.channel=='magento1x' and self.default_store_id:
            self = self.default_store_id
        return super(MultiChannelSale,self).match_category_mappings(store_category_id=store_category_id,odoo_category_id=odoo_category_id,domain=domain,limit=limit)

    @api.model
    def match_partner_mappings(self, store_id = None, _type='contact',domain=None, limit=1):
        if self.channel=='magento1x' and self.default_store_id:
            self = self.default_store_id
        return super(MultiChannelSale,self).match_partner_mappings(store_id=store_id,_type=_type,domain=domain,limit=limit)



    def test_magento1x_connection(self):
        for obj in self:
            state = 'error'
            message = ''
            res = obj.get_magento1x_session()
            session = res.get('session')
            if not session:
                message += '<br/>%s'%(res.get('message'))
            else:
                session = res.get('session')
                client = res.get('client')
                store_list=client.call(session, 'store.list')
                store_code = obj.store_code
                res_store = [store for store in store_list if int(store.get('store_id')) and store.get('code')==store_code ]
                if len(res_store):
                    state = 'validate'
                    message += '<br/> Credentials successfully validated.'
                    obj.store_config = res_store[0]
                else:
                    store_list = [store.get('code') for store in store_list  if int(store.get('store_id'))]
                    message += '<br/> Store <b>%s</b> not match in these stores %r.'%(store_code,store_list)
            obj.state = state
            if state != 'validate':
                message += '<br/> Error While Credentials  validation.'
        return self.display_message(message)

    store_code = fields.Char(
        string='Mage Store ID',
        default='default',
    )
    store_config = fields.Text(
        string='Mage Store Config'
    )
    default_product_set_id = fields.Many2one(
        comodel_name='magento.attributes.set',
        string='Default Attribute-Set',
        help='ID of the product attribute set'
    )

    @api.model
    def create(self, vals):
        base_uri = vals.get('url')
        if base_uri:
            vals['url'] = re.sub('/index.php', '', base_uri.strip(' ').strip('/'))
        return super(MultiChannelSale,self).create(vals)

    def write(self, vals):
        base_uri = vals.get('url')
        if base_uri:
            vals['url'] = re.sub('/index.php', '', base_uri.strip(' ').strip('/'))
        return super(MultiChannelSale,self).write(vals)


    @api.model
    def magento1x_post_do_transfer(self,picking_id,mapping_ids,result):
        debug = self.debug=='enable'
        if self.sync_shipment:
            sync_vals = dict(
                status ='error',
                action_on ='order',
                action_type ='export',
            )
            res =self.get_magento1x_session()
            session = res.get('session')
            client = res.get('client')
            if debug:
                _logger.debug("do_transfer #1 %r===%r="%(res,mapping_ids))
            if session:
                for mapping_id in mapping_ids:
                    message=''
                    comment,data='',None
                    sync_vals['ecomstore_refrence'] ='%s(%s)'%(mapping_id.store_order_id,mapping_id.store_id)

                    sync_vals['odoo_id'] = mapping_id.odoo_order_id
                    try:
                        comment = 'Create For Odoo Order %s , Picking %s'%( mapping_id.order_name.name,picking_id.name)
                        data=client.call(session, 'order_shipment.create',[mapping_id.store_order_id,[],comment])
                        sync_vals['status'] = 'success'

                        message   += 'Delivery created successfully '
                    except Error as e:
                        e =str(e).strip('<').strip('>')
                        message += '<br/>Error For  Order  %s  Shipment <br/>%s'%(mapping_id.store_order_id,str(e))
                    except Exception as e:
                        message += '<br/>Error For  Order  %s  Shipment <br/>%s'%(mapping_id.store_order_id,str(e))
                    sync_vals['summary'] = message
                    if debug:
                        _logger.debug("=do_transfer #2==%r=====%r==%r="%(comment,data,sync_vals))
                    mapping_id.channel_id._create_sync(sync_vals)

    @api.model
    def magento1x_post_confirm_paid(self,invoice_id,mapping_ids,result):
        debug = self.debug=='enable'
        if self.sync_invoice:
            sync_vals = dict(
                status ='error',
                action_on ='order',
                action_type ='export',
            )
            res =self.get_magento1x_session()
            session = res.get('session')
            client = res.get('client')
            if debug:
                _logger.debug("confirm_paid #1 %r===%r="%(res,mapping_ids))
            if session:
                for mapping_id in mapping_ids:
                    comment,data='',None
                    sync_vals['ecomstore_refrence'] ='%s(%s)'%(mapping_id.store_order_id,mapping_id.store_id)
                    sync_vals['odoo_id'] = mapping_id.odoo_order_id
                    message=''
                    try:
                        comment = 'Create For Odoo Order %s  Invoice %s'%( mapping_id.order_name.name,invoice_id.number)
                        data=client.call(session, 'order_invoice.create',[mapping_id.store_order_id,[],comment])
                        sync_vals['status'] = 'success'
                        message += 'Invoice created successfully '
                    except Error as e:
                        e =str(e).strip('<').strip('>')
                        message += '<br/>Error For  Order  %s  Invoice <br/>%s'%(mapping_id.store_order_id,str(e))
                    except Exception as e:
                        message += '<br/>Error For  Order  %s  Invoice <br/>%s'%(mapping_id.store_order_id,str(e))
                    sync_vals['summary'] = message
                    if debug:
                        _logger.debug("=do_transfer #2==%r=====%r==%r="%(comment,data,sync_vals))
                    mapping_id.channel_id._create_sync(sync_vals)
    @api.model
    def magento1x_post_cancel_order(self, order_id, mapping_ids, result):
        debug = self.debug=='enable'
        if self.sync_invoice:
            sync_vals = dict(
                status ='error',
                action_on ='order',
                action_type ='export',
            )
            res =self.get_magento1x_session()
            session = res.get('session')
            client = res.get('client')
            if debug:
                _logger.debug("confirm_cancel #1 %r===%r="%(res,mapping_ids))
            if session:
                for mapping_id in mapping_ids:
                    comment,data='',None
                    sync_vals['ecomstore_refrence'] ='%s(%s)'%(mapping_id.store_order_id,mapping_id.store_id)
                    sync_vals['odoo_id'] = mapping_id.odoo_order_id
                    message=''
                    try:
                        comment = 'Cancel For Odoo Order %s  Cancel %s'%( mapping_id.order_name.name,order_id)
                        data=client.call(session, 'order.cancel',[mapping_id.store_order_id])
                        sync_vals['status'] = 'success'
                        message += 'Canceled Order successfully '
                    except Error as e:
                        e =str(e).strip('<').strip('>')
                        message += '<br/>Error For  Order  %s  Cancel Order <br/>%s'%(mapping_id.store_order_id,str(e))
                    except Exception as e:
                        message += '<br/>Error For  Order  %s  Cancel Order <br/>%s'%(mapping_id.store_order_id,str(e))
                    sync_vals['summary'] = message
                    if debug:
                        _logger.debug("=do_transfer #2==%r=====%r==%r="%(comment,data,sync_vals))
                    mapping_id.channel_id._create_sync(sync_vals)

    @api.model
    def sync_quantity_magento1x(self,mapping,product_qty,**kwargs):
        channel_id = self
        message = ''
        res = channel_id.get_magento1x_session()
        if not res.get('session'):
            message+=res.pop('message')
            return False
        else:
            result = {'status': True, 'message': ''}
            store_id = mapping.store_product_id
            qty_available = 0
            qty_available+=product_qty
            data=dict(
                sku = mapping.default_code,
                stock_data=dict(
                qty= qty_available,
                is_in_stock= qty_available and 1 or 0,
                )
            )
            res=channel_id.magento1x_update_product(product_id=store_id,data=data,channel_id=channel_id,**res)
            result.update(res)
            return result

    def import_magento1x_attributes_sets(self,kwargs):
        self.ensure_one()
        vals =dict(
            channel_id=self.id,
        )
        obj=self.env['import.magento1x.attributes.sets'].create(vals)
        return obj.import_now(kwargs)

    @staticmethod
    def trun(**data):
        if data.get("image"):
            data['image'] = data['image'][:15] + '....'
        return data
        
    def import_magento1x(self, object, **kwargs):
        result = None
        debug = self.debug == 'enable'
        res = self.get_magento1x_session()
        session = res.get('session')
        if not session:
            return None,None
        if object == 'res.partner':
            result = self.env['import.partners']._magento1x_import_partners(self,res,kwargs)
        elif object == 'product.category':
            result = self.env['import.categories']._magento1x_import_categories(self, res, kwargs)
            kwargs.update(page_size=1000)
        elif object == "product.template":
            result = self.env['import.templates']._magento1x_import_products(self, res, kwargs)
        elif object == "sale.order":
            result = self.env['import.orders']._magento1x_import_orders(self, res, kwargs)
        elif object == "product.attribute":
            result = self.import_magento1x_attributes_sets(kwargs)
        elif object == 'delivery.carrier':
            result = []
            kwargs.update(
                message="For magento this operation gets automatically executed when order sync run, so you don't have to run it spearately."
            )
        if not result:
            result = None
        if debug:
            _logger.debug('====================result==%r=================',result)
        return result,kwargs
    
    def update_magento1x(self, record, get_remote_id):
        result = None,None
        debug = self.debug == 'enable'
        res = self.get_magento1x_session()
        session = res.get('session')
        if not session:
            return result
        model_name = record._name
        if model_name == 'product.category':
            result = self.env['export.categories'].magento1x_post_categories_data(self, record, "update", res, kwargs)
        
        elif model_name == 'product.template':
            result = self.env['export.templates'].with_context(base_operation='update').magento1x_post_products_data(self, record, **res)
            if result.get('update_ids'):
                result = True,res
        if debug:
            _logger.debug('================UPDATE RESULT+%r+++++++++++++',result)
        return result

    @classmethod
    def _magento1x_get_product_images_vals(cls,media):
        vals = dict()
        for data in media.get('media'):
            image_url = data.get('url')
            if image_url:
                vals['image'] =cls.read_website_image_url(image_url)
                vals['image_url'] = image_url
            break
        return vals

    @staticmethod
    def magento1x_upload_image(session,client,product_id,image,image_name,operation):
        file = dict(
            content=image,
            mime='image/jpeg',
            name= image_name
        )
        media_data = dict(
            file=file,
            types=['image','thumbnail','small_image'],
            label='label'
        )
        post_data =[product_id,media_data]
        if operation=='update':
            post_data = [product_id,image_name,media_data]

        return client.call(session,'product_media.%s'%(operation),post_data
        )

    @classmethod
    def magento1x_create_category(cls,session,client,data,**kwargs):
        message=''
        obj_id= None
        parent_id = data.pop('parent_id',2)
        try:

            obj_id=  client.call(session, 'catalog_category.create',[parent_id,data])
        except Error as e:
            e =str(e).strip('<').strip('>')
            message += '<br/>For Categories %s<br/>%s'%(data.get('name'),e)
        except Exception as e:
            message += '<br/>For Categories %s<br/>%s'%(data.get('name'),e)
        return dict(
            obj_id=obj_id,
            message=message
        )

    @classmethod
    def magento1x_update_category(cls,session,client,data,**kwargs):
        message=''
        obj_id= None
        store_id = data.pop('store_id')
        try:

            obj_id=  client.call(session, 'catalog_category.update',[store_id,data])
        except Error as e:
            e =str(e).strip('<').strip('>')
            message += '<br/>For Categories %s<br/>%s'%(data.get('name'),e)
        except Exception as e:
            message += '<br/>For Categories %s<br/>%s'%(data.get('name'),e)
        return dict(
            obj_id=obj_id,
            message=message
        )

    @classmethod
    def magento1x_create_product(cls,session,client,data,channel_id,**kwargs):
        message=''
        debug = channel_id.debug=='enable'
        obj_id= None
        _type = data.pop('_type','simple')
        set_id = data.pop('set_id','4')
        sku = data.pop('sku','None')
        image = data.pop('image','None')
        store_code = channel_id.store_code
        try:

            obj_id=  client.call(session, 'catalog_product.create',[_type,set_id,sku,data,store_code])
            if image:
                image_name = 'image_%s'%(sku)
                cls.magento1x_upload_image(session,client,obj_id,image,image_name,'create')
        except Error as e:
            e =str(e).strip('<').strip('>')
            message += '<br/>For Product %s<br/>%s'%(data.get('name'),e)
        if debug:
            _logger.debug("%r===%r==="%(data,message))
        return dict(
            obj_id=obj_id,
            message=message
        )

    @classmethod
    def magento1x_update_product(cls,session,client,product_id,data,channel_id,**kwargs):
        message=''
        status= False
        _type = data.pop('_type','simple')
        set_id = data.pop('set_id','4')
        sku = data.pop('sku','None')
        image = data.pop('image','None')
        store_code = channel_id.store_code
        try:
            status=  client.call(session, 'catalog_product.update',[product_id,data,store_code])
            if image:
                media_res = channel_id._fetch_magento1x_product_media(client=client,session=session,
                product_id=product_id)
                message += media_res.get('message','')
                media = media_res.get('data',{}).get('media')
                if len(media):
                    image_name = EL(media).get('file')

                    cls.magento1x_upload_image(session,client,product_id,image,image_name,'update')
                else:
                    image_name = 'image_%s'%(sku)
                    cls.magento1x_upload_image(session,client,product_id,image,image_name,'create')
        except Error as e:
            e =str(e).strip('<').strip('>')
            message += '<br/>For Product %s<br/>%s'%(data.get('name'),e)
        except Exception as e:
            message += '<br/>For Product %s<br/>%s'%(data.get('name'),e)
        return dict(
            status=status,
            message=message
        )
