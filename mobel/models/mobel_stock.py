# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class StockBackorderConfirmationLine(models.TransientModel):
    _inherit = 'stock.backorder.confirmation.line'



    def process_cancel_backorder(self):
        print(self)
        print(Hola)

        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            return self.env['stock.picking']\
                .browse(pickings_to_validate)\
                .with_context(skip_backorder=True, picking_ids_not_to_backorder=self.pick_ids.ids)\
                .button_validate()
        return True
