# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import erppeek
import xlrd
import xlsxwriter
import configparser


# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
# From config file:
cfg_filename = os.path.expanduser('~/openerp.cfg')
cfg_file = os.path.expanduser(cfg_filename)

print('Read parameters from: %s' % cfg_filename)
config = configparser.ConfigParser()
config.read([cfg_file])

dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

customer_csv = config.get('file', 'customer')
product_csv = config.get('file', 'product')
pricelist_csv = config.get('file', 'pricelist')

# -----------------------------------------------------------------------------
# Connect to ODOO:
# -----------------------------------------------------------------------------
odoo = erppeek.Client(
    'http://%s:%s' % (
        server, port), 
    db=dbname,
    user=user,
    password=pwd,
    )
    
# Pool used:
partner_pool = odoo.model('res.partner')
product_pool = odoo.model('product.template')

# -----------------------------------------------------------------------------
# Customer:
# -----------------------------------------------------------------------------

i = 0
print('Read Customer CSV file: %s' % customer_csv)
for line in open(customer_csv, 'r'):    
    i += 1
    
    # Columns:
    row = line.split(';')
    customer_code = row[0].strip()
    name = customer_code
    # Create record:    
    data = {
        'name': name,
        'etl_import': True,
        'customer_code': customer_code,
        'is_company': True,
        'customer' : True,
        
        }

    # Search partner name:    
    partner_ids = partner_pool.search([
        ('customer_code', '=', customer_code),
        ('etl_import', '=', True),
        ])
        
    if partner_ids:
        print('%s. Update partner %s\n' % (i, name))
        partner_pool.write(partner_ids, data)
        partner_id = partner_ids[0]
    else:    
        print('%s. Create partner %s\n' % (i, name))        
        partner_id = partner_pool.create(data).id

    # -----------------------------------------------------------------------------
    # Destination:
    # -----------------------------------------------------------------------------

    # Columns:
 
    destination_code = row[1].strip()
    street = row[2].strip()
    zip_code = row[3].strip()    
    city = row[4].strip()
    name = destination_code
    
    # Create record:    
    data = {
        'parent_id': partner_id,
        'name': name,
        'etl_import': True,
        'destination_code': destination_code,
        'street': street,
        'zip': zip_code,
        'city': city,
        'type': 'delivery',
        }

    # Search destination name:    
    destination_ids = partner_pool.search([
        ('destination_code', '=', destination_code),
        ('etl_import', '=', True),
        ])
        
    if destination_ids:
        print('%s. Update destination %s\n' % (i, name))
        partner_pool.write(destination_ids, data)
        destination_id = destination_ids[0]
    else:    
        print('%s. Create destination %s\n' % (i, name))        
        destination_id = partner_pool.create(data).id

