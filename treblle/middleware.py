from django.conf import settings
import json
import time
import socket
import platform
import requests
import datetime
import json
import threading


class TreblleMiddleware(object):

	start_time = ''
	end_time = ''
	valid = True
	hidden_json_keys = ["password", "pwd", "secret", "password_confirmation", "passwordConfirmation", "cc", "card_number", "cardNumber", "ccv","ssn",
	"credit_score", "creditScore",]

	"""
	Get treblle api and project key from settings.py
	"""
	treblle_api_key = settings.TREBLLE_INFO.get('api_key', '')
	treblle_project_id = settings.TREBLLE_INFO.get('project_id', '')
	treblle_hidden_keys = settings.TREBLLE_INFO.get('hidden_keys', [])
	if not treblle_project_id or not treblle_api_key:
		valid = False
		if settings.DEBUG:
			print('treblle', 'no treblle api key or project id in setting file')

	if type(treblle_hidden_keys) == list:
		hidden_json_keys+= treblle_hidden_keys
	
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
			"errors": []
		}

	}

	def __init__(self, get_response):
		self.get_response = get_response

	
	def __call__(self, request):
		"""
		Default function to handle requests and responses
		"""

		self.start_time = time.time()
		self.final_result['data']['request']['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		request_body = request.body
		response = self.get_response(request)
		self.end_time = time.time()
		self.final_result['data']['response']['load_time'] = self.end_time - self.start_time
		thread = threading.Thread(target=self.handle_request_and_response, args=(request, response, request_body))
		thread.start()
		return response
	
	def handle_request_and_response(self, request, response, request_body):
		"""
		Function to handle all the request and response
		"""
		self.handle_request(request, request_body)
		self.handle_response(request, response)

	def handle_request(self, request, request_body):
		"""
		Function to handle each request
		"""
		hostname = socket.gethostname()
		host_ip = socket.gethostbyname(hostname)
		self.final_result['data']['server']['ip'] = host_ip
		self.final_result['data']['server']['timezone'] = settings.TIME_ZONE
		self.final_result['data']['request']['method'] = request.method
		self.final_result['data']['server']['software'] = request.META.get('SERVER_SOFTWARE', 'SERVER_SOFTWARE_NOT_FOUND')
		self.final_result['data']['server']['protocol'] = request.META.get('SERVER_PROTOCOL', 'SERVER_PROTOCOL_NOT_FOUND')
		self.final_result['data']['language']['version'] = '.'.join(platform.python_version_tuple())
		self.final_result['data']['server']['os']['name'] = platform.system()
		self.final_result['data']['server']['os']['release'] = platform.release()
		self.final_result['data']['server']['os']['architecture'] = platform.machine()
		self.final_result['data']['request']['url'] = request.build_absolute_uri()
		self.final_result['data']['request']['user_agent'] = request.META.get('HTTP_USER_AGENT', 'HTTP_USER_AGENT_NOT_FOUND')

		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		self.final_result['data']['request']['ip'] = ip

		if request.headers:
			self.final_result['data']['request']['headers'] = self.go_through_json(dict(request.headers))

		if request_body:
			try:
				body = request_body.decode('utf-8')
				body = json.loads(body)
				if isinstance(body, dict):
					body = self.go_through_json(body)
				elif isinstance(body, list):
					body = self.go_through_list(body)
				self.final_result['data']['request']['body'] = body
			except Exception as E:
				self.valid = False
				self.treblle_print(E)

	def handle_response(self, request, response):
		"""
		Function to handle each response
		"""

		headers = {}
		try:

			if response.headers:
				headers = request.headers

		except Exception:
			try:
				if response._headers:
					headers = response._headers
			except Exception:
				pass
		
		if headers:
			self.final_result['data']['response']['headers'] = self.go_through_json(dict(headers))
		else:
			self.final_result['data']['response']['headers'] = headers
		
		self.final_result['data']['response']['code'] = response.status_code

		if response.content:
			body = response.content.decode('utf-8')
			try:
				body = json.loads(body)
				self.final_result['data']['response']['size'] = len(body)
				if isinstance(body, dict):
					body = self.go_through_json(body)
				elif isinstance(body, list):
					body = self.go_through_list(body)
				self.final_result['data']['response']['body'] = body
			except Exception as E:
				self.treblle_print(E)
		else:
			self.valid = False

		if self.valid:
			self.send_to_treblle()

	def send_to_treblle(self):
		"""
		Function to send the data to treblle
		"""
		json_body = json.dumps(self.final_result)
		treblle_headers = {'Content-Type': 'application/json',
						'X-API-Key': self.treblle_api_key}
		treblle_request = requests.post(url='https://rocknrolla.treblle.com/', data=json_body, headers=treblle_headers, timeout=2)
		self.treblle_print(f'Trebble response code {treblle_request.status_code}')
		self.treblle_print(f'Trebble response content {treblle_request.content}')
	
	def go_through_json(self, json_example):
		for key, value in json_example.items():
			if isinstance(value, dict):
				self.go_through_json(value)
			elif isinstance(value, list):
				try:
					for item in value:
						if key.lower() in self.hidden_json_keys:
							json_example[key][item] = '*' * len(str(item))
						self.go_through_json(item)
				except Exception as e:
					for item in range(len(value)):
						if key.lower() in self.hidden_json_keys:
							json_example[key][item] = '*' * len(str(item))
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

	def treblle_print(self, print_value):
		if settings.DEBUG:
			print('treblle', print_value)
	
	def process_exception(self, request, exception):
		"""
		default function to handle exceptions
		"""
		
		trace_back = exception.__traceback__
		trace = []
		while trace_back is not None:
			trace.append({
				"filename": trace_back.tb_frame.f_code.co_filename,
				"linenumber": trace_back.tb_lineno
			})
			trace_back = trace_back.tb_next
		file_name = trace[-1]['filename']
		line_number = trace[-1]['linenumber']

		if len(self.final_result['data']['errors']) == 0 and file_name and  line_number and exception:
			self.final_result['data']['errors'].append({'message' : str(exception), 'source' : 'onException', 'type': 'UNHANDLED_EXCEPTION', 'file': file_name, 'line': line_number})

		return None