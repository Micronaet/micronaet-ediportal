# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import erppeek
import xlrd
import xlsxwriter
import ConfigParser

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
# From config file:
cfg_filename = os.path.expanduser('~/openerp.cfg')
cfg_file = os.path.expanduser(cfg_filename)

# -----------------------------------------------------------------------------
# Utility:
# -----------------------------------------------------------------------------
def get_text(value):
    """ Extract clean text
    """
    res = ''
    for c in value.strip():
        if ord(c) < 127:
            res += c
        else:
            res += '#'   
            
    return res

def get_float(value):
    """ Extract fload from text
    """
    value = (value or '').strip()
    value = value.replace(',', '.')
    try:  
        return float(value)
    except:
        print 'Error convert to float: %s' % value
        return 0.0    

print 'Read parameters from: %s' % cfg_filename
config = ConfigParser.ConfigParser()
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
pricelist_pool = odoo.model('res.partner.pricelist')

# -----------------------------------------------------------------------------
# Customer:
# -----------------------------------------------------------------------------
partner_db = {}

i = 0
print 'Read Customer CSV file: %s' % customer_csv

#file_data = pandas.read_csv(customer_csv, encoding='unicode_escape')
file_data = open(customer_csv, 'r')
for line in file_data:
    i += 1
    
    # Columns:
    row = line.split(';')
    customer_code = get_text(row[0])
    name = get_text(row[7]) 

    if customer_code in partner_db:
        partner_id = partner_db[customer_code]
    else:
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
            print '%s. Update partner %s' % (i, name)
            partner_pool.write(partner_ids, data)
            partner_id = partner_ids[0]
        else:    
            print '%s. Create partner %s' % (i, name)
            partner_id = partner_pool.create(data).id
        if customer_code not in partner_db:
            partner_db[customer_code] = partner_id
        
    # -------------------------------------------------------------------------
    # Destination:
    # -------------------------------------------------------------------------
    # Columns: 
    destination_code = get_text(row[1])
    street = get_text(row[2])
    zip_code = get_text(row[3])    
    city = get_text(row[4])
    name = get_text(row [6])
    
    # Create record:    
    data = {
        'parent_id': partner_id,
        'etl_import': True,
        'destination_code': destination_code,
        'street': street,
        'zip': zip_code,
        'city': city,
        'name': name,
        'type': 'delivery',
        }

    # Search destination name:    
    destination_ids = partner_pool.search([
        ('destination_code', '=', destination_code),
        ('etl_import', '=', True),
        ])
        
    if destination_ids:
        print '   Update destination %s' % name
        partner_pool.write(destination_ids, data)
        destination_id = destination_ids[0]
    else:    
        print '   Create destination %s' % name
        destination_id = partner_pool.create(data).id

# -----------------------------------------------------------------------------
# Price list (product):
# -----------------------------------------------------------------------------
i = 0
print 'Read Pricelist CSV file: %s' % pricelist_csv
for line in open(pricelist_csv, 'r'):    
    i += 1
    
    # Columns:
    row = line.split(';')
    customer_code = get_text(row[0])
    default_code = get_text(row[1])
    product_name = get_text(row[2])
    lst_price = get_float(row[4])
    # TODO UOM

    # -------------------------------------------------------------------------
    # Search customer:    
    # -------------------------------------------------------------------------
    partner_ids = partner_pool.search([
        ('customer_code', '=', customer_code),
        ])
        
    if partner_ids:
        partner_id = partner_ids[0]
    else:    
        print '%s. Partner code not found: %s' % (i, customer_code)
        continue
        
    # -------------------------------------------------------------------------
    # Search product: 
    # -------------------------------------------------------------------------
    product_ids = product_pool.search([
        ('default_code', '=', default_code),
        ])

    if product_ids:
        product_id = product_ids[0]
    else:    
        print '%s. Create product %s\n' % (i, default_code)
        product_id = product_pool.create({
            'default_code': default_code,
            'name': product_name,
            }).id
        
    pricelist_ids = pricelist_pool.search([
        ('partner_id', '=', partner_id),
        ('product_id', '=', product_id),
        ])

    data = {
        'partner_id': partner_id,
        'product_id': product_id,
        'lst_price': lst_price,
        }        
    if pricelist_ids:
        pricelist_pool.write(pricelist_ids, data)
        print '%s. Pricelist: %s - %s updated' % (
            i, customer_code, default_code)
    else:    
        pricelist_pool.create(data)
        print '%s. Pricelist: %s - %s created' % (
            i, customer_code, default_code)

           
