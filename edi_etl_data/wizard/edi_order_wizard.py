# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import xlrd
import logging
import base64
import shutil
from odoo import models, fields, api
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class EdiOrderWizard(models.TransientModel):
    """ Model name: EDI Order wizard
    """
    _name = 'edi.order.wizard'
    _description = 'Extract pricelist wizard'

    @api.multi
    def export_pricelist(self):
        """ Export XLSX file for select product
        """
        report_pool = self.env['excel.report']

        partner = self.portal_partner_id

        pricelist_pool = self.env['res.partner.pricelist']
        pricelists = pricelist_pool.search([
            ('partner_id', '=', partner.id),
            ])

        title = (
            '',
            _('%s Pricelist article for purchase order') % partner.name,
            )

        header = ('ID', _('Code'), _('Name'), _('Price'), _('Purchase'))
        column_width = (1, 20, 40, 15, 12)

        ws_name = _('Pricelist order')
        report_pool.create_worksheet(ws_name, format_code='DEFAULT')
        report_pool.column_width(ws_name, column_width)

        # Title:
        report_pool.column_hidden(ws_name, [0])  # Hide first columns
        row = 0
        report_pool.write_xls_line(ws_name, row, title, style_code='title')

        # Header:
        row += 1
        report_pool.write_xls_line(ws_name, row, header, style_code='header')

        for pricelist in pricelists:
            product = pricelist.product_id
            row += 1
            report_pool.write_xls_line(ws_name, row, (
                pricelist.id,
                product.default_code,
                product.name,
                pricelist.lst_price,
                '',
            ), style_code='text')

        return report_pool.return_attachment('Pricelist_Purchase_Order')


    @api.multi
    def import_pricelist(self):
        """ Export Xlsx file for select product
        """

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    user_id = fields.Many2one(
        'res.users', 'User', required=True, default=lambda self: self.env.user)
    portal_partner_id = fields.Many2one(
        'res.partner', 'Portal Customer', related='user_id.portal_partner_id')
