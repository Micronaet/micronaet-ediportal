# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

customer_csv = '/home/odoo/script/etl/data/testdestgfd.csv'

file_data = open(customer_csv, 'r')
i = 0 
for line in file_data:
    i += 1
    print i
    print(line)
    
