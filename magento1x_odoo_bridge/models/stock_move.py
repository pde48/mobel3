# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
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
# Developed By: PRAKASH KUMAR
##########################################################################
from itertools import groupby
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

# store_product_id
# store_variant_id
class StockMove(models.Model):
    _inherit = "stock.move"

    def multichannel_sync_quantity(self, pick_details):
            channel_list = self._context.get('channel_list')
            if not channel_list:
                channel_list = list()
            channel_list.append('magento1x')
            return super(
                StockMove,self.with_context(
                    channel_list=channel_list)
                    ).multichannel_sync_quantity(pick_details)
