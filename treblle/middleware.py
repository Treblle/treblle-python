from django.conf import settings
from django.urls import resolve
from functools import cached_property
import json
import time
import socket
import platform
import requests
import datetime
import json
import threading
import random
import re
import os
import gzip


class TreblleMiddleware(object):
	# Class-level cached server info (computed once, shared across instances)
	_server_info_cache = None
	_cache_lock = threading.Lock()
	
	# Class-level connection pooling (shared session across all instances)
	_session = None
	_session_lock = threading.Lock()
	
	# Default masked fields (class-level constant)
	DEFAULT_MASKED_FIELDS = ["password", "pwd", "secret", "password_confirmation", "passwordConfirmation", "cc", "card_number", "cardNumber", "ccv","ssn", "credit_score", "creditScore"]
	
	# Default payload size limit (10MB in bytes)  
	DEFAULT_MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB
	PAYLOAD_TOO_LARGE_MESSAGE = "Treblle can only capture payloads up to 10MB in size. This payload was too large to capture."
	
	@cached_property
	def max_payload_size(self):
		"""Get configurable payload size limit from settings"""
		custom_size = self.treblle_config.get('MAX_PAYLOAD_SIZE') or self.treblle_info_config.get('max_payload_size')
		if custom_size:
			try:
				return int(custom_size)
			except (ValueError, TypeError):
				if self.treblle_debug:
					self.treblle_print(f"Invalid MAX_PAYLOAD_SIZE setting: {custom_size}, using default 10MB")
		return self.DEFAULT_MAX_PAYLOAD_SIZE
	
	@cached_property
	def treblle_config(self):
		"""Lazy load Treblle configuration from settings"""
		try:
			return getattr(settings, 'TREBLLE', {})
		except (AttributeError, ImportError):
			return {}
	
	@cached_property
	def treblle_info_config(self):
		"""Lazy load legacy TREBLLE_INFO configuration from settings"""
		try:
			return getattr(settings, 'TREBLLE_INFO', {})
		except (AttributeError, ImportError):
			return {}
	
	@cached_property
	def treblle_sdk_token(self):
		"""Lazy load SDK token from settings"""
		return self.treblle_config.get('SDK_TOKEN', '') or self.treblle_info_config.get('api_key', '')
	
	@cached_property 
	def treblle_api_key(self):
		"""Lazy load API key from settings"""
		return self.treblle_config.get('API_KEY', '') or self.treblle_info_config.get('project_id', '')
	
	@cached_property
	def treblle_debug(self):
		"""Lazy load debug setting from settings"""
		return self.treblle_config.get('DEBUG', False) or self.treblle_info_config.get('debug', False)
	
	@cached_property
	def is_valid(self):
		"""Lazy validation of SDK configuration"""
		return bool(self.treblle_sdk_token and self.treblle_api_key)
	
	@cached_property
	def masked_fields(self):
		"""Lazy load and combine all masked fields"""
		# Start with default fields
		fields = set(field.lower().strip() for field in self.DEFAULT_MASKED_FIELDS)
		
		# Add ENV fields
		env_masked_fields = os.environ.get('TREBLLE_MASKED_FIELDS', '')
		if env_masked_fields:
			fields.update(field.lower().strip() for field in env_masked_fields.split(',') if field.strip())
		
		# Add settings fields
		settings_masked_fields = self.treblle_config.get('MASKED_FIELDS', []) or self.treblle_info_config.get('hidden_keys', [])
		if isinstance(settings_masked_fields, list):
			fields.update(field.lower().strip() for field in settings_masked_fields if field.strip())
		
		return fields
	@classmethod
	def get_server_info(cls):
		"""Get cached server information to avoid expensive system calls on every request"""
		if cls._server_info_cache is None:
			with cls._cache_lock:
				if cls._server_info_cache is None:  # Double-check locking
					try:
						hostname = socket.gethostname()
						host_ip = socket.gethostbyname(hostname)
						timezone = getattr(settings, 'TIME_ZONE', 'UTC')
						python_version = '.'.join(platform.python_version_tuple())
						
						cls._server_info_cache = {
							'ip': host_ip,
							'timezone': timezone,
							'python_version': python_version,
							'os_name': platform.system(),
							'os_release': platform.release(),
							'os_architecture': platform.machine()
						}
					except Exception:
						# Fallback if system calls fail
						cls._server_info_cache = {
							'ip': 'unknown',
							'timezone': 'UTC',
							'python_version': '3.x',
							'os_name': 'unknown',
							'os_release': 'unknown',
							'os_architecture': 'unknown'
						}
		return cls._server_info_cache

	@classmethod
	def get_session(cls):
		"""Get persistent HTTP session with connection pooling for better performance"""
		if cls._session is None:
			with cls._session_lock:
				if cls._session is None:  # Double-check locking
					cls._session = requests.Session()
					# Configure connection pooling adapter
					adapter = requests.adapters.HTTPAdapter(
						pool_connections=3,   # Number of connection pools (one per endpoint)
						pool_maxsize=10,      # Max connections per pool
						max_retries=0         # Disable retries for fire-and-forget approach
					)
					cls._session.mount('https://', adapter)
					cls._session.mount('http://', adapter)
		return cls._session

	def __init__(self, get_response):
		self.get_response = get_response
		
		# Initialize instance variables for thread safety
		self.start_time = None
		self.end_time = None
		
		# Configuration is now lazy-loaded via @cached_property
		# Only validate and show debug messages on first access
		if self.treblle_debug:
			if not self.is_valid:
				print('[TREBLLE DEBUG] Missing TREBLLE SDK_TOKEN or API_KEY in settings')
				if not self.treblle_sdk_token:
					print('[TREBLLE DEBUG] SDK_TOKEN is required - get it from your Treblle dashboard')
				if not self.treblle_api_key:
					print('[TREBLLE DEBUG] API_KEY is required - get it from your Treblle dashboard')
			else:
				print('[TREBLLE DEBUG] Treblle middleware successfully loaded and ready to capture API requests')

	def create_payload_structure(self):
		"""Create the payload structure for each request (instance method for thread safety)"""
		server_info = self.get_server_info()
		
		return {
			"api_key": self.treblle_sdk_token,
			"project_id": self.treblle_api_key,
			"version": "2.0.0",
			"sdk": "django",
			"data": {
				"server": {
					"ip": server_info['ip'],
					"timezone": server_info['timezone'],
					"software": "",
					"signature": "",
					"protocol": "",
					"os": {
						"name": server_info['os_name'],
						"release": server_info['os_release'],
						"architecture": server_info['os_architecture']
					}
				},
				"language": {
					"name": "python",
					"version": server_info['python_version'],
				},
				"request": {
					"timestamp": "",
					"ip": "",
					"url": "",
					"user_agent": "",
					"method": "",
					"headers": {},
					"body": {},
					"route_path": ""
				},
				"response": {
					"headers": {},
					"code": "",
					"size": "",
					"load_time": "",
					"body": {}
				},
				"errors": []
			}
		}
	
	def __call__(self, request):
		"""
		Default function to handle requests and responses
		"""
		if not self.is_valid:
			return self.get_response(request)
			
		self.start_time = time.time()
		request_body = request.body
		response = self.get_response(request)
		self.end_time = time.time()
		
		# Create fresh payload structure for this request (thread-safe)
		final_result = self.create_payload_structure()
		final_result['data']['request']['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		
		thread = threading.Thread(target=self.handle_request_and_response, args=(request, response, request_body, final_result))
		thread.start()
		return response
	
	def handle_request_and_response(self, request, response, request_body, final_result):
		"""
		Function to handle all the request and response
		"""
		self.handle_request(request, request_body, final_result)
		self.handle_response(request, response, final_result)
		
		# Calculate load time in milliseconds after response is fully processed
		load_time_ms = (self.end_time - self.start_time) * 1000
		final_result['data']['response']['load_time'] = round(load_time_ms, 2)
		
		# Pick up any stored exceptions from process_exception method
		if hasattr(request, '_treblle_exceptions'):
			final_result['data']['errors'].extend(request._treblle_exceptions)
		
		# Send to Treblle
		self.send_to_treblle(final_result)

	def handle_request(self, request, request_body, final_result):
		"""
		Function to handle each request
		"""
		# Server info is already populated from cache in create_payload_structure()
		final_result['data']['request']['method'] = request.method
		final_result['data']['server']['software'] = request.META.get('SERVER_SOFTWARE', 'SERVER_SOFTWARE_NOT_FOUND')
		final_result['data']['server']['protocol'] = request.META.get('SERVER_PROTOCOL', 'SERVER_PROTOCOL_NOT_FOUND')
		final_result['data']['request']['url'] = request.build_absolute_uri()
		final_result['data']['request']['user_agent'] = request.META.get('HTTP_USER_AGENT', 'HTTP_USER_AGENT_NOT_FOUND')
		
		# Extract route path
		try:
			resolved = resolve(request.path_info)
			route_pattern = resolved.route
			if route_pattern:
				# Convert Django URL patterns to OpenAPI format
				# <int:id> -> {id}, <uuid:uuid> -> {uuid}, etc.
				route_path = re.sub(r'<[^:]+:([^>]+)>', r'{\1}', str(route_pattern))
				final_result['data']['request']['route_path'] = route_path
			else:
				final_result['data']['request']['route_path'] = request.path_info
		except Exception as e:
			final_result['data']['request']['route_path'] = request.path_info
			if self.treblle_debug:
				self.treblle_print(f'Could not resolve route pattern: {e}')

		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		final_result['data']['request']['ip'] = ip

		if request.headers:
			# Ensure headers are a flat dict with lowercase keys (following HTTP convention)
			request_headers = {}
			for key, value in dict(request.headers).items():
				request_headers[key.lower()] = str(value)
			final_result['data']['request']['headers'] = self.mask_sensitive_data(request_headers)

		if request_body:
			# Check payload size limit
			if len(request_body) > self.max_payload_size:
				final_result['data']['request']['body'] = self.PAYLOAD_TOO_LARGE_MESSAGE
				if self.treblle_debug:
					self.treblle_print(f"Request body too large ({len(request_body)} bytes > {self.max_payload_size} bytes), replacing with size limit message")
			else:
				try:
					body = request_body.decode('utf-8')
					body = json.loads(body)
					if isinstance(body, (dict, list)):
						body = self.mask_sensitive_data(body)
					final_result['data']['request']['body'] = body
				except (json.JSONDecodeError, UnicodeDecodeError):
					# Only valid JSON is sent - ignore non-JSON request bodies
					if self.treblle_debug:
						self.treblle_print("Request body is not valid JSON, ignoring")

	def handle_response(self, request, response, final_result):
		"""
		Function to handle each response
		"""

		headers = {}
		try:

			if response.headers:
				headers = response.headers

		except Exception:
			try:
				if response._headers:
					headers = response._headers
			except Exception:
				pass
		
		if headers:
			# Ensure headers are a flat dict with lowercase keys (following HTTP convention)  
			response_headers = {}
			try:
				# Handle Django response headers format
				if hasattr(headers, 'items'):
					for key, value in headers.items():
						if isinstance(value, (list, tuple)) and len(value) > 0:
							# Django sometimes stores headers as tuples like ('Content-Type', 'application/json')
							response_headers[key.lower()] = str(value[0] if isinstance(value, (list, tuple)) else value)
						else:
							response_headers[key.lower()] = str(value)
				else:
					response_headers = dict(headers)
			except Exception:
				response_headers = {}
			
			final_result['data']['response']['headers'] = self.mask_sensitive_data(response_headers)
		else:
			final_result['data']['response']['headers'] = {}
		
		final_result['data']['response']['code'] = response.status_code

		if response.content:
			final_result['data']['response']['size'] = len(response.content)
			
			# Check payload size limit
			if len(response.content) > self.max_payload_size:
				final_result['data']['response']['body'] = self.PAYLOAD_TOO_LARGE_MESSAGE
				if self.treblle_debug:
					self.treblle_print(f"Response body too large ({len(response.content)} bytes > {self.max_payload_size} bytes), replacing with size limit message")
			else:
				try:
					body = response.content.decode('utf-8')
					body = json.loads(body)
					if isinstance(body, (dict, list)):
						body = self.mask_sensitive_data(body)
					final_result['data']['response']['body'] = body
				except (json.JSONDecodeError, UnicodeDecodeError):
					# Only valid JSON is sent - ignore non-JSON response bodies
					if self.treblle_debug:
						self.treblle_print("Response body is not valid JSON, ignoring")
		else:
			final_result['data']['response']['size'] = 0

	def send_to_treblle(self, final_result):
		"""
		Function to send the data to treblle with gzip compression for faster transfer
		"""
		json_body = json.dumps(final_result)
		treblle_headers = {
			'Content-Type': 'application/json',
			'X-API-Key': self.treblle_sdk_token,
			'Connection': 'keep-alive',
			'Keep-Alive': 'timeout=60, max=10'
		}
		treblle_endpoints = [
			'https://rocknrolla.treblle.com/',
			'https://punisher.treblle.com/',
			'https://sicario.treblle.com/'
		]
		treblle_url = random.choice(treblle_endpoints)
		
		# Attempt compression for faster data transfer
		request_data = json_body
		try:
			# Compress JSON payload with gzip
			compressed_data = gzip.compress(json_body.encode('utf-8'))
			# Only use compression if it actually reduces size (usually true for JSON > 1KB)
			if len(compressed_data) < len(json_body.encode('utf-8')):
				request_data = compressed_data
				treblle_headers['Content-Encoding'] = 'gzip'
				if self.treblle_debug:
					original_size = len(json_body.encode('utf-8'))
					compressed_size = len(compressed_data)
					compression_ratio = (1 - compressed_size / original_size) * 100
					self.treblle_print(f'Payload compressed: {original_size}B → {compressed_size}B ({compression_ratio:.1f}% reduction)')
			elif self.treblle_debug:
				self.treblle_print('Compression skipped: no size benefit for this payload')
		except Exception as e:
			# Fallback to uncompressed data if compression fails
			request_data = json_body
			if self.treblle_debug:
				self.treblle_print(f'Compression failed, using uncompressed data: {e}')
		
		try:
			session = self.get_session()
			treblle_request = session.post(url=treblle_url, data=request_data, headers=treblle_headers, timeout=5)
			
			if self.treblle_debug:
				self.treblle_print(f'Treblle request sent to: {treblle_url}')
				self.treblle_print(f'Treblle response code: {treblle_request.status_code}')
				
			# Check for 4xx or 5xx errors
			if treblle_request.status_code >= 400:
				if self.treblle_debug:
					self.treblle_print(f'[TREBLLE ERROR] HTTP {treblle_request.status_code} - {treblle_request.text}')
					if treblle_request.status_code == 401:
						self.treblle_print('[TREBLLE ERROR] Unauthorized - check your SDK_TOKEN')
					elif treblle_request.status_code == 403:
						self.treblle_print('[TREBLLE ERROR] Forbidden - check your API_KEY permissions')
					elif treblle_request.status_code >= 500:
						self.treblle_print('[TREBLLE ERROR] Server error - Treblle service may be temporarily unavailable')
			else:
				if self.treblle_debug:
					self.treblle_print('[TREBLLE DEBUG] Data successfully sent to Treblle')
					
		except requests.exceptions.RequestException as e:
			if self.treblle_debug:
				self.treblle_print(f'[TREBLLE ERROR] Failed to send data to Treblle: {e}')
		except Exception as e:
			if self.treblle_debug:
				self.treblle_print(f'[TREBLLE ERROR] Unexpected error: {e}')
	
	def mask_sensitive_data(self, data):
		"""
		Efficiently mask sensitive data in dict/list structures
		"""
		if isinstance(data, dict):
			for key, value in data.items():
				if key.lower() in self.masked_fields:
					data[key] = '*' * len(str(value)) if value is not None else '***'
				elif isinstance(value, (dict, list)):
					data[key] = self.mask_sensitive_data(value)
		elif isinstance(data, list):
			for i, item in enumerate(data):
				if isinstance(item, (dict, list)):
					data[i] = self.mask_sensitive_data(item)
		return data

	def treblle_print(self, print_value):
		if self.treblle_debug:
			print(f'[TREBLLE DEBUG] {print_value}')
	
	def process_exception(self, request, exception):
		"""
		Default function to handle exceptions - Django middleware callback
		Note: This method is called by Django's middleware system outside our normal flow
		Since we can't access the final_result here, we'll store exception data on the request
		"""
		if not self.is_valid:
			return None
			
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

		if file_name and line_number and exception:
			# Store exception data on request object to be picked up later
			if not hasattr(request, '_treblle_exceptions'):
				request._treblle_exceptions = []
			request._treblle_exceptions.append({
				'message': str(exception), 
				'file': file_name, 
				'line': line_number,
				'source': 'onException', 
				'type': 'UNHANDLED_EXCEPTION'
			})

		return None