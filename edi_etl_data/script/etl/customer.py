# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import erppeek
import xlrd
import xlsxwriter
import configparser

import pdb; pdb.set_trace()
# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
# Parameters:
file_csv = './data/customer.csv'

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

# -----------------------------------------------------------------------------
# Customer:
# -----------------------------------------------------------------------------
i = 0
print('Read Customer CSV file: %s' % customer_csv)
for row in open(customer_csv, 'r'):    
    i += 1
    
    # Columns:
    name = row[:50]

    # Create record:    
    data = {
        'name': name,
        'etl_import': True
        }

    # Search partner name:    
    partner_ids = partner_pool.search([
        ('name', '=', name),
        ('etl_import', '=', True),
        ])
        
    if partner_ids:
        print('%s. Update partner %s\n' % (i, name))
        # partner_pool.write(partner_ids, data)
    else:    
        print('%s. Create partner %s\n' % (i, name))        
        # partner_pool.create(data)


