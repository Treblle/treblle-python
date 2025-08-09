# Treblle - API Intelligence Platform

[![Treblle API Intelligence](https://github.com/user-attachments/assets/b268ae9e-7c8a-4ade-95da-b4ac6fce6eea)](https://treblle.com)

[Website](http://treblle.com/) • [Documentation](https://docs.treblle.com/) • [Pricing](https://treblle.com/pricing)


Treblle is an API intelligence platfom that helps developers, teams and organizations understand their APIs from a single integration point.

***

## Treblle Django SDK

### Requirements

- **Python**: 3.7 or higher
- **Django**: 2.2 or higher  
- **requests**: 2.25.0 or higher

> **Note**: Django 5.0+ requires Python 3.10 or higher. If you're using Django 5.x, ensure you have Python 3.10+.

### Getting Started

You can install Treblle for django via PyPI. 

**For the latest stable version:**
```sh
$ pip install treblle
```

Don’t forget to load the required python modules in your settings.py like so:

```python
INSTALLED_APPS = [
...
'treblle',
]
```

```python
MIDDLEWARE = [
    ...
    'treblle.middleware.TreblleMiddleware',
]
```

Create a FREE account on [treblle.com](https://treblle.com/), copy your SDK Token and API Key from the Treblle dashboard to the `settings.py` like so:

```python
TREBLLE = {
    'SDK_TOKEN': os.environ.get('TREBLLE_SDK_TOKEN'),
    'API_KEY': os.environ.get('TREBLLE_API_KEY'),
    'MASKED_FIELDS': ['custom_field', 'internal_id'],  # Optional
    'DEBUG': True,  # Optional - enables debug logging (default: False)
    'MAX_PAYLOAD_SIZE': 5 * 1024 * 1024,  # Optional - 5MB limit (default: 10MB)
}
```

Visit the [Treblle Dashboard](https://platform.treblle.com/) and see requests appear in real-time.

## Version 2.0 🚀

**Treblle Django SDK v2.0** brings significant performance improvements, better security, and enhanced developer experience. This version has been completely rewritten with production-grade optimizations.

### ✨ What's New

**🚀 Performance Improvements:**
- **Thread-safe architecture** - No more race conditions or memory leaks
- **Server info caching** - 50-100ms faster per request by caching system calls
- **Lazy configuration loading** - Faster Django startup time
- **Payload size limits** - Protection against large payloads (configurable, default 10MB)
- **Memory optimizations** - Efficient data masking and processing

**🔒 Enhanced Security:**
- **Environment variable support** - `TREBLLE_MASKED_FIELDS` ENV variable
- **Improved data masking** - More efficient and comprehensive field masking
- **Robust error handling** - Better exception capture and processing

**🛠️ Developer Experience:**
- **Comprehensive debug mode** - Detailed logging for troubleshooting
- **Better configuration** - Cleaner Django-native settings format
- **OpenAPI route patterns** - Proper route path detection and formatting
- **Load balancing** - Random endpoint selection across Treblle infrastructure

### 🔄 Migrating from v1 to v2

If you're upgrading from v1, you'll need to make these changes:

#### 1. **Configuration Format (REQUIRED)**

**❌ Old v1 Format:**
```python
TREBLLE_INFO = {
    'api_key': 'your_sdk_token',
    'project_id': 'your_api_key',
    'hidden_keys': ['password']
}
```

**✅ New v2 Format:**
```python
TREBLLE = {
    'SDK_TOKEN': 'your_sdk_token',
    'API_KEY': 'your_api_key',
    'MASKED_FIELDS': ['password'], # Optional
    'DEBUG': False, # Optional
    'MAX_PAYLOAD_SIZE': 10485760, # Optional
}
```

#### 2. **Django Settings Update (REQUIRED)**

**❌ Old v1 Middleware:**
```python
MIDDLEWARE_CLASSES = [  # Deprecated Django setting
    'treblle.middleware.TreblleMiddleware',
]
```

**✅ New v2 Middleware:**
```python
MIDDLEWARE = [  # Modern Django setting
    'treblle.middleware.TreblleMiddleware',
]
```

#### 3. **Environment Variables (OPTIONAL)**

**🆕 New in v2:** Support for environment-based configuration:
```bash
export TREBLLE_MASKED_FIELDS="api_key,password,credit_card"
```

### 🔄 Backward Compatibility

**Good news!** v2 maintains backward compatibility:
- ✅ Old `TREBLLE_INFO` format still works
- ✅ Existing `MIDDLEWARE_CLASSES` still supported  
- ✅ All v1 functionality preserved
- ✅ No immediate migration required (but recommended)


---

### Debug Mode

Enable debug mode to get detailed logging about the SDK's operation:

- **Configuration errors**: Missing or invalid SDK_TOKEN/API_KEY
- **Middleware loading**: Confirmation that Treblle is active
- **API responses**: HTTP status codes from Treblle endpoints
- **Error handling**: 4xx/5xx errors with helpful troubleshooting tips
- **Data processing**: JSON validation and masking information

```python
TREBLLE = {
    'SDK_TOKEN': 'your_sdk_token',
    'API_KEY': 'your_api_key', 
    'DEBUG': True  # Enable debug mode
}
```

### Payload Size Limits

To prevent memory issues and maintain API performance, Treblle limits payload sizes:

- **Default limit**: 10MB for both request and response bodies
- **Configurable**: Set custom limits via `MAX_PAYLOAD_SIZE` setting
- **Behavior**: Large payloads are replaced with a descriptive message, but the request is still tracked

```python
TREBLLE = {
    'SDK_TOKEN': 'your_token',
    'API_KEY': 'your_key',
    'MAX_PAYLOAD_SIZE': 5 * 1024 * 1024,  # 5MB limit
}
```

**Note**: Headers, metadata, and other request/response data are always captured regardless of payload size.

**Backward compatibility:** The old `TREBLLE_INFO` format is still supported:
```python
TREBLLE_INFO = {
    'api_key': os.environ.get('TREBLLE_SDK_TOKEN'),  # SDK Token
    'project_id': os.environ.get('TREBLLE_API_KEY'),  # API Key  
}
```
> See the [docs](https://docs.treblle.com/en/integrations/django) for this SDK to learn more.

### Getting Help

If you continue to experience issues:

1. Enable `debug: true` and check console output
2. Verify your SDK token and API key are correct in Treblle dashboard
3. Test with a simple endpoint first
4. Check [Treblle documentation](https://docs.treblle.com) for the latest updates
5. Contact support at <https://treblle.com> or email support@treblle.com

## Support

If you have problems of any kind feel free to reach out via <https://treblle.com> or email support@treblle.com and we'll do our best to help you out.

## License

Copyright 2025, Treblle Inc. Licensed under the MIT license:
http://www.opensource.org/licenses/mit-license.php