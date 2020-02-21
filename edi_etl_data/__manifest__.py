# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'EDI Portal ETL',
    'version': '11.0.2.0.0',
    'category': 'EDI',
    'description': '''
        EDI Portal EDL data exchange
        ''',
    'summary': 'EDI, ETL, data',
    'author': 'Micronaet S.r.l. - Nicola Riolini',
    'website': 'http://www.micronaet.it',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/edi_view.xml',
        #'data/color_data.xml',        
        ],
    'external_dependencies': {
        'python': ['xlsxwriter', 'xlrd', 'erppeek'],
        },
    'application': False,
    'installable': True,
    'auto_install': False,
    }
