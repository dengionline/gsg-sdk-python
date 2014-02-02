"""
Usage:

= Create client object:

client = GSGClient(project_id, secret)

or, if you set in settings.py file:

client = GSGClient()


= Check available payment systems:

response = client.paysystems()

= Check your balance

response = client.main_balance()

= Look at error description list

response = client.errors()

= Create pre-pay checking of payment possibilities

response = client.check(
	txn_id = 0,
	paysystem = 7,
	account = '9522771693',
	amount = 1,
	currency = 'RUB'
)

= Initiate payment by your txn_id and invoice, which you get view "check"-request

response = client.pay(invoice = 20340387, txn_id = 0)

or

response = client.pay(20340387, 0)

= Check payment status

response = client.pay_status(20340387, 0)

* More information look in gsgclient.client *

"""

from gsgclient.client import GSGClient

client = GSGClient()

response = client.check(
	txn_id = 0,
	paysystem = 7,
	account = '9522771693',
	amount = 1,
	currency = 'RUB'
)

print(response)