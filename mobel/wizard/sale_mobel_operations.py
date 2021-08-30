# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools
from odoo.osv import expression
from datetime import datetime, time

from odoo.exceptions import UserError, ValidationError



class GenerateExceptionPurchases(models.TransientModel):
    _name = "purchase.generate.excepction"
    _description = "Generate Purchases Excepction"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    count = fields.Integer(default=_count, string='Cantidad de Ordenes Seleccionadas')

    decision_purchase = fields.Selection(selection=[
        ('new_order', 'New order'),
        ('returned_ammount', 'Return Money'),

    ], string='Desicion Order', copy=False,required=True )

    motive_order = fields.Text(string='Specify reason',required=True)
    motive_decision_purchase = fields.Selection(selection=[
        ('product_bad_condition', 'Product in bad condition'),
        ('product_not_arrive', 'Product did not arrive'),

    ], string='Desicion Order', copy=False,required=True )

    def process_desicion(self):
        """
            2 Tipos de Opciones encargar nueva orden

            Cancelando la linea de la orden de compra, estabelcendola en 0
            Cancelando el status de la linea de Venta


            1 -New Order
                        Guardar Log
                        Crear Orden de Venta Nuevo
                        Copiar sale order line
                        Eliminar La linea de Pedido de Venta
                        Asignar Cupon 15USD


            2..- Devolver Dinero
                        Guardar Log
                        Elimnar la Linea           
                        DEvolver Diner

        """
        for po_res in self:
            print(po_res)
        myList = []
        purchase_orders_lines = self.env['purchase.order.line'].browse(self._context.get('active_ids', []))
        for rec_ in purchase_orders_lines:
            print(rec_)
            res_search = self.env['purchase.order.line'].search_read([('id','=',rec_.id)],['auto_sale_order_id','sale_line_id','order_id','id','product_id'])
            for res_1 in res_search:
                print(res_1)
                if res_1['auto_sale_order_id'] not in myList:
                    myList.append(res_1['auto_sale_order_id'])
            

        print(myList)

        print(auto_sale_order_id)

class SaleGeneratePurchasesPending(models.TransientModel):
    _name = "sale.generate.purchases.pending"
    _description = "Sales Generate Purchases pending"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    count = fields.Integer(default=_count, string='Cantidad de Ordenes Seleccionadas')

    state_process = fields.Selection(selection=[
        ('initial', 'Initial'),
        ('pending', 'Pending'),
        ('not_available', 'Not Available'),
        ('cancelled', 'Cancelled'),
    ], string='Status Process', copy=False,required=True )

  
    decision_purchase = fields.Selection(selection=[
        ('discount_coupon', 'Discount coupon'),
        ('change_product_discount_coupon', 'change product and discount coupon'),
        ('returned_ammount', 'Return Money'),


    ], string='Desicion Order', copy=False,required=False )

    ammount_coupon = fields.Float(string='Ammount Coupon',)
    display_list = fields.Boolean(string='Display List',default=True)

    motive_canceled = fields.Char(string='Motive de Canceled',)

    
    def generate_purchases_pending(self):
        print(self)
        sale_orders_lines = self.env['sale.order.line'].browse(self._context.get('active_ids', []))
        for rec_ in sale_orders_lines:
            print(rec_)
            for rec2 in self:
                print(rec_.state_process)
                if(rec2.state_process == 'pending'):
                    rec_update = rec_.update({'state_process': rec2.state_process})
                    print(rec2)
                else:
                    if(rec2.state_process == 'not_available'):
                        rec_update = rec_.update({'state_process': rec2.state_process,'display_list': False})
                        print(rec2)
                    else:
                        rec_update = rec_.update({'state_process': rec2.state_process})
                                

        return {'type': 'ir.actions.act_window_close'}





class SaleGeneratePurchases(models.TransientModel):
    _name = "sale.generate.purchases"
    _description = "Sales Generate Purchases"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()


    product_id = fields.Many2one('product.product', string='Product', domain=[('type', '=', 'service')],
        default=_default_product_id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    partner_id_purchase = fields.Many2one('res.partner', string='Supplier USA', required=True, change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    count = fields.Integer(default=_count, string='Ordenes Seleccionadas')



    
    def generate_purchases(self):
        #self.ensure_one()
        dict_values_config = self.env['res.config.settings'].sudo().get_values()
        val_company_purchase_import_id = dict_values_config['company_purchase_import_id']
        warehouse_default_uy_id = dict_values_config['warehouse_default_uy_id']
        warehouse_default_usa_id = dict_values_config['warehouse_default_usa_id']
        location_default_uy_id = dict_values_config['location_default_uy_id']
        location_default_usa_id = dict_values_config['location_default_usa_id']


        company_id = self.env.company
        validate_company_purchase_origen = self.env['res.config.settings'].search([('company_purchase_import_id','=',self.env.company.id)])
        if(not validate_company_purchase_origen):
            raise ValidationError(_('The active Company is not configured to generate Shopping Routes : %s)', self.env.company.name))

        #Get Company Purchase Supplier
        val_company_purchase_supplier_id = dict_values_config['company_purchase_supplier_id']

        """
            1.- Validar Emppresa Origen sea de Compra
            2-. Validar que exista ye ste en la compañia de Compra
            3.- Crear Orden de Compra

            REVISARRRRRRRRRRRRRRRRR

            LISTAS DE PRECIOS
            SECUENCIAS POR EMPRESAS DIUFERNCIARLAS
        """
        #Create Purchase Order
        get_partner_id_po_1 = self.env['res.company'].search_read([('id','=',val_company_purchase_supplier_id)],['partner_id'])
        for res_1 in get_partner_id_po_1:
            partner_id_po_1 = res_1['partner_id'][0]


        #Get Picking Type
        picking_type_id = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'), ('warehouse_id', '=', warehouse_default_uy_id)
        ], limit=1)

        company_partner = company_id.partner_id.with_user(val_company_purchase_import_id)



        vals_create_po = {
                    'name': self.env['ir.sequence'].sudo().next_by_code('purchase.order'),
                    'origin': "SO MAGENTO",
                    'partner_id': partner_id_po_1,
                    'required_import' : True,
                    'user_id': False,
                    'picking_type_id': picking_type_id.id,
                    'company_id': val_company_purchase_import_id,
                    'currency_id': company_id.currency_id.id,
                    #'payment_term_id': partner.with_company(company_id).property_supplier_payment_term_id.id,
                    'date_order': datetime.now(),
                    'auto_generated': True,
                    #'auto_sale_order_id': self.id,
                }

        res_po_1 = self.env['purchase.order'].sudo().create(vals_create_po)

        res_po_1.write({'state': 'purchase'})

        #########################################################################
        ##################### REVISAR DEBE TENER ACTIVADO EL MULTIEMPRESA PARA QUE PUEDA GENERAR CORRECTO
        picking_type_id_usa = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'), ('warehouse_id', '=', warehouse_default_usa_id)
        ])
        #########################################################################
        ##################### REVISAR DEBE TENER ACTIVADO EL MULTIEMPRESA PARA QUE PUEDA GENERAR CORRECTO


        #create Purchase Order Supplier
        vals_create_po_2 = {
                    'name': self.env['ir.sequence'].sudo().next_by_code('purchase.order'),
                    'partner_id': self.partner_id_purchase.id,
                    'user_id': False,
                    'picking_type_id': picking_type_id_usa.id,
                    'company_id': val_company_purchase_supplier_id,
                    'currency_id': company_id.currency_id.id,
                    'origin': 'SALES MAGENTO 2',
                    'date_order': datetime.now(),
                    #'fiscal_position_id': fpos.id,
                    #'group_id': group
                }

        res_po_2 = self.env['purchase.order'].sudo().create(vals_create_po_2)
        res_po_2.write({'state': 'purchase'})

        sale_orders_lines = self.env['sale.order.line'].browse(self._context.get('active_ids', []))
        vals_gen1 = {}
        vals_gen1_item = {}
        for rec_ in sale_orders_lines:
            partner_id_purchase = self.partner_id_purchase
            print(rec_.id)

            get_data_add = self.env['sale.order.line'].search_read([('id','=',rec_.id)])
            for res_2_data in get_data_add:
                #print(res_2_data)
                line_order_id = res_2_data['id']

                print(res_2_data['order_partner_id'])
                product_id = res_2_data['product_id'][0]
                uom_po_qty = float(res_2_data['product_uom_qty'])
                name = res_2_data['name']
                product_uom = res_2_data['product_uom'][0]
                price_unit = res_2_data['price_unit']
                date_planned = datetime.now()
                sale_order_id = res_2_data['order_id'][0]
                        

                vals_create_po_order_line = {
                        'name': name,
                        'product_qty': uom_po_qty,
                        'product_id': product_id,
                        'product_uom': product_uom,
                        'price_unit': price_unit,
                        'date_planned': date_planned,
                        #'taxes_id': [(6, 0, taxes_id.ids)],
                        'sale_line_id': line_order_id,
                        'order_id': res_po_1.id,
                        'auto_sale_order_id':sale_order_id,
                    }


                res_po_order_line_1 = self.env['purchase.order.line'].sudo().create(vals_create_po_order_line)


                vals_create_po_order_line_2 = {
                            'name': name,
                            'product_qty': uom_po_qty,
                            'product_id': product_id,
                            'product_uom': product_uom,
                            'price_unit': price_unit,
                            'date_planned': date_planned,
                            #'taxes_id': [(6, 0, taxes_id.ids)],
                            #'move_dest_ids': self.location_default_usa_id and [(4, self.location_default_usa_id.id)] or [],
                            'order_id': res_po_2.id,
                        }
                res_po_order_line_2 = self.env['purchase.order.line'].sudo().create(vals_create_po_order_line_2)

                res_order_self_2 = self.env['sale.order'].search([('id','=',sale_order_id)])
                res_order_self_2.write({'state': 'sale'})


                #update order.line
                up_ord_line = self.env['sale.order.line'].search([('id','=',line_order_id)])
                for res_p in up_ord_line:
                    rec_update = res_p.update({'state_process': 'purchase_confirmed'})
            


        #print(hola)

        return {'type': 'ir.actions.act_window_close'}
