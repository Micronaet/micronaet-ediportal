# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import io
import xlsxwriter
import logging
import base64
import shutil
from odoo import models, fields, api

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
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    user_id = fields.Many2one('res.users', 'Customer user')

    partner_id = fields.Many2one('res.partner', 'Customer')
    product_id = fields.Many2one('product.product', 'Product')
    lst_price = fields.Float('List price', digits=(16, 3))


class SaleOrder(models.Model):
    """ Model name: Sale order
    """
    _inherit = 'sale.order'

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    user_id = fields.Many2one('res.users', 'Customer user')
