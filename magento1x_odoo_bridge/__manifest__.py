# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo Multichannel Magento 1.X Connector",
  "summary"              :  "Connect Magento Store With Odoo along with other multi channel platforms with this module. Manage Magento Store in Odoo",
  "category"             :  "Website",
  "version"              :  "1.0.3",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Multi-Channel-Magento-1-x-Odoo-Bridge-Multi-Channel-MOB.html",
  "description"          :  """Magento Odoo Bridge
Odoo Magento bridge
Connect Magento with Odoo
Connect Odoo with magento
Magento Orders in Odoo
Magento customers in odoo
Magento Store manage in Odoo
Integrate Magento with Odoo
Integrate Odoo with Magento
Magento Odoo data transfer
Magento store in Odoo
Integrate Odoo with Woocommerce
Integrate Woocommerce with Odoo
Ecommerce website to Odoo
E-commerce website to Odoo
Connect ecommerce website
Ecommerce connector
E-commerce connector
Multi-channel connector
Odoo Multi-channel bridge
Odoo Multi-channel Sale
Odoo Multichannel bridge
Multi channel connector""",
  "live_test_url"        :  "http://magento1odoo.webkul.com/",
  "depends"              :  ['odoo_multi_channel_sale'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/data.xml',
                             'wizard/import_operation.xml',
                             'wizard/inherits.xml',
                             'wizard/export_operation.xml',
                             'views/views.xml',
                             'views/search.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  100,
  "currency"             :  "USD",
}
