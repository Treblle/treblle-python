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
from concurrent.futures import ThreadPoolExecutor


class TreblleJSONEncoder(json.JSONEncoder):
	"""Custom JSON encoder that safely handles Django/Python objects that aren't JSON serializable"""
	
	def default(self, obj):
		# Handle datetime objects
		if hasattr(obj, 'isoformat'):  # datetime, date, time objects
			return obj.isoformat()
		
		# Handle Decimal objects
		elif hasattr(obj, '__float__'):
			try:
				return float(obj)
			except (ValueError, OverflowError):
				return str(obj)
		
		# Handle UUID objects
		elif hasattr(obj, 'hex'):  # UUID has hex attribute
			return str(obj)
		
		# Handle Django model instances (have _meta attribute)
		elif hasattr(obj, '_meta'):
			return f"<{obj.__class__.__name__}: {obj}>"
		
		# Handle file objects
		elif hasattr(obj, 'read') and hasattr(obj, 'name'):
			return f"<File: {getattr(obj, 'name', 'unknown')}>"
		
		# Handle bytes
		elif isinstance(obj, bytes):
			try:
				return obj.decode('utf-8')
			except UnicodeDecodeError:
				return f"<bytes: {len(obj)} bytes>"
		
		# Handle sets (convert to list)
		elif isinstance(obj, set):
			return list(obj)
		
		# Handle complex numbers
		elif isinstance(obj, complex):
			return {'real': obj.real, 'imag': obj.imag}
		
		# Fallback: try to get string representation
		try:
			return str(obj)
		except Exception:
			return f"<{obj.__class__.__name__}: non-serializable>"


class TreblleMiddleware(object):
	# Class-level cached server info (computed once, shared across instances)
	_server_info_cache = None
	_cache_lock = threading.Lock()
	
	# Class-level connection pooling (shared session across all instances)
	_session = None
	_session_lock = threading.Lock()
	
	# Class-level thread pool for background processing
	_thread_pool = None
	_thread_pool_lock = threading.Lock()
	
	# Default masked fields (class-level constant)
	DEFAULT_MASKED_FIELDS = ["password", "pwd", "secret", "password_confirmation", "passwordConfirmation", "cc", "card_number", "cardNumber", "ccv","ssn", "credit_score", "creditScore"]
	
	# Payload size limit constant (10MB in bytes)
	MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB
	PAYLOAD_TOO_LARGE_MESSAGE = "Treblle can only capture payloads up to 10MB in size. This payload was too large to capture."
	
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
	
	@cached_property
	def excluded_routes(self):
		"""Lazy load excluded routes from settings"""
		routes = self.treblle_config.get('EXCLUDED_ROUTES', []) or self.treblle_info_config.get('excluded_routes', [])
		if isinstance(routes, list):
			return [route.strip() for route in routes if route.strip()]
		return []
	
	def should_skip_route(self, path):
		"""Check if the current request path should be excluded from tracking"""
		if not self.excluded_routes:
			return False
		
		for pattern in self.excluded_routes:
			# Exact match
			if pattern == path:
				return True
			
			# Wildcard pattern matching
			if '*' in pattern:
				# Convert pattern to simple regex: * becomes .*
				import fnmatch
				if fnmatch.fnmatch(path, pattern):
					return True
		
		return False
	@classmethod
	def get_server_info(cls):
		"""Get cached server information to avoid expensive system calls on every request"""
		if cls._server_info_cache is None:
			with cls._cache_lock:
				if cls._server_info_cache is None:
					try:
						hostname = socket.gethostname()
						host_ip = socket.gethostbyname(hostname)
						timezone = getattr(settings, 'TIME_ZONE', 'UTC')
						python_version = '.'.join(platform.python_version_tuple())
						
						cls._server_info_cache = {
							'ip': host_ip,
							'timezone': timezone,
							'python_version': python_version,
							'os_name': platform.system() or None,
							'os_release': platform.release() or None,
							'os_architecture': platform.machine() or None
						}
					except Exception:
						# Fallback if system calls fail
						cls._server_info_cache = {
							'ip': 'unknown',
							'timezone': 'UTC',
							'python_version': '3.x',
							'os_name': None,
							'os_release': None,
							'os_architecture': None
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

	@classmethod
	def get_thread_pool(cls):
		"""Get shared thread pool for background processing to prevent memory leaks"""
		if cls._thread_pool is None:
			with cls._thread_pool_lock:
				if cls._thread_pool is None:  # Double-check locking
					cls._thread_pool = ThreadPoolExecutor(
						max_workers=10,  # Configurable limit to prevent resource exhaustion
						thread_name_prefix="treblle-worker-"
					)
		return cls._thread_pool

	@classmethod
	def cleanup_resources(cls):
		"""Cleanup shared resources - can be called during Django shutdown"""
		with cls._thread_pool_lock:
			if cls._thread_pool is not None:
				cls._thread_pool.shutdown(wait=True)  # Wait for pending tasks to complete
				cls._thread_pool = None
		
		with cls._session_lock:
			if cls._session is not None:
				cls._session.close()
				cls._session = None

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
					"method": "GET",
					"headers": {},
					"body": {},
					"query": {},
					"route_path": null
				},
				"response": {
					"headers": {},
					"code": 200,
					"size": 0,
					"load_time": 0,
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
		
		# Check if route should be excluded from tracking
		if self.should_skip_route(request.path_info):
			if self.treblle_debug:
				self.treblle_print(f"Skipping route: {request.path_info}")
			return self.get_response(request)
			
		self.start_time = time.time()
		request_body = request.body
		response = self.get_response(request)
		self.end_time = time.time()
		
		# Create fresh payload structure for this request (thread-safe)
		final_result = self.create_payload_structure()
		final_result['data']['request']['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		
		# Use thread pool to prevent memory leaks from unlimited thread creation
		thread_pool = self.get_thread_pool()
		thread_pool.submit(self.handle_request_and_response, request, response, request_body, final_result)
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
		
		# Pick up any stored exceptions from process_exception method (thread-safe)
		exceptions = getattr(request, '_treblle_exceptions', [])
		if exceptions:
			final_result['data']['errors'].extend(exceptions)
		
		# Send to Treblle
		self.send_to_treblle(final_result)

	def safe_json_dumps(self, data):
		"""Safely serialize data to JSON with comprehensive error handling"""
		try:
			# First attempt with custom encoder
			return json.dumps(data, cls=TreblleJSONEncoder, ensure_ascii=False, separators=(',', ':'))
		except (TypeError, ValueError, RecursionError, OverflowError) as e:
			# Log the error if debug mode is enabled
			if self.treblle_debug:
				self.treblle_print(f"JSON serialization failed: {type(e).__name__}: {e}")
			
			# Return minimal safe payload to ensure Treblle still gets some data
			try:
				fallback_payload = {
					"api_key": self.treblle_sdk_token,
					"project_id": self.treblle_api_key,
					"version": "2.0.0",
					"sdk": "django",
					"data": {
						"server": {"ip": "unknown", "timezone": "UTC", "software": None, "signature": "", "protocol": None, "os": {"name": None, "release": None, "architecture": None}},
						"language": {"name": "python", "version": "3.x"},
						"request": {"timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "ip": "", "url": "", "user_agent": "", "method": "GET", "headers": {}, "body": {}, "query": {}, "route_path": None},
						"response": {"headers": {}, "code": 200, "size": 0, "load_time": 0, "body": {}},
						"errors": [{"message": f"JSON serialization failed: {type(e).__name__}: {str(e)}", "file": "treblle/middleware.py", "line": 0, "source": "jsonSerialization", "type": "SERIALIZATION_ERROR"}]
					}
				}
				return json.dumps(fallback_payload, ensure_ascii=False, separators=(',', ':'))
			except Exception as fallback_error:
				# Ultimate fallback - return minimal JSON string
				if self.treblle_debug:
					self.treblle_print(f"Fallback JSON serialization also failed: {fallback_error}")
				return '{"error":"critical_json_serialization_failure"}'

	def handle_request(self, request, request_body, final_result):
		"""
		Function to handle each request
		"""
		# Server info is already populated from cache in create_payload_structure()
		final_result['data']['request']['method'] = request.method
		final_result['data']['server']['software'] = request.META.get('SERVER_SOFTWARE') or None
		final_result['data']['server']['protocol'] = request.META.get('SERVER_PROTOCOL') or None
		# Build clean URL without query parameters
		clean_url = request.build_absolute_uri().split('?')[0]
		final_result['data']['request']['url'] = clean_url
		
		# Extract and structure query parameters
		if request.GET:
			query_params = {}
			for key, value_list in request.GET.lists():
				# Handle multiple values for same key
				if len(value_list) == 1:
					query_params[key] = value_list[0]
				else:
					query_params[key] = value_list
			final_result['data']['request']['query'] = self.mask_sensitive_data(query_params)
		else:
			final_result['data']['request']['query'] = {}
		final_result['data']['request']['user_agent'] = request.META.get('HTTP_USER_AGENT', 'HTTP_USER_AGENT_NOT_FOUND')
		
		# Extract route path
		try:
			resolved = resolve(request.path_info)
			route_pattern = resolved.route
			if route_pattern:
				# Convert Django URL patterns to OpenAPI format
				route_path = re.sub(r'<[^:]+:([^>]+)>', r'{\1}', str(route_pattern))
				final_result['data']['request']['route_path'] = route_path
			else:
				final_result['data']['request']['route_path'] = None
		except Exception as e:
			final_result['data']['request']['route_path'] = None
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
			if len(request_body) > self.MAX_PAYLOAD_SIZE:
				final_result['data']['request']['body'] = self.PAYLOAD_TOO_LARGE_MESSAGE
				if self.treblle_debug:
					self.treblle_print(f"Request body too large ({len(request_body)} bytes > {self.MAX_PAYLOAD_SIZE} bytes), replacing with size limit message")
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

		try:
			if response.content:
				final_result['data']['response']['size'] = len(response.content)
				
				# Check payload size limit
				if len(response.content) > self.MAX_PAYLOAD_SIZE:
					final_result['data']['response']['body'] = self.PAYLOAD_TOO_LARGE_MESSAGE
					if self.treblle_debug:
						self.treblle_print(f"Response body too large ({len(response.content)} bytes > {self.MAX_PAYLOAD_SIZE} bytes), replacing with size limit message")
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
		except Exception:
			# Default to 0 if we can't calculate response size for any reason
			final_result['data']['response']['size'] = 0

	def send_to_treblle(self, final_result):
		"""
		Function to send the data to treblle with gzip compression for faster transfer
		"""
		json_body = self.safe_json_dumps(final_result)
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