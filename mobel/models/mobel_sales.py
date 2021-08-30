# -*- coding: utf-8 -*-

from random import randint

from odoo import models, fields, api

STATES_SALES_TRACKING = {
    ('payment_received' , 'Pago recibido'),
    ('preparend_send_store_miami' , 'Preparando su pedido en tienda Miami'),
    ('on_deposit_miami' , 'En depósito Miami'),
    ('traveling_to_uruguay' , 'Viajando a Uruguay'),
    ('arrived' , 'Arribado'),
    ('ready_to_deliver' , 'Listo para entregar'),
    ('delivered' , 'Entregado'),
}



class SaleOrderLine(models.Model):
    _inherit = 'sale.order'

    purchase_confirmed = fields.Boolean(string='Purchase Confirmed',default=False,required=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

        
    status_tracking_id = fields.Many2one(
        'status.tracking', string='Status Tracking', change_default=True, ondelete='restrict')

    status_sales_tracking_id = fields.Selection(selection=[
                ('payment_received' , 'Pago recibido'),
                ('preparend_send_store_miami' , 'Preparando su pedido en tienda Miami'),
                ('on_deposit_miami' , 'En depósito Miami'),
                ('traveling_to_uruguay' , 'Viajando a Uruguay'),
                ('arrived' , 'Arribado'),
                ('ready_to_deliver' , 'Listo para entregar'),
                ('delivered' , 'Entregado'),

        ], string='Status Sales Tracking', copy=False, tracking=True,
        default='payment_received')
   

    url_prd = fields.Char(related='product_template_id.url_product', store=True)

    #('purchase_confirmed', 'Purchase Confirmed'),
    state_process = fields.Selection(selection=[
            ('initial', 'Order Received'),           
            ('pending', 'Pending'),
            ('not_available', 'Not Available'),
            ('purchase_confirmed', 'Purchase Confirmed'),
            ('cancelled', 'Cancelled'),
        ], string='Status Process', copy=False, tracking=True,
        default='initial')

    display_list = fields.Boolean(string='Display List',default=True)



class StatusTracking(models.Model):
    _name = "status.tracking"
    _description = "CRM Tag"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Status already exists !"),
    ]
