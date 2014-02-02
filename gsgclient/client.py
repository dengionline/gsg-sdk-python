import calendar
import time
import json
import requests
import hashlib

import gsgclient.settings as settings

class GSGClient():
	"""
	GSG Client

	You can find protocol at http://dengionline.com/dev/protocol/gsg_protocol
	"""

	project = False
	secret = False

	def __init__(self, project=0, secret=''):

		if project == 0:
			self.project = settings.project
		else:
			self.project = project

		if secret == '':
			self.secret = settings.secret
		else:
			self.secret = secret

	def check(self, txn_id, paysystem, account, **kwargs):
		"""
		Pre-pay request for checking payment possibilities.
		You may send some additional params:
		* amount - amount of payment
		* currency - currency of amount

		Response must contain:
		* invoice - identifier, use this in "pay" and "pay_status" request
		* income currency - amount and currency of payment as described in request
		* amount currency - amount and currency of payment in project's balance currency
		* outcome currency - amount and currency of payment in PS currency
		* rate - conversion courses
			income - from "income" to "amount" currency
			outcome - from "amount" to "outcome" currency
			total - result, from "income" to "outcome" currency

		More information at http://dengionline.com/dev/protocol/gsg_check
		"""

		params = {
			'txn_id': txn_id,
			'paysystem': paysystem,
			'account' : account
		}

		params.update(kwargs)

		return self.send('check', params)

	def pay(self, invoice, txn_id, **kwargs):
		"""
		Request for the payment.
		You need also send "amount" and "currency" if they wasn't sent in "check"-request.

		Server response consist of several fields:
		* income - amount of payment in it's currency, described in check
		* rate - course of currency conversion (from income to outcome)
		* amount - amount of payment in currency of main project balance
		* outcome - amount of payment in PS currency
		* fee - % of commission for project's payment in it's PS

		Important! For one invoice you can send "pay"-request only at once.

		More information at http://dengionline.com/dev/protocol/gsg_pay
		"""
		params = {
			'invoice': invoice,
			'txn_id': txn_id
		}

		params.update(kwargs)

		return self.send('pay', params)

	def pay_status(self, invoice, txn_id):
		"""
		Getting information about transaction status by its identifier.
		Following fields in response:

		* pay_status - status of transaction. One from the list:
			* new - new transaction, not processed,
			* processing - transaction processing now,
			* pending - transaction waiting in queue,
			* paid - transaction paid to customer,
			* error - error occurred while processing
		* rate - course of currency conversion (from income to outcome)
		* income - amount of payment in it's currency, described in check
			* amount
			* currency
		* amount - amount of payment in currency of main project balance
			* amount
			* currency
		* outcome - amount of payment in PS currency
			* amount
			* currency
		* fee - % of commission for project's payment in it's PS
		* ts_create - date of creation of invoice in MySQL datetime format
		* ts_close - date of payout to PS in MySQL datetime format

		Only "pay_status" is always in response.

		More information at http://dengionline.com/dev/protocol/gsg_pay_status
		"""

		return self.send('pay_status', {'invoice': invoice, 'txn_id': txn_id})

	def main_balance(self):
		"""
		Getting current balance. Response should contain:

		* balance - project balance in its base currency
		* currency - base currency in ISO 4217

		More information at http://dengionline.com/dev/protocol/gsg_main_balance
		"""

		return self.send('main_balance')

	def paysystems(self):
		"""
		Getting all available payment systems and its parameters:

		* id - payments system (PS) identifier
		* tag - or alias - identifier too
		* title - the title of PS
		* jname - juditial name of PS
		* region - identifier of PS currency
		* min_amount - minimum amount of payment in PS currency
		* max_amount - maximum amount of payment in PS currency
		* account_name - hint of what we expect to see in "account" field in "check"-request
		* account_regexp - regular expression, must be match the "account" field
		* currency_id - PS currency in ISO 4217
		* params - some additional params, that needed in "check/pay" request.
			Each parameter has attributes like:
			* name - name of parameter, for example: "Full name" for MCMS payments
			* descr - description of parameter
			* regexp - regular expression for checking parameter

		More information at http://dengionline.com/dev/protocol/gsg_paysystems
		"""

		return self.send('paysystems')

	def errors(self):
		"""
		Getting list of possible error codes and it's description.

		The most common error codes:
		12 - wrong request format, some required fields missing
		16 - mon enough money on balance
		19 - not valid account-field
		23 - error in PS-side
		24 - transaction with same id already exists
		27 - amount is less then minimal for this PS
		28 - amount is bigger then maximum for this PS
		31 - incorrect sign
		1000 - internal error

		More information at http://dengionline.com/dev/protocol/gsg_errors
		"""

		return self.send('errors')

	def send(self, action, params = {}):

		try:
			response = requests.post(
				settings.endpoint,
				json.dumps(self.get_request_body(action, params))
			)

			response = response.json()['response'][0]
			return response

		except requests.ConnectionError:
			print("A Connection error occurred.")
			return False

		except requests.HTTPError:
			print("An HTTP error occurred.")
			return False

		except requests.Timeout:
			print("The request timed out.")
			return False

		except requests.RequestException:
			print("There was an ambiguous exception that occurred while handling your request.")
			return False

		except ValueError:
			print("Unexpected response format.")
			return False

		except Exception:
			print("Unknown exception.")
			return False

	def get_request_body(self, action, params):

		request_body = {
			'project' : self.project,
			'timestamp' : calendar.timegm(time.localtime()),
			'action' : action,
			'params' : params
		}

		request_body.update({'sign' : self.get_sign(request_body)})

		if not request_body['params']:
			request_body.pop('params')

		return {"request": request_body}

	def get_sign(self, request_body):

		hash = hashlib.md5(
			str(request_body['timestamp']) +
			str(self.project) +
			request_body['action'] +
			GSGClient.get_params_stringify(request_body['params']) +
			self.secret
		)

		return hash.hexdigest()

	@staticmethod
	def get_params_stringify(params):

		if not params:
			return ''

		params_keys = params.keys()
		params_keys = sorted(params_keys)

		params_str = ''

		for param_key in params_keys:
			params_str += str(params[param_key])

		return params_str