# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api,fields, models,_

class MagentoAttributesSet(models.Model):
    _rec_name='set_name'
    _name = "magento.attributes.set"
    _description = "Magento Attributes Set"
    _inherit = ['channel.mappings']

    set_name = fields.Char(
        string = 'Set Name'
    )
    attribute_ids = fields.Many2many(
        'product.attribute',
        string='Attribute(s)',
    )
