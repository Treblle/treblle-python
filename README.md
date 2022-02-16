# Treblle for Django

[![Downloads](https://pepy.tech/badge/treblle)](https://pepy.tech/project/treblle)
[![Downloads](https://pepy.tech/badge/treblle/month)](https://pepy.tech/project/treblle)
[![Downloads](https://pepy.tech/badge/treblle/week)](https://pepy.tech/project/treblle)

Treblle makes it super easy to understand what’s going on with your APIs and the apps that use them. Just by adding Treblle to your API out of the box you get:

- Real-time API monitoring and logging
- Auto-generated API docs with OAS support
- API analytics
- Quality scoring
- One-click testing
- API management on the go
- and more...

## Requirements

- requests

## Installation

You can install Treblle for django via [PYPi](https://pypi.org/). Simply run the following command:

```shell
$ pip install treblle
```

Don't forget to load the required python modules in your settings.py like so:

```
INSTALLED_APPS = [ 
...
'treblle',
]
```

```
MIDDLEWARE_CLASSES = [
...
'treblle.middleware.TreblleMiddleware',
]
```

# Getting started

Next, create a FREE account on [Treblle](https://treblle.com) to get an API key and Project ID. After you have those simply initialize Treblle in your **settinsg.py** file like so for django:

```
TREBLLE_INFO = {
'api_key': os.environ.get('TREBLLE_API_KEY'),
'project_id': os.environ.get('TREBLLE_PROJECT_ID')
}
```
That's it. Your API requests and responses are now being sent to your Treblle project. Just by adding these lines of code you get features like: auto-documentation, real-time request/response monitoring, error tracking and so much more.


# Need to hide additional fields?


If you want to expand the list of fields you want to hide, you can pass property names you want to hide by using the `TREBLLE_HIDDEN_KEYS` setting like in the example below.

```
TREBLLE_HIDDEN_KEYS = ["id", "email"]
```

```
TREBLLE_INFO = {
'api_key': os.environ.get('TREBLLE_API_KEY'),
'project_id': os.environ.get('TREBLLE_PROJECT_ID'),
'hidden_keys' : TREBLLE_HIDDEN_KEYS
}
```


# releases
0.9 - stable

0.10, 0.11 - send application errors to treblle

0.13 - solve bug of hidden field being too long

0.14 - fixes

# Support

If you have problems of any kind feel free to reach out via <https://treblle.com> or email vedran@treblle.com and we'll do our best to help you out.

# License

Copyright 2022, Treblle Limited. Licensed under the MIT license:
http://www.opensource.org/licenses/mit-license.php
