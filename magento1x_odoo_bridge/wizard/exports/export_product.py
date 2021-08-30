# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################
from odoo import api, fields, models, _
from odoo.addons.odoo_multi_channel_sale.tools import extract_list as EL
from odoo.addons.odoo_multi_channel_sale.tools import ensure_string as ES

class ExportMagento1xProducts(models.TransientModel):
    _inherit = ['export.templates']

    default_product_set_id = fields.Many2one(
        comodel_name='magento.attributes.set',
        string='Default Attribute-Set',
        help='Magento Product Attribute Set.',
    )

    @api.onchange('channel_id')
    def set_default_magento_data(self):
        channel_id = self.channel_id
        if channel_id.channel=='magento1x' and channel_id.default_product_set_id:
            self.default_product_set_id = channel_id.default_product_set_id.id

    @api.model
    def magento1x_get_store_category_ids(self,product_id,channel_id):
        res =None
        match_category = channel_id.get_channel_category_id(product_id,channel_id,limit=None)
        if match_category:
            res= list(map(int,match_category))
            if 1 in res:res.remove(1)
        elif channel_id.channel_default_product_categ_id:
            res= [channel_id.channel_default_product_categ_id.store_category_id]
        return res

    @api.model
    def magento1x_get_product_data(self,product_id,channel_id):
        product_set_id = (self.default_product_set_id or
            channel_id.default_product_set_id
        )
        context = dict(self._context)
        context.update({
            'lang':channel_id.language_id.code,
            'pricelist':channel_id.pricelist_name.id
        })
        product_data = product_id.with_context(context).read([])[0]
        description = product_data.get('description_sale')
        default_code = product_data.get('default_code')
        if not default_code and channel_id.sku_sequence_id:
            product_id.default_code = channel_id.sku_sequence_id.next_by_id()
        sku =  product_id.default_code
        qty_available = product_data.get('qty_available')
        context = dict(self._context)
        data=dict(
            _type='simple',
            set_id=int(product_set_id.store_id),
            sku = sku,
            image = product_id.image_1920,
            name=product_data.get('name') ,
            description=description,
            short_description=description,
            price=product_data.get('price') ,
            cost=product_data.get('standard_price') ,
            weight=product_data.get('weight') ,
            status=product_data.get('sale_ok') and 1 or 2,
            visibility='4',
            tax_class_id ='0',
            stock_data=dict(
               qty= qty_available,
               is_in_stock= qty_available and 1 or 0,
            )
        )
        categories = self.magento1x_get_store_category_ids(product_id,channel_id)
        if categories:
            data['categories'] = categories
        return data

    @api.model
    def magento1x_create_product_data(self,channel_id,product_id,**kwargs):
        mapping_obj = self.env['channel.template.mappings']
        data = self.magento1x_get_product_data(product_id,channel_id)
        if "sku" in data:
            res=channel_id.magento1x_create_product(data=data,channel_id=channel_id,**kwargs)
            message = res.get('message')
            store_product_id = res.get('obj_id')
        else:
            message = "Please set sku sequence in configurations..."
        mapping_id = None
        if store_product_id:
            if not self._context.get('base_operation'):
                mapping_id=channel_id.create_template_mapping(product_id,store_product_id,
                vals=EL(product_id.read(['default_code','barcode'])))
                for variant_id in product_id.product_variant_ids:
                    channel_id.create_product_mapping(product_id, variant_id, store_product_id,'No Variants',
                    vals=EL(variant_id.read(['default_code','barcode'])))
            else:
                mapping_id = [store_product_id]
        #add your custom code here
        return dict(
            mapping_id=mapping_id,
            message=message
        )
    @api.model
    def magento1x_update_product_data(self,channel_id,product_id,**kwargs):
        mapping_obj = self.env['channel.template.mappings']
        message=''
        mapping_id = None
        magento1x_mapping = product_id.channel_mapping_ids.filtered(lambda mapping:mapping.channel_id.channel=='magento1x')
        if not len(magento1x_mapping):
            message+='Mapping not exits for template %s [%s].'%(product_id.name,product_id.id)
        for match in magento1x_mapping:
            store_product_id = match.store_product_id
            data = self.magento1x_get_product_data(product_id,channel_id)
            data['default_code'] = match.default_code
            res=channel_id.magento1x_update_product(product_id=store_product_id,data=data,channel_id=channel_id,**kwargs)
            message+=res.get('message')
            status =res.get('status')
            if status:
                mapping_id=match
                match.need_sync='no'
        return dict(
            mapping_id=mapping_id,
            message=message
        )
    @api.model
    def post_magento1x_category(self, channel_id, odoo_category_ids, operation ='export', **kwargs):
        Attribute = self.env['export.categories']
        for category in odoo_category_ids:
            export_category = Attribute.magento1x_post_categories_data(channel_id, category, operation,kwargs, None)
        if export_category:
            self.env['channel.category.mappings'].create(
                {
                    'channel_id'       : channel_id.id,
                    'ecom_store'       : channel_id.channel,
                    'category_name'    : category.id,
                    'odoo_category_id' : category.id,
                    'store_category_id': export_category,
                    'operation'        : 'export',
                }
            )
            return True



    @api.model
    def export_mage1x_product_category(self,product_tmpl_ids,channel_id,**kwargs):
        result = dict(
            data = None,
            message=''
        )
        data=dict()
        new_attribute_for_value = self.env['product.category']
        map_obj = self.env['channel.category.mappings']
        channel_category_ids = product_tmpl_ids.mapped('channel_category_ids')
        categ = channel_category_ids.filtered(lambda cat:cat.instance_id==channel_id)
        extra_category_ids = categ.mapped('extra_category_ids')
        domain = [
            ('category_name', 'in',extra_category_ids.ids),
        ]
        match = channel_id._match_mapping(map_obj, domain)
        new_categ = extra_category_ids-match.mapped('category_name')
        if len(new_categ):
            post_res= self.post_magento1x_category(channel_id, new_categ, operation='export',**kwargs)
        #     result['message']+=post_res.get('message','')
        # return result
            if post_res:
                pass


    @api.model
    def magento1x_post_products_data(self, channel_id, product_tmpl_ids, **kwargs):
        message=''
        update_ids=[]
        create_ids=[]
        self.export_mage1x_product_category(product_tmpl_ids,channel_id,**kwargs)
        store_product_id = None
        operation = self._context.get('base_operation') if self._context.get('base_operation') \
        else self.operation
        for product_id in product_tmpl_ids:
            if product_id.product_variant_count > 1:
                message = "Product having more than one variant..."
                break # for base operations
            sync_vals = dict(
                status ='error',
                action_on ='template',
                action_type ='export',
            )
            post_res = dict()
            if operation == 'export':
                post_res=self.magento1x_create_product_data(channel_id, product_id, **kwargs)
                if post_res.get('mapping_id'):
                    create_ids+=post_res.get('mapping_id')
            else:
                post_res=self.magento1x_update_product_data(channel_id,product_id,**kwargs)
                if post_res.get('mapping_id'):
                    update_ids+=post_res.get('mapping_id')
            msz = post_res.get('message')
            if self._context.get('base_operation') == "export" and create_ids:
                store_product_id = create_ids[0]
                create_ids = dict(
                            template_id=create_ids[0],
                            variant_ids=[create_ids[0]]
                        )
            message+=msz
            if post_res.get('mapping_id'):
                if not store_product_id:
                    store_product_id = post_res.get('mapping_id').store_product_id
                sync_vals['status'] = 'success'
                sync_vals['ecomstore_refrence'] = store_product_id
                sync_vals['odoo_id'] = product_id.id
                sync_vals['summary'] = msz or '%s %sed'%(product_id.name,operation)
                channel_id._create_sync(sync_vals)
        return dict(
            message=message,
            update_ids=update_ids,
            create_ids=create_ids,

        )

    def magento1x_export_templates(self):
        message = ''
        ex_create_ids,ex_update_ids,create_ids,update_ids= [],[],[],[]
        config_tmpl_ids=[]
        exclude_type_ids=[]

        for record in self:
            channel_id = record.channel_id
            res =channel_id.get_magento1x_session()
            message+=res.pop('message','')
            if res.get('session'):
                exclude_res=record.exclude_export_data(record.product_tmpl_ids,channel_id,record.operation)
                template_ids=exclude_res.get('object_ids')
                product_tmpl_ids = template_ids.filtered(
                    lambda pt:pt.product_variant_count==1 and pt.type in ['product','consu']
                )
                ex_update_ids+=exclude_res.get('ex_update_ids')
                ex_create_ids+=exclude_res.get('ex_create_ids')
                config_tmpl_ids+=  record.product_tmpl_ids.filtered(
                    lambda pt:pt.product_variant_count>1
                )
                exclude_type_ids+=record.product_tmpl_ids.filtered(
                    lambda pt:pt.type not in ['product','consu']
                )
                post_res=record.magento1x_post_products_data(channel_id=channel_id,
                    product_tmpl_ids=product_tmpl_ids,**res
                )
                create_ids+=post_res.get('create_ids')
                update_ids+=post_res.get('update_ids')
                message+=post_res.get('message')
        if len(config_tmpl_ids):
           message += '<br/> Total %s  product template not exported/updated because of having more than one variants.'%(len(config_tmpl_ids))
        if len(exclude_type_ids):
           message += '<br/> Total %s  product template not exported/updated because of having type other than product  and consumable .'%(len(exclude_type_ids))
        message+=self.export_message(ex_create_ids,ex_update_ids,create_ids,update_ids)
        return self.env['multi.channel.sale'].display_message(message)
