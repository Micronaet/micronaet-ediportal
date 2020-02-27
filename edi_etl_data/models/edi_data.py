# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields, api, exceptions
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """ Model name: Res Partner
    """
    _inherit = 'res.partner'

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    etl_import = fields.Boolean('ETL Import')

    # Account reference:
    customer_code = fields.Char('Customer code', size=9)
    destination_code = fields.Char('Destination code', size=9)
    supplier_code = fields.Char('Supplier code', size=9)


class ResUsers(models.Model):
    """ Model name: Res Users
    """
    _inherit = 'res.users'

    # -------------------------------------------------------------------------
    # Button:
    # -------------------------------------------------------------------------
    @api.multi
    def update_all_portal_partner(self):
        """ Update order and pricelist
        """
        self.update_all_data(self.id)

    @api.multi
    def remove_all_portal_partner(self):
        """ Remove reference from order and pricelist
        """
        self.update_all_data(False)
        self.portal_partner_id = False

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    @api.model
    def update_all_data(self, user_id):
        """ Utility for reset or setup the user in pricelist and sale order
        """
        operation = 'update' if user_id else 'remove'
        partner_id = self.portal_partner_id.id

        # ---------------------------------------------------------------------
        # Remove portal partner from sale order:
        # ---------------------------------------------------------------------
        order_pool = self.env['sale.order']
        orders = order_pool.search([
            ('partner_id', '=', partner_id)])
        orders.write({
            'user_id': user_id,
            })
        _logger.info('%s %s sale order' % (operation, len(orders)))

        # ---------------------------------------------------------------------
        # Remove portal partner from pricelist:
        # ---------------------------------------------------------------------
        pricelist = self.env['res.partner.pricelist']
        pricelists = pricelist.search([
            ('partner_id', '=', partner_id)])
        pricelists.write({
            'user_id': user_id,
            })

        _logger.info('%s %s pricelists items' % (operation, len(pricelists)))

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    portal_partner_id = fields.Many2one('res.partner', 'Portal Customer')


class ResPartnerPricelist(models.Model):
    """ Model name: Res Partner Pricelist
    """
    _name = 'res.partner.pricelist'
    _description = 'Partner pricelist'
    _rec_name = 'product_id'

    # -------------------------------------------------------------------------
    #                                   BUTTON:
    # -------------------------------------------------------------------------
    @api.multi
    def generate_purchase_order(self):
        """ Generate all purchase order from quantity selected
        """
        order_pool = self.env['sale.order']
        line_pool = self.env['sale.order.line.my']
        user_pool = self.env['res.users']

        now = ('%s' % fields.Datetime.now())[:19]
        
        user_id = self.env.uid
        user = user_pool.browse(user_id)
        pricelists = self.search([
            ('user_id', '=', user_id),
            ('product_uom_qty', '>', 0),
            ])

        if not pricelists: 
            raise exceptions.Warning('No quantity setup! Insert almost one')
        
        # -------------------------------------------------------------
        # Create sale order:
        # -------------------------------------------------------------
        order_id = order_pool.create({
            'partner_id': user.portal_partner_id.id,
            'user_id': user_id,
            'date_order': now,
            }).id

        for item in pricelists:
            pricelist_id = item.id
            #lst_price = item.lst_price
            product_uom_qty = item.product_uom_qty

            product = item.product_id
            line_pool.create({
                'user_id': user_id,
                'order_id': order_id,
                'product_id': pricelist_id,
                'name': product.name,
                'product_uom_qty': item.product_uom_qty,
                #'price_unit': lst_price,
                })
        
        # Reset selection:
        pricelists.write({
            'product_uom_qty': 0,
            })    

        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_id': order_id,
            'res_model': 'sale.order',
            'view_id': False,
            'views': [(False, 'form'), (False, 'tree')],
            'domain': [],
            'context': self.env.context,
            'target': 'current',
            'nodestroy': False,
            'form_view_initial_mode': 'edit', 
            'force_detailed_view': 'true',
            }
            
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    user_id = fields.Many2one('res.users', 'Customer user')

    partner_id = fields.Many2one('res.partner', 'Customer')
    product_id = fields.Many2one('product.product', 'Product')
    lst_price = fields.Float('List price', digits=(16, 3))
    product_uom_qty = fields.Float('Order qty', digits=(16, 3))

class SaleOrderLineMy(models.Model):
    """ Model name: Sale order line
    """
    _name = 'sale.order.line.my'
    _description = 'My sale order'
    _rec_name = 'product_id'
    
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    product_id = fields.Many2one(
        'res.partner.pricelist', 'Product', 
        domain="[('user_id', '=', user_id)]",
        )
    user_id = fields.Many2one(
        'res.users', 'Customer user', default=lambda s: s.uid)

    order_id = fields.Many2one('sale.order', 'Order')
    product_uom_qty = fields.Float('Product qty', digits=(16, 3))

class SaleOrder(models.Model):
    """ Model name: Sale order
    """
    _inherit = 'sale.order'

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    user_id = fields.Many2one('res.users', 'Customer user')
    my_line_ids = fields.One2many('sale.order.line.my', 'order_id', 'My line')
    partner_id = fields.Many2one(
        'res.partner', 'Partner', related='user_id.portal_partner_id', 
        store=True)
