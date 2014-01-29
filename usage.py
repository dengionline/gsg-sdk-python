__author__ = 'k.chukhlomin@gmail.com'

from gsgclient.client import Client as GSGClient

client = GSGClient(1290, 'secret')

response = client.check(txn_id = 0,
			 paysystem = 1,
			 account = '+79522771693',
			 amount = 1,
			 currency = 'RUB')

# response = client.pay(invoice = 0, txn_id = 2)

# response = client.paysystems()

# response = client.main_balance()

# response = client.errors()

print(response)

