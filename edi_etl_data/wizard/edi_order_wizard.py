# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import xlrd
import logging
import base64
import shutil
from odoo import models, fields, api, exceptions
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

        for pricelist in sorted(
                pricelists,
                key=lambda x: x.product_id.default_code):
            product = pricelist.product_id
            row += 1
            report_pool.write_xls_line(ws_name, row, (
                pricelist.id,  # TODO change management with product
                product.default_code,
                product.name,
                (pricelist.lst_price, 'number'),
                ('', 'number'),
            ), style_code='text')

        return report_pool.return_attachment('Pricelist_Purchase_Order')

    @api.multi
    def import_pricelist(self):
        """ Export Xlsx file for select product
        """
        start_row = 1

        order_pool = self.env['sale.order']
        line_pool = self.env['sale.order.line']
        pricelist_pool = self.env['res.partner.pricelist']

        # ---------------------------------------------------------------------
        # Save passed file:
        # ---------------------------------------------------------------------
        b64_file = base64.decodebytes(self.file)
        now = ('%s' % fields.Datetime.now())[:19]
        filename = '/tmp/tx_%s.xlsx' % now.replace(':', '_').replace('-', '_')
        f = open(filename, 'wb')
        f.write(b64_file)
        f.close()

        # ---------------------------------------------------------------------
        # Open Excel file:
        # ---------------------------------------------------------------------
        try:
            WB = xlrd.open_workbook(filename)
        except:
            raise exceptions.Warning(_('Cannot read XLS file'))

        WS = WB.sheet_by_index(0)
        no_data = True
        start_import = False
        import pdb; pdb.set_trace()
        for row in range(start_row, WS.nrows):
            pricelist_id = WS.cell_value(row, 0)
            if pricelist_id == 'ID':
                start_import = True
                _logger.info('%s. Header line' % row)
                continue

            if not start_import:
                _logger.info('%s. Jump line' % row)
                continue

            lst_price = WS.cell_value(row, 3)
            product_qty = WS.cell_value(row, 4)

            if product_qty <= 0:
                _logger.info('%s. No quantity' % row)
                continue  # Jump empty line
            else:
                _logger.info('%s. Import line' % row)

            if no_data:
                no_data = False

                # -------------------------------------------------------------
                # Create sale order:
                # -------------------------------------------------------------
                order_id = order_pool.create({
                    'partner_id': self.portal_partner_id.id,
                    'user_id': self.user_id.id,
                    'date_order': now,
                    }).id

            # Create sale order line:
            pricelist = pricelist_pool.browse(pricelist_id)  # TODO use product
            product = pricelist.product_id
            line_pool.create({
                'order_id': order_id,
                'product_id': product.id,
                'name': product.name,
                'product_uom_qty': product_qty,
                'price_unit': lst_price,
                })
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    user_id = fields.Many2one(
        'res.users', 'User', required=True, default=lambda self: self.env.user)
    portal_partner_id = fields.Many2one(
        'res.partner', 'Portal Customer', related='user_id.portal_partner_id')
    file = fields.Binary('XLSX file', filters=None)
