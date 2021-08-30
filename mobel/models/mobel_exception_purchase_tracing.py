# -*- coding: utf-8 -*-

from random import randint

from odoo import models, fields, api

class ExceptionPurchaseTracing(models.Model):
    _name = 'exception.purchase.tracing'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Purchase Order Exception"
    _rec_name ="name"

    @api.depends('estimated_delivery_date', 'currency_id', 'company_id', 'company_id.currency_id')
    def _compute_currency_rate(self):
        for order in self:
            order.currency_rate = self.env['res.currency']._get_conversion_rate(order.company_id.currency_id, order.currency_id, order.company_id, order.estimated_delivery_date)
    
    
    name = fields.Char('N°', required=True, index=True, copy=False, default='New Register')

    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )

    po_name_order_line = fields.Char( string='Name Order Line', )
    po_product_qty_line = fields.Char( string='Product Qty Order Line', )
    po_product_id_line = fields.Char( string='Product id Order Line', )
    po_price_unit_line = fields.Char( string='Price id Order Line', )
    po_date_planned_line = fields.Char( string='Date Planned Order Line', )
    po_sale_order_line = fields.Char( string='Sale Line Order Line', )
    po_order_line = fields.Char( string='Order Line', )
    po_order_line = fields.Char( string='Order Line', )





    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New Import') == 'New Import':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('exception.purchase.tracing', sequence_date=seq_date) or '/'
        return super(ExceptionPurchaseTracing, self_comp).create(vals)