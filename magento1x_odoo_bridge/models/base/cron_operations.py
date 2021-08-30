# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import models, api, _

class MultiChannelSale(models.Model):
    _inherit = 'multi.channel.sale'

    def magento1x_import_order_cron(self):
        #adding filter
        kw =  {'filter_on':"date_range"}
        if self.import_order_date and self.update_order_date:
            kw['start_date'] = self.import_order_date
            kw['end_date'] = self.update_order_date
        obj = self.env['import.operation'].create({'channel_id':self.id})
        obj.import_with_filter(object="sale.order",**kw)

    def magento1x_import_product_cron(self):
        #adding filter
        obj = self.env['import.operation'].create({'channel_id':self.id})
        kw =  {'filter_on':"date_range"}
        if self.import_product_date and self.update_product_date:
            kw['start_date'] = self.import_product_date
            kw['end_date'] = self.update_product_date
        obj.import_with_filter(object="product.template",**kw)
    
    def magento1x_import_partner_cron(self):
        #adding filter
        obj = self.env['import.operation'].create({'channel_id':self.id})
        kw =  {'filter_on':"date_range"}
        if self.import_customer_date and self.update_customer_date:
            kw['start_date'] = self.import_customer_date
            kw['end_date'] = self.update_customer_date
        obj.import_with_filter(object="res.partner",**kw)
    
    def magento1x_import_category_cron(self):
        obj = self.env['import.operation'].create({'channel_id':self.id})
        obj.import_with_filter(object="product.category")
