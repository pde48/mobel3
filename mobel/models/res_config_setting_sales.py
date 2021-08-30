# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

   
    company_purchase_supplier_id = fields.Many2one(
        'res.company',
        'Compañia Recepcion de Compras/Comprar a Proveedores (IKEA, Etc)',
        config_parameter='mobel.default_partner_purchase_id',
        help='Compañia de Compra por Defecto', required=True)

    company_purchase_import_id = fields.Many2one(
        'res.company',
        'Compañia Origen de Compras/Importaciones',
        config_parameter='mobel.default_partner_sale_id',
        help='Compañia de Compra por Defecto', required=True)


    warehouse_default_uy_id = fields.Many2one(
        'stock.warehouse',
        'Warehouse Mobel UY',
        config_parameter='mobel.default_warehouse_default_uy_id',
        help='Almacen Mobel UY por Defecto', required=True)

    warehouse_default_usa_id = fields.Many2one(
        'stock.warehouse',
        'Warehouse Mobel USA',
        config_parameter='mobel.default_warehouse_default_usa_id',
        help='Almacen Mobel USA por Defecto', required=True)


    location_default_uy_id = fields.Many2one(
        'stock.location',
        'location Mobel UY',
        config_parameter='mobel.default_location_default_uy_id',
        help='location Mobel UY por Defecto', required=True)

    location_default_usa_id = fields.Many2one(
        'stock.location',
        'location Mobel USA',
        config_parameter='mobel.default_location_default_usa_id',
        help='location Mobel USA por Defecto', required=True)


    def set_values(self):
        super(ResConfigSettings,self).set_values()
        IrDefault = self.env['ir.default'].sudo()

        IrDefault.set(
            'res.config.settings',
            'company_purchase_supplier_id',
            self.company_purchase_supplier_id.id
        )
        IrDefault.set(
            'res.config.settings',
            'company_purchase_import_id',
            self.company_purchase_import_id.id
        )

        IrDefault.set(
            'res.config.settings',
            'warehouse_default_uy_id',
            self.warehouse_default_uy_id.id
        )

        IrDefault.set(
            'res.config.settings',
            'warehouse_default_usa_id',
            self.warehouse_default_usa_id.id
        )

        IrDefault.set(
            'res.config.settings',
            'location_default_uy_id',
            self.location_default_uy_id.id
        )

        IrDefault.set(
            'res.config.settings',
            'location_default_usa_id',
            self.location_default_usa_id.id
        )
        return True

    @api.model
    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            {
                'company_purchase_supplier_id': IrDefault.get('res.config.settings','company_purchase_supplier_id'),
                'company_purchase_import_id': IrDefault.get('res.config.settings','company_purchase_import_id',),
                'warehouse_default_uy_id': IrDefault.get('res.config.settings','warehouse_default_uy_id',),
                'warehouse_default_usa_id': IrDefault.get('res.config.settings','warehouse_default_usa_id',),
                'location_default_uy_id': IrDefault.get('res.config.settings','location_default_uy_id',),
                'location_default_usa_id': IrDefault.get('res.config.settings','location_default_usa_id',),
            }
        )
        return res
