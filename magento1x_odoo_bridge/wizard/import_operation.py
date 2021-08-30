from odoo import api, fields, models

class ImportOperation(models.TransientModel):
    _inherit = 'import.operation'

    object = fields.Selection(
        selection_add=[
            ('product.attribute','Attributes')
        ]
    )

    magento1x_filter_type = fields.Selection(
        selection=[
            ('date_range','Date Range'),
            ('id_range', 'ID Range'),
            ('order_state', 'Order State')
        ]
    )
    magento1x_start_date = fields.Datetime("Mage From Date")
    magento1x_end_data = fields.Datetime("To Date")
    magento1x_start_id = fields.Integer('From-ID')
    magento1x_end_id = fields.Integer('Till-ID')
    # magento1x_category_id = fields.Integer('Category ID',help="Get product which belongs to this category ID")
    # magento1x_customer_email = fields.Char('Customer Email', help="Get Orders made by specific customers",size=30)
    magento1x_order_state = fields.Selection([('pending','Pending'),('done','Done')])

    def magento1x_get_filter(self):
        kw = {'filter_on':self.magento1x_filter_type}
        if self.magento1x_start_date or self.magento1x_end_data:
            kw['start_date'] = self.magento1x_start_date
            kw['end_date'] = self.magento1x_end_data
        elif self.magento1x_start_id or self.magento1x_end_id:
            kw.update(
                start_id=self.magento1x_start_id,
                end_id=self.magento1x_end_id
            )
        # elif self.magento1x_category_id:
        #     kw.update(
        #         category_id=self.magento1x_category_id
        #     ) 
        # elif self.magento1x_customer_email:
        #     kw.update(
        #         customer_email=self.magento1x_customer_email
        #     )
        elif self.magento1x_order_state:
            kw.update(
                order_state=self.magento1x_order_state
            )
        return kw

