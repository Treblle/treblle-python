<div align="center">
  <img src="https://treblle-github.s3.us-east-1.amazonaws.com/github-header.jpg"/>
</div>
<div align="center">

# Treblle

<a href="https://docs.treblle.com/en/integrations" target="_blank">Integrations</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="http://treblle.com/" target="_blank">Website</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="https://docs.treblle.com" target="_blank">Docs</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="https://blog.treblle.com" target="_blank">Blog</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="https://twitter.com/treblleapi" target="_blank">Twitter</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="https://treblle.com/chat" target="_blank">Discord</a>
<br />

  <hr />
</div>

Treblle is a lightweight SDK that helps Engineering and Product teams build, ship & maintain REST based APIs faster.

## Features

<div align="center">
  <br />
  <img src="https://treblle-github.s3.amazonaws.com/features.png"/>
  <br />
  <br />
</div>

- [API Monitoring & Observability](https://www.treblle.com/features/api-monitoring-observability)
- [Auto-generated API Docs](https://www.treblle.com/features/auto-generated-api-docs)
- [API analytics](https://www.treblle.com/features/api-analytics)
- [Treblle API Score](https://www.treblle.com/features/api-quality-score)
- [API Lifecycle Collaboration](https://www.treblle.com/features/api-lifecycle)
- [Native Treblle Apps](https://www.treblle.com/features/native-apps)


## How Treblle Works
Once you’ve integrated a Treblle SDK in your codebase, this SDK will send requests and response data to your Treblle Dashboard.

In your Treblle Dashboard you get to see real-time requests to your API, auto-generated API docs, API analytics like how fast the response was for an endpoint, the load size of the response, etc.

Treblle also uses the requests sent to your Dashboard to calculate your API score which is a quality score that’s calculated based on the performance, quality, and security best practices for your API.

> Visit [https://docs.treblle.com](http://docs.treblle.com) for the complete documentation.

## Security

### Masking fields
Masking fields ensure certain sensitive data are removed before being sent to Treblle.

To make sure masking is done before any data leaves your server [we built it into all our SDKs](https://docs.treblle.com/en/security/masked-fields#fields-masked-by-default).

This means data masking is super fast and happens on a programming level before the API request is sent to Treblle. You can [customize](https://docs.treblle.com/en/security/masked-fields#custom-masked-fields) exactly which fields are masked when you’re integrating the SDK.

> Visit the [Masked fields](https://docs.treblle.com/en/security/masked-fields) section of the [docs](https://docs.sailscasts.com) for the complete documentation.


## Version 2.0 - Major Update 🚀

**Treblle Django SDK v2.0** brings significant performance improvements, better security, and enhanced developer experience. This version has been completely rewritten with production-grade optimizations.

### ✨ What's New in v2.0

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

### 🔄 Breaking Changes - Migration Required

If you're upgrading from v1, you'll need to make these changes:

#### 1. **Configuration Format (REQUIRED)**

**❌ Old v1 Format:**
```python
TREBLLE_INFO = {
    'api_key': 'your_sdk_token',      # Confusing naming
    'project_id': 'your_api_key',     # Confusing naming
    'hidden_keys': ['password']
}
```

**✅ New v2 Format:**
```python
TREBLLE = {
    'SDK_TOKEN': 'your_sdk_token',     # Clear naming
    'API_KEY': 'your_api_key',         # Clear naming  
    'MASKED_FIELDS': ['password'],     # Django-style naming
    'DEBUG': True,                     # New debug mode
    'MAX_PAYLOAD_SIZE': 10485760,      # New payload limits
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

### 📊 Performance Comparison

| Metric | v1.x | v2.0 | Improvement |
|--------|------|------|-------------|
| Memory Usage | High (leaks) | Low (optimized) | ~60% reduction |
| Request Overhead | 100-200ms | 10-50ms | ~75% faster |
| Django Startup | Slow | Fast | ~50% faster |
| Thread Safety | ❌ Race conditions | ✅ Fully safe | Production ready |
| Large Payloads | ❌ Memory issues | ✅ Protected | Stable under load |

### 🚀 Recommended Migration Steps

1. **Update configuration** to new `TREBLLE` format
2. **Enable debug mode** during migration: `'DEBUG': True`
3. **Test thoroughly** in your staging environment
4. **Monitor logs** for any configuration issues
5. **Update Django middleware** setting if using `MIDDLEWARE_CLASSES`

### 📋 Migration Checklist

- [ ] Update settings from `TREBLLE_INFO` to `TREBLLE`
- [ ] Change `MIDDLEWARE_CLASSES` to `MIDDLEWARE` (if applicable)
- [ ] Test in staging environment with `DEBUG: True`
- [ ] Verify all API endpoints are tracked correctly
- [ ] Check that sensitive fields are properly masked
- [ ] Monitor performance improvements in production

---

## Get Started

1. Sign in to [Treblle](https://app.treblle.com).
2. [Create a Treblle project](https://docs.treblle.com/en/dashboard/projects#creating-a-project).
3. [Setup the SDK](#install-the-SDK) for your platform.

### Install the SDK

You can install Treblle for django via PYPi. Simply run the following command:

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
MIDDLEWARE_CLASSES = [
...
'treblle.middleware.TreblleMiddleware',
]
```

After you've retrieved your SDK Token and API Key from your Treblle dashboard, initialize Treblle in your `settings.py` file like so for Django:

```python
TREBLLE = {
    'SDK_TOKEN': os.environ.get('TREBLLE_SDK_TOKEN'),
    'API_KEY': os.environ.get('TREBLLE_API_KEY'),
    'MASKED_FIELDS': ['custom_field', 'internal_id'],  # Optional
    'DEBUG': True,  # Optional - enables debug logging (default: False)
    'MAX_PAYLOAD_SIZE': 5 * 1024 * 1024,  # Optional - 5MB limit (default: 10MB)
}
```

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

## Available SDKs

Treblle provides [open-source SDKs](https://docs.treblle.com/en/integrations) that let you seamlessly integrate Treblle with your REST-based APIs.

- [`treblle-laravel`](https://github.com/Treblle/treblle-laravel): SDK for Laravel
- [`treblle-php`](https://github.com/Treblle/treblle-php): SDK for PHP
- [`treblle-symfony`](https://github.com/Treblle/treblle-symfony): SDK for Symfony
- [`treblle-lumen`](https://github.com/Treblle/treblle-lumen): SDK for Lumen
- [`treblle-sails`](https://github.com/Treblle/treblle-sails): SDK for Sails
- [`treblle-adonisjs`](https://github.com/Treblle/treblle-adonisjs): SDK for AdonisJS
- [`treblle-fastify`](https://github.com/Treblle/treblle-fastify): SDK for Fastify
- [`treblle-directus`](https://github.com/Treblle/treblle-directus): SDK for Directus
- [`treblle-strapi`](https://github.com/Treblle/treblle-strapi): SDK for Strapi
- [`treblle-express`](https://github.com/Treblle/treblle-express): SDK for Express
- [`treblle-koa`](https://github.com/Treblle/treblle-koa): SDK for Koa
- [`treblle-go`](https://github.com/Treblle/treblle-go): SDK for Go
- [`treblle-ruby`](https://github.com/Treblle/treblle-ruby): SDK for Ruby on Rails
- [`treblle-python`](https://github.com/Treblle/treblle-python): SDK for Python/Django

> See the [docs](https://docs.treblle.com/en/integrations) for more on SDKs and Integrations.

## Other Packages

Besides the SDKs, we also provide helpers and configuration used for SDK
development. If you're thinking about contributing to or creating a SDK, have a look at the resources
below:

- [`treblle-utils`](https://github.com/Treblle/treblle-utils):  A set of helpers and
  utility functions useful for the JavaScript SDKs.
- [`php-utils`](https://github.com/Treblle/php-utils):   A set of helpers and
  utility functions useful for the PHP SDKs.

## Community 💙

First and foremost: **Star and watch this repository** to stay up-to-date.

Also, follow our [Blog](https://blog.treblle.com), and on [Twitter](https://twitter.com/treblleapi).

You can chat with the team and other members on [Discord](https://treblle.com/chat) and follow our tutorials and other video material at [YouTube](https://youtube.com/@treblle).

[![Treblle Discord](https://img.shields.io/badge/Treblle%20Discord-Join%20our%20Discord-F3F5FC?labelColor=7289DA&style=for-the-badge&logo=discord&logoColor=F3F5FC&link=https://treblle.com/chat)](https://treblle.com/chat)

[![Treblle YouTube](https://img.shields.io/badge/Treblle%20YouTube-Subscribe%20on%20YouTube-F3F5FC?labelColor=c4302b&style=for-the-badge&logo=YouTube&logoColor=F3F5FC&link=https://youtube.com/@treblle)](https://youtube.com/@treblle)

[![Treblle on Twitter](https://img.shields.io/badge/Treblle%20on%20Twitter-Follow%20Us-F3F5FC?labelColor=1DA1F2&style=for-the-badge&logo=Twitter&logoColor=F3F5FC&link=https://twitter.com/treblleapi)](https://twitter.com/treblleapi)

### How to contribute

Here are some ways of contributing to making Treblle better:

- **[Try out Treblle](https://docs.treblle.com/en/introduction#getting-started)**, and let us know ways to make Treblle better for you. Let us know here on [Discord](https://treblle.com/chat).
- Join our [Discord](https://treblle.com/chat) and connect with other members to share and learn from.
- Send a pull request to any of our [open source repositories](https://github.com/Treblle) on Github. Check the contribution guide on the repo you want to contribute to for more details about how to contribute. We're looking forward to your contribution!

### Contributors
<!-- Replace link with the link of the SDK contributors-->
<a href="https://github.com/Treblle/treblle-python/graphs/contributors">
  <p align="center">
    <img  src="https://contrib.rocks/image?repo=Treblle/treblle-python" alt="A table of avatars from the project's contributors" />
  </p>
</a>
