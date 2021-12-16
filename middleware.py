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
			self.final_result['data']['request']['headers'] = dict(request.headers)

		if request.body:
			try:
				body = request.body
				body = json.loads(body)
				self.final_result['data']['request']['body'] = body
			except json.JSONDecodeError:
				self.valid = False
				if settings.DEBUG:
					print('json decode error')

	def process_request(self, request):
		"""
		Defualt function to handle each request
		"""
		thread = threading.Thread(target=self.handle_request, args=(request,))
		thread.start()

	def handle_response(self, request, response):
		"""
		Function to handle each response
		"""
		self.end_time = time.time()
		self.final_result['data']['response']['load_time'] = self.end_time - self.start_time

		if response.headers:
			self.final_result['data']['response']['headers'] = dict(response.headers)

		if response.content:
			body = response.content
			try:
				json_body = json.loads(body)
				self.final_result['data']['response']['size'] = len(body)
				self.final_result['data']['response']['body'] = json_body
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
