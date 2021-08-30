# -*- coding: utf-8 -*-
{
    'name': "Mobel",
    'summary': """
        Administracion de Ventas Mobel UY a traves de E-commerce Magento
        """,

    'description': """
        Gestion de Multimepresas Mobel UY y Mobel USA
        Administrar ordenes de Ventas de origen de Magento Mobel UY
        Gestion de Compras Para Mobel USA
        Administrar Productos
        Gestion de Facturacion Mobel UY
        Administrar Notificaciones de Pago
            
    """,
    'author': "Möbel",
    'website': "http://www.somosmobel.com",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base','sale','account','stock','purchase','product','contacts','sale_stock', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/mobel_sales_view.xml',
        'views/mobel_product_view.xml',
        'views/res_config_setting_sales.xml',
        'views/mobel_purchase_import_view.xml',
        'wizard/sale_mobel_operations_views.xml',
        'views/mobel_exception_purchase_tracing_view.xml',
        'data/mobel_data.xml',

    ],
    'demo': [
    ],
}
