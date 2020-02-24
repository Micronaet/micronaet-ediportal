# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import xlsxwriter
import xlrd
import logging
import base64
import shutil
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class EdiOrderWizard(models.Model):
    """ Model name: EDI Order wizard
    """
    _inherit = 'edi.order.wizard'

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    user_id = fields.Many2one(
        'res.users', 'User', required=True, default=lambda self: self.env.user)
    portal_partner_id = fields.Many2one(
        'res.partner', 'Portal Customer', related='user_id.portal_partner_id')
