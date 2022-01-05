from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import json
import time
import socket
import platform
import requests
import datetime
import json
import threading


class TreblleMiddleware(MiddlewareMixin):

	start_time = ''
	end_time = ''
	valid = True
	hidden_json_keys = ['card_number','credit_card', 'cvv', 'expiry_date', 'number', 'pin', 'token', 'transaction_id', 'transaction_reference', 'job_name', 'hello', 'password']

	"""
	Get treblle api and project key from settings.py
	"""
	try:
		treblle_api_key = settings.TREBLLE_API_KEY
		treblle_project_id = settings.TREBLLE_PROJECT_ID
	except:
		valid = False
		if settings.DEBUG:
			print('no treblle api key or project id in setting file')

	if type(settings.TREBLLE_HIDDEN_JSON_KEYS) == list:
		hidden_json_keys+= settings.TREBLLE_HIDDEN_JSON_KEYS
	
	hidden_json_keys = list(x.lower() for x in  hidden_json_keys)
	"""
	set structure of final_result
	"""
	final_result = {
		"api_key": treblle_api_key,
		"project_id": treblle_project_id,
		"version": 0.6,
		"sdk": "django",
		"data": {
			"server": {
				"ip": "",
				"timezone": "",
				"software": "",
				"signature": "",
				"protocol": "",
				"os": {
					"name": "",
					"release": "",
					"architecture": ""

				}
			},
			"language": {
				"name": "python",
				"version": "",
			},
			"request": {
				"timestamp": "",
				"ip": "",
				"url": "",
				"user_agent": "",
				"method": "",
				"headers": {

				},
				"body": {

				}
			},
			"response": {
				"headers": {
				},
				"code":	"",
				"size": "",
				"load_time": "",
				"body": {
				}
			},
			"errors": [
			]
		}

	}

	def handle_request(self, request):
		"""
		Function to handle each request

		param request: request object
		"""
		self.start_time = time.time()
		self.final_result['data']['request']['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		hostname = socket.gethostname()
		host_ip = socket.gethostbyname(hostname)
		self.final_result['data']['server']['ip'] = host_ip
		self.final_result['data']['server']['timezone'] = settings.TIME_ZONE
		self.final_result['data']['request']['method'] = request.method
		self.final_result['data']['server']['software'] = request.META['SERVER_SOFTWARE']
		self.final_result['data']['server']['protocol'] = request.META['SERVER_PROTOCOL']
		self.final_result['data']['language']['version'] = '.'.join(platform.python_version_tuple())
		self.final_result['data']['server']['os']['name'] = platform.system()
		self.final_result['data']['server']['os']['release'] = platform.release()
		self.final_result['data']['server']['os']['architecture'] = platform.machine()
		self.final_result['data']['request']['url'] = request.build_absolute_uri()
		self.final_result['data']['request']['user_agent'] = request.META['HTTP_USER_AGENT']

		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		self.final_result['data']['request']['ip'] = ip

		if request.headers:
			self.final_result['data']['request']['headers'] = self.go_through_json(dict(request.headers))

		if request.body:
			try:
				body = request.body.decode('utf-8')
				body = json.loads(body)
				if isinstance(body, dict):
					body = self.go_through_json(body)
					print('dict')
				elif isinstance(body, list):
					body = self.go_through_list(body)
					print(body)
				self.final_result['data']['request']['body'] = body
			except Exception as E:
				self.valid = False
				if settings.DEBUG:
					print(E)

	def process_request(self, request):
		"""
		Defualt function to handle each request
		"""
		self.handle_request(request)

	def handle_response(self, request, response):
		"""
		Function to handle each response
		"""
		self.end_time = time.time()
		self.final_result['data']['response']['load_time'] = self.end_time - self.start_time

		if response.headers:
			self.final_result['data']['response']['headers'] = self.go_through_json(dict(response.headers))

		if response.content:
			body = response.content.decode('utf-8')
			try:
				body = json.dumps(body)
				body = json.loads(body)
				self.final_result['data']['response']['size'] = len(body)
				if isinstance(body, dict):
					body = self.go_through_json(body)
				elif isinstance(body, list):
					body = self.go_through_list(body)
				self.final_result['data']['response']['body'] = body
				self.final_result['data']['response']['code'] = response.status_code
			except Exception as E:
				self.valid = False
				if settings.DEBUG:
					print(E)
		else:
			self.valid = False

		if self.valid:
			json_body = json.dumps(self.final_result)
			treblle_headers = {'Content-Type': 'application/json',
							'X-API-Key': self.treblle_api_key}
			treblle_request = requests.post(url='https://rocknrolla.treblle.com/', data=json_body, headers=treblle_headers)
			if settings.DEBUG:
				print(f'Trebble response code {treblle_request.status_code}')
				print(f'Trebble response content {treblle_request.content}')

	def process_response(self, request, response):
		"""
		Defualt function to handle each response
		"""
		thread = threading.Thread(target=self.handle_response, args=(request, response,))
		thread.start()

		return response

	
	def go_through_json(self, json_example):
		for key, value in json_example.items():
			if isinstance(value, dict):
				self.go_through_json(value)
			elif isinstance(value, list):
				try:
					for item in value:
						self.go_through_json(item)
				except Exception as e:
					for item in range(len(value)):
						if key.lower() in self.hidden_json_keys:
							json_example[key][item] = '*' * len(value)
			else:
				if key.lower() in self.hidden_json_keys:
					json_example[key] = '*' * len(str(value))
		return json_example

	
	def go_through_list(self, list_example):
		for item in list_example:
			if isinstance(item, dict):
				self.go_through_json(item)
			elif isinstance(item, list):
				self.go_through_list(item)
		return list_example