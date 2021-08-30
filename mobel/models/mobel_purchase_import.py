# -*- coding: utf-8 -*-

from random import randint

from odoo import models, fields, api

READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

STATES_MANAGMENT = {
    'draf' : 'Pago recibido',
    'preparend_send_store_miami' : 'Preparando su pedido en tienda Miami',
    'on_deposit_miami' : 'En depósito Miami',
    'traveling_to_uruguay' : 'Viajando a Uruguay',
    'arrived' : 'Arribado',
    'ready_to_deliver' : 'Listo para entregar',
    'delivered' : 'Entregado',
}


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    auto_sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
    )

    purchase_line_import_id = fields.Many2one(
        'purchase.import',
        string='Import ',
    )
    number_puchase_supplier = fields.Char('N° Supplier', required=False, index=True, copy=False,default="0")

    status_purchase_tracking_id = fields.Selection(selection=[
                ('payment_received' , 'Pago recibido'),
                ('preparend_send_store_miami' , 'Preparando su pedido en tienda Miami'),
                ('on_deposit_miami' , 'En depósito Miami'),
                ('traveling_to_uruguay' , 'Viajando a Uruguay'),
                ('arrived' , 'Arribado'),
                ('ready_to_deliver' , 'Listo para entregar'),
                ('delivered' , 'Entregado'),
    ], string='Status Purchase Tracking', copy=False, tracking=True,
    default='payment_received'
    )

    order_partner_id = fields.Many2one(
        'res.partner',
        related="auto_sale_order_id.partner_id",
        string='Order Partner',
    )


    def write(self, vals):
        # Do not allow changing the company_id when account_move_line already exist
        res = super(PurchaseOrderLine, self).write(vals)    
        for res2 in self:
            if(('status_purchase_tracking_id' in vals) and vals['status_purchase_tracking_id'] != False):
                get_status_purchase_tracking_id = vals['status_purchase_tracking_id']
                if(get_status_purchase_tracking_id != False):
                    res_update = self.env['purchase.order.line'].search_read([('id','=',res2.id)],['sale_line_id'])
                    for rec_upt in res_update:
                        res_updt2 = self.env['sale.order.line'].search([('id','=',rec_upt['sale_line_id'][0])])
                        res_updt2.write({'status_sales_tracking_id': get_status_purchase_tracking_id})

        return res




class PurchaseORder(models.Model):
    _inherit = 'purchase.order'

    purchase_import_id = fields.Many2one(
        'purchase.import',
        string='Import ',
    )

    estimated_delivery_date = fields.Date(string='Estimated Delivery Date', related="purchase_import_id.estimated_delivery_date", readonly=True)
    
    type_import = fields.Selection(related="purchase_import_id.type_import",selection=[
            ('maritime', 'Maritime'),
            ('aerial', 'Aerial'),
        ], string='Type Import', readonly=True, tracking=True,
        default='maritime')

    required_import = fields.Boolean(string='Required Import', default=False)
    auto_generated = fields.Boolean(string='Auto Generated', default=False)

  


class PurchaseImport(models.Model):
    _name = 'purchase.import'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Purchase Import"
    _rec_name ="name"

    @api.depends('estimated_delivery_date', 'currency_id', 'company_id', 'company_id.currency_id')
    def _compute_currency_rate(self):
        for order in self:
            order.currency_rate = self.env['res.currency']._get_conversion_rate(order.company_id.currency_id, order.currency_id, order.company_id, order.estimated_delivery_date)
    
    
    name = fields.Char('N°', required=True, index=True, copy=False, default='New Import')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES,
        default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.company.id)
    currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', compute_sudo=True, store=True, readonly=True, help='Ratio between the purchase order currency and the company currency')
    estimated_delivery_date = fields.Date(
        string='Estimated Delivery Date',required=True,
    )

    type_import = fields.Selection(selection=[
            ('maritime', 'Maritime'),
            ('aerial', 'Aerial'),
        ], string='Type Import', required=True, copy=False, tracking=True,
        default='maritime')

    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('in_process', 'In Process'),
            ('terminated', 'Terminated'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, copy=False, tracking=True,
        default='draft')


    purchase_id_ids = fields.One2many(
        'purchase.order',
        'purchase_import_id',
        string='Purchase Order',
    )

    purchase_id_line_ids = fields.One2many(
        'purchase.order.line',
        'purchase_line_import_id',
        string='Purchase Order',
    )

    def button_draft(self):
        self.write({'state': 'draft'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def button_process(self):
        self.write({'state': 'in_process'})
        
    def button_terminated(self):
        self.write({'state': 'terminated'})


    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New Import') == 'New Import':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.import', sequence_date=seq_date) or '/'
        return super(PurchaseImport, self_comp).create(vals)


