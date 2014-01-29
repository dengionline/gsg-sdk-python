__author__ = 'k.chukhlomin@gmail.com'

import calendar
import time
import json
import requests
import hashlib

import gsgclient.settings as settings

class Client():

	project = False
	secret = False

	def __init__(self, project, secret):
		self.project = project
		self.secret = secret

	def check(self, txn_id, paysystem, account, **kwargs):

		params = {'txn_id': txn_id,
				  'paysystem': paysystem,
				  'account' :account}

		params.update(kwargs)

		return self.send('check', params)

	def pay(self, invoice, txn_id, **kwargs):

		params = {'invoice': invoice,
				  'txn_id': txn_id}

		params.update(kwargs)

		return self.send('pay', params)

	def pay_status(self, invoice, txn_id):

		return self.send(
			'pay_status',
			{'invoice' : invoice, 'txn_id' : txn_id}
		)

	def main_balance(self):

		return self.send('main_balance')

	def paysystems(self):

		return self.send('paysystems')

	def errors(self):

		return self.send('errors')

	def send(self, action, params = {}):

		response = requests.post(
			settings.endpoint,
			json.dumps(self.get_request_body(action, params))
			)

		response = response.json()['response'][0]

		return response

	def get_request_body(self, action, params):

		request_body = {
			'project' : self.project,
			'timestamp' : calendar.timegm(time.localtime()),
			'action' : action,
			'params' : params
		}

		request_body.update({'sign' : self.get_sign(request_body)})

		return request_body

	def get_sign(self, request_body):

		hash = hashlib.md5(
			str(request_body['timestamp']) +
			str(self.project) +
			request_body['action'] +
			self.get_params_stringify(request_body['params']) +
			self.secret
		)

		return hash.hexdigest()

	def get_params_stringify(self, params):

		params_keys = params.keys()
		params_keys = sorted(params_keys)

		params_str = ''

		for param_key in params_keys:
			params_str += str(params[param_key])

		return params_str

