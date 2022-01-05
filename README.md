# Treblle for Django

[![Latest Version](https://img.shields.io/npm/v/treblle)](https://img.shields.io/npm/v/treblle)
[![Total Downloads](https://img.shields.io/npm/dt/treblle)](https://img.shields.io/npm/dt/treblle)
[![MIT Licence](https://img.shields.io/npm/l/treblle)](LICENSE.md)

Treblle makes it super easy to understand what’s going on with your APIs and the apps that use them. Just by adding Treblle to your API out of the box you get:

- Real-time API monitoring and logging
- Auto-generated API docs with OAS support
- API analytics
- Quality scoring
- One-click testing
- API managment on the go
- and more...

## Requirements

- requests

## Dependencies

- [`django`](https://www.djangoproject.com/)

## Installation

You can install Treblle for django via [PYPi](https://pypi.org/). Simply run the following command:

```bash
$ pip install treblle
```

Don't forget to load the required python modules in your setting.py like so:


**Include "treblle" to your INSTALLED_APPS:**


```py
INSTALLED_APPS = [
    ...
    'treblle',
]
```

**Include "TreblleMiddleware" to your MIDDLEWARE_CLASSES:**

```py
MIDDLEWARE_CLASSES = (
    ...
    'treblle.middleware.TreblleMiddleware',
)
```

## Getting started

Next, create a FREE account on <https://treblle.com> to get an API key and Project ID. After you have those simply initialize Treblle in your **setting.py** file like so for django:

```py
TREBLLE_API_KEY = "_YOUR_API_KEY_"
TREBLLE_PROJECT_ID = "_YOUR_PROJECT_ID_"
```

That's it. Your API requests and responses are now being sent to your Treblle project. Just by adding that line of code you get features like: auto-documentation, real-time request/response monitoring, error tracking and so much more.


### Need to hide additional fields?


If you want to expand the list of fields you want to hide, you can pass property names you want to hide by using the `TREBLLE_HIDDEN_JSON_KEYS` setting like in the example below.

```py
TREBLLE_HIDDEN_JSON_KEYS = ["secretField", "highlySensitiveField"]
```

## Support

If you have problems of any kind feel free to reach out via <https://treblle.com> or email vedran@treblle.com and we'll do our best to help you out.

## License

Copyright 2021, Treblle Limited. Licensed under the MIT license:
http://www.opensource.org/licenses/mit-license.php