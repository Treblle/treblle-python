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

Don’t forget to load the required python modules in your `settings.py` like so:

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

Create a FREE account on [treblle.com](https://treblle.com/), copy your SDK Token and API Key from the Treblle Dashboard to `settings.py` like so:

```python
TREBLLE = {
    'SDK_TOKEN': os.environ.get('TREBLLE_SDK_TOKEN'),
    'API_KEY': os.environ.get('TREBLLE_API_KEY'),
    'MASKED_FIELDS': ['custom_field', 'internal_id'],  # Optional - additonal fields to mask
    'DEBUG': True,  # Optional - enables debug logging (default: False)
    'EXCLUDED_ROUTES': ['/health/', '/ping', '/admin/*'],  # Optional - routes to exclude from tracking
}
```

Visit the [Treblle Dashboard](https://platform.treblle.com/) and see requests appear in real-time.

## Version 2.0 🚀

**Treblle Django SDK v2.0** brings significant performance improvements, better security, and enhanced developer experience. This version has been completely rewritten with production-grade optimizations.

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
    'EXCLUDED_ROUTES': ['/health/', '/ping'], # Optional
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

### Route Exclusion

You can exclude specific routes from being tracked by Treblle. This is useful for health checks, monitoring endpoints, or other routes that generate high-frequency, low-value traffic:

```python
TREBLLE = {
    'SDK_TOKEN': 'your_token',
    'API_KEY': 'your_key',
    'EXCLUDED_ROUTES': [
        '/health/',           # Exact path match
        '/api/health',        # Exact path match  
        '/ping',              # Exact path match
        '/admin/*',           # Wildcard: excludes /admin/login, /admin/users, etc.
        '*/metrics',          # Wildcard: excludes /api/metrics, /internal/metrics, etc.
        '/status/*',          # Wildcard: excludes anything under /status/
    ],
}
```

**Pattern matching:**
- **Exact matches**: `/health/` only matches exactly `/health/`
- **Wildcards**: Use `*` for flexible matching (e.g., `/admin/*` matches `/admin/login`, `/admin/users/1`)
- **Debug logging**: Enable `DEBUG: True` to see which routes are being excluded

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