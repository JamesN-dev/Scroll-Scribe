# Testing Tools

Django provides a small set of tools that come in handy when writing tests.

## The Test Client

The test client is a Python class that acts as a dummy web browser, allowing you to test your views and interact with your Django-powered application programmatically.

Some of the things you can do with the test client are:

- Simulate GET and POST requests on a URL and observe the response – everything from low-level HTTP (result headers and status codes) to page content.
- See the chain of redirects (if any) and check the URL and status code at each step.
- Test that a given request is rendered by a given Django template, with a template context that contains certain values.

Note that the test client is not intended to be a replacement for [Selenium](https://www.selenium.dev/) or other “in-browser” frameworks. Django’s test client has a different focus. In short:

- Use Django’s test client to establish that the correct template is being rendered and that the template is passed the correct context data.
- Use [RequestFactory](../advanced/#django.test.RequestFactory) to test view functions directly, bypassing the routing and middleware layers.
- Use in-browser frameworks like [Selenium](https://www.selenium.dev/) to test *rendered* HTML and the *behavior* of web pages, namely JavaScript functionality. Django also provides special support for those frameworks; see the section on [LiveServerTestCase](#django.test.LiveServerTestCase) for more details.

A comprehensive test suite should use a combination of all of these test types.

### Overview and a Quick Example

To use the test client, instantiate `django.test.Client` and retrieve web pages:

```python
>>> from django.test import Client
>>> c = Client()
>>> response = c.post("/login/", {"username": "john", "password": "smith"})
>>> response.status_code
200
>>> response = c.get("/customer/details/")
>>> response.content
b'<!DOCTYPE html...'
```

As this example suggests, you can instantiate `Client` from within a session of the Python interactive interpreter.

Note a few important things about how the test client works:

- The test client does *not* require the web server to be running. In fact, it will run just fine with no web server running at all! That’s because it avoids the overhead of HTTP and deals directly with the Django framework. This helps make the unit tests run quickly.
- When retrieving pages, remember to specify the *path* of the URL, not the whole domain. For example, this is correct:

```python
>>> c.get("/login/")
```

This is incorrect:

```python
>>> c.get("https://www.example.com/login/")
```

The test client is not capable of retrieving web pages that are not powered by your Django project. If you need to retrieve other web pages, use a Python standard library module such as [urllib](https://docs.python.org/3/library/urllib.html#module-urllib).

- To resolve URLs, the test client uses whatever URLconf is pointed-to by your [ROOT_URLCONF](../../../ref/settings/#std-setting-ROOT_URLCONF) setting.
- Although the above example would work in the Python interactive interpreter, some of the test client’s functionality, notably the template-related functionality, is only available *while tests are running*.

The reason for this is that Django’s test runner performs a bit of black magic in order to determine which template was loaded by a given view. This black magic (essentially a patching of Django’s template system in memory) only happens during test running.

- By default, the test client will disable any CSRF checks performed by your site.

If, for some reason, you *want* the test client to perform CSRF checks, you can create an instance of the test client that enforces CSRF checks. To do this, pass in the `enforce_csrf_checks` argument when you construct your client:

```python
>>> from django.test import Client
>>> csrf_client = Client(enforce_csrf_checks=True)
```

### Making Requests

Use the `django.test.Client` class to make requests.

#### class Client(enforce_csrf_checks=False, raise_request_exception=True, json_encoder=DjangoJSONEncoder, *, headers=None, query_params=None, **defaults)

A testing HTTP client. Takes several arguments that can customize behavior.

- `headers` allows you to specify default headers that will be sent with every request. For example, to set a `User-Agent` header:

```python
client = Client(headers={"user-agent": "curl/7.79.1"})
```

- `query_params` allows you to specify the default query string that will be set on every request.

Arbitrary keyword arguments in `**defaults` set WSGI [environ variables](https://peps.python.org/pep-3333/#environ-variables). For example, to set the script name:

```python
client = Client(SCRIPT_NAME="/app/")
```

> **Note**
>
> Keyword arguments starting with a `HTTP_` prefix are set as headers, but the `headers` parameter should be preferred for readability.

The values from the `headers`, `query_params`, and `extra` keyword arguments passed to `get()`, `post()`, etc. have precedence over the defaults passed to the class constructor.

- The `enforce_csrf_checks` argument can be used to test CSRF protection (see above).
- The `raise_request_exception` argument allows controlling whether or not exceptions raised during the request should also be raised in the test. Defaults to `True`.
- The `json_encoder` argument allows setting a custom JSON encoder for the JSON serialization that’s described in `post()`.

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

Once you have a `Client` instance, you can call any of the following methods:

#### get(path, data=None, follow=False, secure=False, *, headers=None, query_params=None, **extra)

Makes a GET request on the provided `path` and returns a `Response` object, which is documented below.

- The key-value pairs in the `query_params` dictionary are used to set query strings. For example:

```python
>>> c = Client()
>>> c.get("/customers/details/", query_params={"name": "fred", "age": 7})
```

…will result in the evaluation of a GET request equivalent to:

```
/customers/details/?name=fred&age=7
```

It is also possible to pass these parameters into the `data` argument. However, `query_params` is preferred as it works for any HTTP method.

- The `headers` parameter can be used to specify headers to be sent in the request. For example:

```python
>>> c = Client()
>>> c.get(
... "/customers/details/",
... query_params={"name": "fred", "age": 7},
... headers={"accept": "application/json"},
...)
```

…will send the HTTP header `HTTP_ACCEPT` to the details view, which is a good way to test code paths that use the [django.http.HttpRequest.accepts()](../../../ref/request-response/#django.http.HttpRequest.accepts) method.

- Arbitrary keyword arguments set WSGI [environ variables](https://peps.python.org/pep-3333/#environ-variables). For example, headers to set the script name:

```python
>>> c = Client()
>>> c.get("/", SCRIPT_NAME="/app/")
```

If you already have the GET arguments in URL-encoded form, you can use that encoding instead of using the data argument. For example, the previous GET request could also be posed as:

```python
>>> c = Client()
>>> c.get("/customers/details/?name=fred&age=7")
```

If you provide a URL with both an encoded GET data and either a query_params or data argument these arguments will take precedence.

- If you set `follow` to `True` the client will follow any redirects and a `redirect_chain` attribute will be set in the response object containing tuples of the intermediate urls and status codes.

If you had a URL `/redirect_me/` that redirected to `/next/`, that redirected to `/final/`, this is what you’d see:

```python
>>> response = c.get("/redirect_me/", follow=True)
>>> response.redirect_chain
[('http://testserver/next/', 302), ('http://testserver/final/', 302)]
```

- If you set `secure` to `True` the client will emulate an HTTPS request.

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

#### post(path, data=None, content_type=MULTIPART_CONTENT, follow=False, secure=False, *, headers=None, query_params=None, **extra)

Makes a POST request on the provided `path` and returns a `Response` object, which is documented below.

- The key-value pairs in the `data` dictionary are used to submit POST data. For example:

```python
>>> c = Client()
>>> c.post("/login/", {"name": "fred", "passwd": "secret"})
```

…will result in the evaluation of a POST request to this URL:

```
/login/
```

…with this POST data:

```
name=fred&passwd=secret
```

If you provide `content_type` as *application/json*, the `data` is serialized using [json.dumps()](https://docs.python.org/3/library/json.html#json.dumps) if it’s a dict, list, or tuple. Serialization is performed with [DjangoJSONEncoder](../../serialization/#django.core.serializers.json.DjangoJSONEncoder) by default, and can be overridden by providing a `json_encoder` argument to `Client`. This serialization also happens for `put()`, `patch()`, and `delete()` requests.

If you provide any other `content_type` (e.g. *text/xml* for an XML payload), the contents of `data` are sent as-is in the POST request, using `content_type` in the HTTP `Content-Type` header.

If you don’t provide a value for `content_type`, the values in `data` will be transmitted with a content type of *multipart/form-data*. In this case, the key-value pairs in `data` will be encoded as a multipart message and used to create the POST data payload.

To submit multiple values for a given key – for example, to specify the selections for a `<select multiple>` – provide the values as a list or tuple for the required key. For example, this value of `data` would submit three selected values for the field named `choices`:

```python
{"choices": ["a", "b", "d"]}
```

Submitting files is a special case. To POST a file, you need only provide the file field name as a key, and a file handle to the file you wish to upload as a value. For example, if your form has fields `name` and `attachment`, the latter a [FileField](../../../ref/forms/fields/#django.forms.FileField):

```python
>>> c = Client()
>>> with open("wishlist.doc", "rb") as fp:
... c.post("/customers/wishes/", {"name": "fred", "attachment": fp})
...
```

You may also provide any file-like object (e.g., [StringIO](https://docs.python.org/3/library/io.html#io.StringIO) or [BytesIO](https://docs.python.org/3/library/io.html#io.BytesIO)) as a file handle. If you’re uploading to an [ImageField](../../../ref/models/fields/#django.db.models.ImageField), the object needs a `name` attribute that passes the [validate_image_file_extension](../../../ref/validators/#django.core.validators.validate_image_file_extension) validator. For example:

```python
>>> from io import BytesIO
>>> img = BytesIO(
... b"GIF89a\x01\x00\x01\x00\x00\x00\x00!"
... b"\xf9\x04\x01\x00\x00\x00"
... b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00"
... )
>>> img.name = "myimage.gif"
```

Note that if you wish to use the same file handle for multiple `post()` calls then you will need to manually reset the file pointer between posts. The easiest way to do this is to manually close the file after it has been provided to `post()`, as demonstrated above.

You should also ensure that the file is opened in a way that allows the data to be read. If your file contains binary data such as an image, this means you will need to open the file in `rb` (read binary) mode.

The `headers`, `query_params`, and `extra` parameters acts the same as for [Client.get()](#django.test.Client.get).

If the URL you request with a POST contains encoded parameters, these parameters will be made available in the request.GET data. For example, if you were to make the request:

```python
>>> c.post(
... "/login/",
... {"name": "fred", "passwd": "secret"},
... query_params={"visitor": "true"}
...)
```

… the view handling this request could interrogate request.POST to retrieve the username and password, and could interrogate request.GET to determine if the user was a visitor.

- If you set `follow` to `True` the client will follow any redirects and a `redirect_chain` attribute will be set in the response object containing tuples of the intermediate urls and status codes.
- If you set `secure` to `True` the client will emulate an HTTPS request.

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

#### head(path, data=None, follow=False, secure=False, *, headers=None, query_params=None, **extra)

Makes a HEAD request on the provided `path` and returns a `Response` object. This method works just like [Client.get()](#django.test.Client.get), including the `follow`, `secure`, `headers`, `query_params`, and `extra` parameters, except it does not return a message body.

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

#### options(path, data='', content_type='application/octet-stream', follow=False, secure=False, *, headers=None, query_params=None, **extra)

Makes an OPTIONS request on the provided `path` and returns a `Response` object. Useful for testing RESTful interfaces.

When `data` is provided, it is used as the request body, and a `Content-Type` header is set to `content_type`.

The `follow`, `secure`, `headers`, `query_params`, and `extra` parameters act the same as for [Client.get()](#django.test.Client.get).

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

#### put(path, data='', content_type='application/octet-stream', follow=False, secure=False, *, headers=None, query_params=None, **extra)

Makes a PUT request on the provided `path` and returns a `Response` object. Useful for testing RESTful interfaces.

When `data` is provided, it is used as the request body, and a `Content-Type` header is set to `content_type`.

The `follow`, `secure`, `headers`, `query_params`, and `extra` parameters act the same as for [Client.get()](#django.test.Client.get).

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

#### patch(path, data='', content_type='application/octet-stream', follow=False, secure=False, *, headers=None, query_params=None, **extra)

Makes a PATCH request on the provided `path` and returns a `Response` object. Useful for testing RESTful interfaces.

The `follow`, `secure`, `headers`, `query_params`, and `extra` parameters act the same as for [Client.get()](#django.test.Client.get).

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

#### delete(path, data='', content_type='application/octet-stream', follow=False, secure=False, *, headers=None, query_params=None, **extra)

Makes a DELETE request on the provided `path` and returns a `Response` object. Useful for testing RESTful interfaces.

When `data` is provided, it is used as the request body, and a `Content-Type` header is set to `content_type`.

The `follow`, `secure`, `headers`, `query_params`, and `extra` parameters act the same as for [Client.get()](#django.test.Client.get).

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

#### trace(path, follow=False, secure=False, *, headers=None, query_params=None, **extra)

Makes a TRACE request on the provided `path` and returns a `Response` object. Useful for simulating diagnostic probes.

Unlike the other request methods, `data` is not provided as a keyword parameter in order to comply with [RFC 9110 Section 9.3.8](https://datatracker.ietf.org/doc/html/rfc9110.html#section-9.3.8), which mandates that TRACE requests must not have a body.

The `follow`, `secure`, `headers`, `query_params`, and `extra` parameters act the same as for [Client.get()](#django.test.Client.get).

> **Changed in Django 5.1:**
>
> The `query_params` argument was added.

#### login(**credentials)

If your site uses Django’s [authentication system](../../auth/), and you deal with logging in users, you can use the test client’s `login()` method to simulate the effect of a user logging into the site.

After you call this method, the test client will have all the cookies and session data required to pass any login-based tests that may form part of a view.

The format of the `credentials` argument depends on which [authentication backend](../../auth/customizing/#authentication-backends) you’re using (which is configured by your [AUTHENTICATION_BACKENDS](../../../ref/settings/#std-setting-AUTHENTICATION_BACKENDS) setting). If you’re using the standard authentication backend provided by Django (`ModelBackend`), `credentials` should be the user’s username and password, provided as keyword arguments:

```python
>>> c = Client()
>>> c.login(username="fred", password="secret")
# Now you can access a view that's only available to logged-in users.
```

If you’re using a different authentication backend, this method may require different credentials. It requires whichever credentials are required by your backend’s `authenticate()` method.

`login()` returns `True` if it the credentials were accepted and login was successful.

Finally, you’ll need to remember to create user accounts before you can use this method. As we explained above, the test runner is executed using a test database, which contains no users by default. As a result, user accounts that are valid on your production site will not work under test conditions. You’ll need to create users as part of the test suite – either manually (using the Django model API) or with a test fixture. Remember that if you want your test user to have a password, you can’t set the user’s password by setting the password attribute directly – you must use the [set_password()](../../../ref/contrib/auth/#django.contrib.auth.models.User.set_password) function to store a correctly hashed password. Alternatively, you can use the [create_user()](../../../ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user) helper method to create a new user with a correctly hashed password.

#### force_login(user, backend=None)

If your site uses Django’s [authentication system](../../auth/), you can use the `force_login()` method to simulate the effect of a user logging into the site. Use this method instead of [login()](#django.test.Client.login) when a test requires a user be logged in and the details of how a user logged in aren’t important.

Unlike `login()`, this method skips the authentication and verification steps: inactive users ([is_active=False](../../../ref/contrib/auth/#django.contrib.auth.models.User.is_active)) are permitted to login and the user’s credentials don’t need to be provided.

The user will have its `backend` attribute set to the value of the `backend` argument (which should be a dotted Python path string), or to `settings.AUTHENTICATION_BACKENDS[0]` if a value isn’t provided. The [authenticate()](../../auth/default/#django.contrib.auth.authenticate) function called by [login()](#django.test.Client.login) normally annotates the user like this.

This method is faster than `login()` since the expensive password hashing algorithms are bypassed. Also, you can speed up `login()` by [using a weaker hasher while testing](../overview/#speeding-up-tests-auth-hashers).

#### logout()

If your site uses Django’s [authentication system](../../auth/), the `logout()` method can be used to simulate the effect of a user logging out of your site.

After you call this method, the test client will have all the cookies and session data cleared to defaults. Subsequent requests will appear to come from an [AnonymousUser](../../../ref/contrib/auth/#django.contrib.auth.models.AnonymousUser).

### Testing Responses

The `get()` and `post()` methods both return a `Response` object. This `Response` object is *not* the same as the `HttpResponse` object returned by Django views; the test response object has some additional data useful for test code to verify.

Specifically, a `Response` object has the following attributes:

#### class Response

- `client`: The test client that was used to make the request that resulted in the response.
- `content`: The body of the response, as a bytestring. This is the final page content as rendered by the view, or any error message.
- `context`: The template `Context` instance that was used to render the template that produced the response content.

If the rendered page used multiple templates, then `context` will be a list of `Context` objects, in the order in which they were rendered.

Regardless of the number of templates used during rendering, you can retrieve context values using the `[]` operator. For example, the context variable `name` could be retrieved using:

```python
>>> response = client.get("/foo/")
>>> response.context["name"]
'Arthur'
```

> **Not using Django templates?**
>
> This attribute is only populated when using the [DjangoTemplates](../../templates/#django.template.backends.django.DjangoTemplates) backend. If you’re using another template engine, [context_data](../../../ref/template-response/#django.template.response.SimpleTemplateResponse.context_data) may be a suitable alternative on responses with that attribute.

- `exc_info`: A tuple of three values that provides information about the unhandled exception, if any, that occurred during the view.

The values are (type, value, traceback), the same as returned by Python’s [sys.exc_info()](https://docs.python.org/3/library/sys.html#sys.exc_info). Their meanings are:

- *type*: The type of the exception.
- *value*: The exception instance.
- *traceback*: A traceback object which encapsulates the call stack at the point where the exception originally occurred.

If no exception occurred, then `exc_info` will be `None`.

- `json(**kwargs)`: The body of the response, parsed as JSON. Extra keyword arguments are passed to [json.loads()](https://docs.python.org/3/library/json.html#json.loads). For example:

```python
>>> response = client.get("/foo/")
>>> response.json()["name"]
'Arthur'
```

If the `Content-Type` header is not `"application/json"`, then a [ValueError](https://docs.python.org/3/library/exceptions.html#ValueError) will be raised when trying to parse the response.

- `request`: The request data that stimulated the response.
- `wsgi_request`: The `WSGIRequest` instance generated by the test handler that generated the response.
- `status_code`: The HTTP status of the response, as an integer. For a full list of defined codes, see the [IANA status code registry](https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml).
- `templates`: A list of `Template` instances used to render the final content, in the order they were rendered. For each template in the list, use `template.name` to get the template’s file name, if the template was loaded from a file. (The name is a string such as `'admin/index.html'`).

> **Not using Django templates?**
>
> This attribute is only populated when using the [DjangoTemplates](../../templates/#django.template.backends.django.DjangoTemplates) backend. If you’re using another template engine, [template_name](../../../ref/template-response/#django.template.response.SimpleTemplateResponse.template_name) may be a suitable alternative if you only need the name of the template used for rendering.

- `resolver_match`: An instance of [ResolverMatch](../../../ref/urlresolvers/#django.urls.ResolverMatch) for the response. You can use the [func](../../../ref/urlresolvers/#django.urls.ResolverMatch.func) attribute, for example, to verify the view that served the response:

```python
# my_view here is a function based view.
self.assertEqual(response.resolver_match.func, my_view)
# Class-based views need to compare the view_class, as the
# functions generated by as_view() won't be equal.
self.assertIs(response.resolver_match.func.view_class, MyView)
```

If the given URL is not found, accessing this attribute will raise a [Resolver404](../../../ref/exceptions/#django.urls.Resolver404) exception.

As with a normal response, you can also access the headers through [HttpResponse.headers](../../../ref/request-response/#django.http.HttpResponse.headers). For example, you could determine the content type of a response using `response.headers['Content-Type']`.

### Exceptions

If you point the test client at a view that raises an exception and `Client.raise_request_exception` is `True`, that exception will be visible in the test case. You can then use a standard `try ... except` block or [assertRaises()](https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertRaises) to test for exceptions.

The only exceptions that are not visible to the test client are [Http404](../../http/views/#django.http.Http404), [PermissionDenied](../../../ref/exceptions/#django.core.exceptions.PermissionDenied), [SystemExit](https://docs.python.org/3/library/exceptions.html#SystemExit), and [SuspiciousOperation](../../../ref/exceptions/#django.core.exceptions.SuspiciousOperation). Django catches these exceptions internally and converts them into the appropriate HTTP response codes. In these cases, you can check `response.status_code` in your test.

If `Client.raise_request_exception` is `False`, the test client will return a 500 response as would be returned to a browser. The response has the attribute [exc_info](#django.test.Response.exc_info) to provide information about the unhandled exception.

### Persistent State

The test client is stateful. If a response returns a cookie, then that cookie will be stored in the test client and sent with all subsequent `get()` and `post()` requests.

Expiration policies for these cookies are not followed. If you want a cookie to expire, either delete it manually or create a new `Client` instance (which will effectively delete all cookies).

A test client has attributes that store persistent state information. You can access these properties as part of a test condition.

- `Client.cookies`: A Python [SimpleCookie](https://docs.python.org/3/library/http.cookies.html#http.cookies.SimpleCookie) object, containing the current values of all the client cookies. See the documentation of the [http.cookies](https://docs.python.org/3/library/http.cookies.html#module-http.cookies) module for more.
- `Client.session`: A dictionary-like object containing session information. See the [session documentation](../../http/sessions/) for full details.

To modify the session and then save it, it must be stored in a variable first (because a new `SessionStore` is created every time this property is accessed):

```python
def test_something(self):
    session = self.client.session
    session["somekey"] = "test"
    session.save()
```

- `Client.asession()`: This is similar to the [session](#django.test.Client.session) attribute but it works in async contexts.

### Setting the Language

When testing applications that support internationalization and localization, you might want to set the language for a test client request. The method for doing so depends on whether or not the [LocaleMiddleware](../../../ref/middleware/#django.middleware.locale.LocaleMiddleware) is enabled.

If the middleware is enabled, the language can be set by creating a cookie with a name of [LANGUAGE_COOKIE_NAME](../../../ref/settings/#std-setting-LANGUAGE_COOKIE_NAME) and a value of the language code:

```python
from django.conf import settings
def test_language_using_cookie(self):
    self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: "fr"})
    response = self.client.get("/")
    self.assertEqual(response.content, b"Bienvenue sur mon site.")
```

or by including the `Accept-Language` HTTP header in the request:

```python
def test_language_using_header(self):
    response = self.client.get("/", headers={"accept-language": "fr"})
    self.assertEqual(response.content, b"Bienvenue sur mon site.")
```

> **Note**
>
> When using these methods, ensure to reset the active language at the end of each test:

```python
def tearDown(self):
    translation.activate(settings.LANGUAGE_CODE)
```

More details are in [How Django discovers language preference](../../i18n/translation/#how-django-discovers-language-preference).

If the middleware isn’t enabled, the active language may be set using [translation.override()](../../../ref/utils/#django.utils.translation.override):

```python
from django.utils import translation
def test_language_using_override(self):
    with translation.override("fr"):
        response = self.client.get("/")
        self.assertEqual(response.content, b"Bienvenue sur mon site.")
```

More details are in [Explicitly setting the active language](../../i18n/translation/#explicitly-setting-the-active-language).

### Example

The following is a unit test using the test client:

```python
import unittest
from django.test import Client
class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
    def test_details(self):
        # Issue a GET request.
        response = self.client.get("/customer/details/")
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contains 5 customers.
        self.assertEqual(len(response.context["customers"]), 5)
```

> **See also**
>
> [django.test.RequestFactory](../advanced/#django.test.RequestFactory)

## Provided Test Case Classes

Normal Python unit test classes extend a base class of [unittest.TestCase](https://docs.python.org/3/library/unittest.html#unittest.TestCase). Django provides a few extensions of this base class:

![Hierarchy of Django unit testing classes (TestCase subclasses)](../../../_images/django_unittest_classes_hierarchy.svg)

You can convert a normal [unittest.TestCase](https://docs.python.org/3/library/unittest.html#unittest.TestCase) to any of the subclasses: change the base class of your test from `unittest.TestCase` to the subclass. All of the standard Python unit test functionality will be available, and it will be augmented with some useful additions as described in each section below.

### SimpleTestCase

#### class SimpleTestCase

A subclass of [unittest.TestCase](https://docs.python.org/3/library/unittest.html#unittest.TestCase) that adds this functionality:

- Some useful assertions like:
  - Checking that a callable [raises a certain exception](#django.test.SimpleTestCase.assertRaisesMessage).
  - Checking that a callable [triggers a certain warning](#django.test.SimpleTestCase.assertWarnsMessage).
  - Testing form field [rendering and error treatment](#django.test.SimpleTestCase.assertFieldOutput).
  - Testing [HTML responses for the presence/lack of a given fragment](#django.test.SimpleTestCase.assertContains).
  - Verifying that a template [has/hasn't been used to generate a given response content](#django.test.SimpleTestCase.assertTemplateUsed).
  - Verifying that two [URLs are equal](#django.test.SimpleTestCase.assertURLEqual).
  - Verifying an HTTP [redirect is performed by the app](#django.test.SimpleTestCase.assertRedirects).
  - Robustly testing two [HTML fragments for equality/inequality or containment](#django.test.SimpleTestCase.assertHTMLEqual).
  - Robustly testing two [XML fragments for equality/inequality](#django.test.SimpleTestCase.assertXMLEqual).
  - Robustly testing two [JSON fragments for equality](#django.test.SimpleTestCase.assertJSONEqual).

- The ability to run tests with [modified settings](#overriding-settings).
- Using the [client](#django.test.SimpleTestCase.client) [Client](#django.test.Client).

If your tests make any database queries, use subclasses [TransactionTestCase](#django.test.TransactionTestCase) or [TestCase](#django.test.TestCase).

- `SimpleTestCase.databases`: [SimpleTestCase](#django.test.SimpleTestCase) disallows database queries by default. This helps to avoid executing write queries which will affect other tests since each `SimpleTestCase` test isn’t run in a transaction. If you aren’t concerned about this problem, you can disable this behavior by setting the `databases` class attribute to `'__all__'` on your test class.

> **Warning**
>
> `SimpleTestCase` and its subclasses (e.g. `TestCase`, …) rely on `setUpClass()` and `tearDownClass()` to perform some class-wide initialization (e.g. overriding settings). If you need to override those methods, don’t forget to call the `super` implementation:

```python
class MyTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ...
    @classmethod
    def tearDownClass(cls):
        ...
        super().tearDownClass()
```

Be sure to account for Python’s behavior if an exception is raised during `setUpClass()`. If that happens, neither the tests in the class nor `tearDownClass()` are run. In the case of [django.test.TestCase](#django.test.TestCase), this will leak the transaction created in `super()` which results in various symptoms including a segmentation fault on some platforms (reported on macOS). If you want to intentionally raise an exception such as [unittest.SkipTest](https://docs.python.org/3/library/unittest.html#unittest.SkipTest) in `setUpClass()`, be sure to do it before calling `super()` to avoid this.

### TransactionTestCase

#### class TransactionTestCase

`TransactionTestCase` inherits from [SimpleTestCase](#django.test.SimpleTestCase) to add some database-specific features:

- Resetting the database to a known state at the end of each test to ease testing and using the ORM.
- Database [fixtures](#django.test.TransactionTestCase.fixtures).
- Test [skipping based on database backend features](#skipping-tests).
- The remaining specialized [assert*](#django.test.TransactionTestCase.assertQuerySetEqual) methods.

Django’s [TestCase](#django.test.TestCase) class is a more commonly used subclass of `TransactionTestCase` that makes use of database transaction facilities to speed up the process of resetting the database to a known state at the end of each test. A consequence of this, however, is that some database behaviors cannot be tested within a Django `TestCase` class. For instance, you cannot test that a block of code is executing within a transaction, as is required when using [select_for_update()](../../../ref/models/querysets/#django.db.models.query.QuerySet.select_for_update). In those cases, you should use `TransactionTestCase`.

`TransactionTestCase` and `TestCase` are identical except for the manner in which the database is reset to a known state and the ability for test code to test the effects of commit and rollback:

- A `TransactionTestCase` resets the database after the test runs by truncating all tables. A `TransactionTestCase` may call commit and rollback and observe the effects of these calls on the database.
- A `TestCase`, on the other hand, does not truncate tables after a test. Instead, it encloses the test code in a database transaction that is rolled back at the end of the test. This guarantees that the rollback at the end of the test restores the database to its initial state.

> **Warning**
>
> `TestCase` running on a database that does not support rollback (e.g. MySQL with the MyISAM storage engine), and all instances of `TransactionTestCase`, will roll back at the end of the test by deleting all data from the test database.

Apps [will not see their data reloaded](../overview/#test-case-serialized-rollback); if you need this functionality (for example, third-party apps should enable this) you can set `serialized_rollback = True` inside the `TestCase` body.

### TestCase

#### class TestCase

This is the most common class to use for writing tests in Django. It inherits from [TransactionTestCase](#django.test.TransactionTestCase) (and by extension [SimpleTestCase](#django.test.SimpleTestCase)). If your Django application doesn’t use a database, use [SimpleTestCase](#django.test.SimpleTestCase).

The class:

- Wraps the tests within two nested [atomic()](../../db/transactions/#django.db.transaction.atomic) blocks: one for the whole class and one for each test. Therefore, if you want to test some specific database transaction behavior, use [TransactionTestCase](#django.test.TransactionTestCase).
- Checks deferrable database constraints at the end of each test.

It also provides an additional method:

#### classmethod TestCase.setUpTestData()

The class-level `atomic` block described above allows the creation of initial data at the class level, once for the whole `TestCase`. This technique allows for faster tests as compared to using `setUp()`.

For example:

```python
from django.test import TestCase
class MyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.foo = Foo.objects.create(bar="Test")
        ...
    def test1(self):
        # Some test using self.foo
        ...
    def test2(self):
        # Some other test using self.foo
        ...
```

Note that if the tests are run on a database with no transaction support (for instance, MySQL with the MyISAM engine), `setUpTestData()` will be called before each test, negating the speed benefits.

Objects assigned to class attributes in `setUpTestData()` must support creating deep copies with [copy.deepcopy()](https://docs.python.org/3/library/copy.html#copy.deepcopy) in order to isolate them from alterations performed by each test methods.

#### classmethod TestCase.captureOnCommitCallbacks(using=DEFAULT_DB_ALIAS, execute=False)

Returns a context manager that captures [transaction.on_commit()](../../db/transactions/#django.db.transaction.on_commit) callbacks for the given database connection. It returns a list that contains, on exit of the context, the captured callback functions. From this list you can make assertions on the callbacks or call them to invoke their side effects, emulating a commit.

`using` is the alias of the database connection to capture callbacks for.

If `execute` is `True`, all the callbacks will be called as the context manager exits, if no exception occurred. This emulates a commit after the wrapped block of code.

For example:

```python
from django.core import mail
from django.test import TestCase
class ContactTests(TestCase):
    def test_post(self):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.client.post(
                "/contact/",
                {"message": "I like your site"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(callbacks), 1)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, "Contact Form")
            self.assertEqual(mail.outbox[0].body, "I like your site")
```

### LiveServerTestCase

#### class LiveServerTestCase

`LiveServerTestCase` does basically the same as [TransactionTestCase](#django.test.TransactionTestCase) with one extra feature: it launches a live Django server in the background on setup, and shuts it down on teardown. This allows the use of automated test clients other than the [Django dummy client](#test-client) such as, for example, the [Selenium](https://www.selenium.dev/) client, to execute a series of functional tests inside a browser and simulate a real user’s actions.

The live server listens on `localhost` and binds to port 0 which uses a free port assigned by the operating system. The server’s URL can be accessed with `self.live_server_url` during the tests.

To demonstrate how to use `LiveServerTestCase`, let’s write a Selenium test. First of all, you need to install the [selenium](https://pypi.org/project/selenium/) package:

```bash
$ python -mpipinstall"selenium >= 4.8.0"
```

Then, add a `LiveServerTestCase`-based test to your app’s tests module (for example: `myapp/tests.py`). For this example, we’ll assume you’re using the [staticfiles](../../../ref/contrib/staticfiles/#module-django.contrib.staticfiles) app and want to have static files served during the execution of your tests similar to what we get at development time with `DEBUG=True`, i.e. without having to collect them using [collectstatic](../../../ref/contrib/staticfiles/#django-admin-collectstatic). We’ll use the [StaticLiveServerTestCase](../../../ref/contrib/staticfiles/#django.contrib.staticfiles.testing.StaticLiveServerTestCase) subclass which provides that functionality. Replace it with `django.test.LiveServerTestCase` if you don’t need that.

The code for this test may look as follows:

```python
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ["user-data.json"]
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    def test_login(self):
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("myuser")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("secret")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()
```

Finally, you may run the test as follows:

```bash
$ ./manage.py test myapp.tests.MySeleniumTests.test_login
```

This example will automatically open Firefox then go to the login page, enter the credentials and press the “Log in” button. Selenium offers other drivers in case you do not have Firefox installed or wish to use another browser. The example above is just a tiny fraction of what the Selenium client can do; check out the [full reference](https://selenium-python.readthedocs.io/api.html) for more details.

> **Note**
>
> When using an in-memory SQLite database to run the tests, the same database connection will be shared by two threads in parallel: the thread in which the live server is run and the thread in which the test case is run. It’s important to prevent simultaneous database queries via this shared connection by the two threads, as that may sometimes randomly cause the tests to fail. So you need to ensure that the two threads don’t access the database at the same time. In particular, this means that in some cases (for example, just after clicking a link or submitting a form), you might need to check that a response is received by Selenium and that the next page is loaded before proceeding with further test execution. Do this, for example, by making Selenium wait until the `<body>` HTML tag is found in the response (requires Selenium > 2.13):

```python
def test_login(self):
    from selenium.webdriver.support.wait import WebDriverWait
    timeout = 2
    ...
    self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()
    # Wait until the response is received
    WebDriverWait(self.selenium, timeout).until(
        lambda driver: driver.find_element(By.TAG_NAME, "body")
    )
```

The tricky thing here is that there’s really no such thing as a “page load,” especially in modern web apps that generate HTML dynamically after the server generates the initial document. So, checking for the presence of `<body>` in the response might not necessarily be appropriate for all use cases. Please refer to the [Selenium FAQ](https://web.archive.org/web/20160129132110/http://code.google.com/p/selenium/wiki/FrequentlyAskedQuestions#Q:_WebDriver_fails_to_find_elements_/_Does_not_block_on_page_loa) and [Selenium documentation](https://www.selenium.dev/documentation/webdriver/waits/#explicit-waits) for more information.

## Test Cases Features

### Default Test Client

Every test case in a `django.test.*TestCase` instance has access to an instance of a Django test client. This client can be accessed as `self.client`. This client is recreated for each test, so you don’t have to worry about state (such as cookies) carrying over from one test to another.

This means, instead of instantiating a `Client` in each test:

```python
import unittest
from django.test import Client
class SimpleTest(unittest.TestCase):
    def test_details(self):
        client = Client()
        response = client.get("/customer/details/")
        self.assertEqual(response.status_code, 200)
    def test_index(self):
        client = Client()
        response = client.get("/customer/index/")
        self.assertEqual(response.status_code, 200)
```

…you can refer to `self.client`, like so:

```python
from django.test import TestCase
class SimpleTest(TestCase):
    def test_details(self):
        response = self.client.get("/customer/details/")
        self.assertEqual(response.status_code, 200)
    def test_index(self):
        response = self.client.get("/customer/index/")
        self.assertEqual(response.status_code, 200)
```

### Customizing the Test Client

If you want to use a different `Client` class (for example, a subclass with customized behavior), use the [client_class](#django.test.SimpleTestCase.client_class) class attribute:

```python
from django.test import Client, TestCase
class MyTestClient(Client):
    # Specialized methods for your environment
    ...
class MyTest(TestCase):
    client_class = MyTestClient
    def test_my_stuff(self):
        # Here self.client is an instance of MyTestClient...
        call_some_test_code()
```

### Fixture Loading

A test case class for a database-backed website isn’t much use if there isn’t any data in the database. Tests are more readable and it’s more maintainable to create objects using the ORM, for example in [TestCase.setUpTestData()](#django.test.TestCase.setUpTestData), however, you can also use [fixtures](../../db/fixtures/#fixtures-explanation).

A fixture is a collection of data that Django knows how to import into a database. For example, if your site has user accounts, you might set up a fixture of fake user accounts in order to populate your database during tests.

The most straightforward way of creating a fixture is to use the [manage.py dumpdata](../../../ref/django-admin/#django-admin-dumpdata) command. This assumes you already have some data in your database. See the [dumpdata documentation](../../../ref/django-admin/#django-admin-dumpdata) for more details.

Once you’ve created a fixture and placed it in a `fixtures` directory in one of your [INSTALLED_APPS](../../../ref/settings/#std-setting-INSTALLED_APPS), you can use it in your unit tests by specifying a `fixtures` class attribute on your [django.test.TestCase](#django.test.TestCase) subclass:

```python
from django.test import TestCase
from myapp.models import Animal
class AnimalTestCase(TestCase):
    fixtures = ["mammals.json", "birds"]
    def setUp(self):
        # Test definitions as before.
        call_setup_methods()
    def test_fluffy_animals(self):
        # A test that uses the fixtures.
        call_some_test_code()
```

Here’s specifically what will happen:

- During `setUpClass()`, all the named fixtures are installed. In this example, Django will install any JSON fixture named `mammals`, followed by any fixture named `birds`. See the [Fixtures](../../db/fixtures/#fixtures-explanation) topic for more details on defining and installing fixtures.

For most unit tests using [TestCase](#django.test.TestCase), Django doesn’t need to do anything else, because transactions are used to clean the database after each test for performance reasons. But for [TransactionTestCase](#django.test.TransactionTestCase), the following actions will take place:

- At the end of each test Django will flush the database, returning the database to the state it was in directly after [migrate](../../../ref/django-admin/#django-admin-migrate) was called.
- For each subsequent test, the fixtures will be reloaded before `setUp()` is run.

In any case, you can be certain that the outcome of a test will not be affected by another test or by the order of test execution.

By default, fixtures are only loaded into the `default` database. If you are using multiple databases and set [TransactionTestCase.databases](#django.test.TransactionTestCase.databases), fixtures will be loaded into all specified databases.

> **Changed in Django 5.2:**
>
> For [TransactionTestCase](#django.test.TransactionTestCase), fixtures were made available during `setUpClass()`.

### URLconf Configuration

If your application provides views, you may want to include tests that use the test client to exercise those views. However, an end user is free to deploy the views in your application at any URL of their choosing. This means that your tests can’t rely upon the fact that your views will be available at a particular URL. Decorate your test class or test method with `@override_settings(ROOT_URLCONF=...)` for URLconf configuration.

### Multi-Database Support

Django sets up a test database corresponding to every database that is defined in the [DATABASES](../../../ref/settings/#std-setting-DATABASES) definition in your settings and referred to by at least one test through `databases`.

However, a big part of the time taken to run a Django `TestCase` is consumed by the call to `flush` that ensures that you have a clean database at the end of each test run. If you have multiple databases, multiple flushes are required (one for each database), which can be a time consuming activity – especially if your tests don’t need to test multi-database activity.

As an optimization, Django only flushes the `default` database at the end of each test run. If your setup contains multiple databases, and you have a test that requires every database to be clean, you can use the `databases` attribute on the test suite to request extra databases to be flushed.

For example:

```python
class TestMyViews(TransactionTestCase):
    databases = {"default", "other"}
    def test_index_page_view(self):
        call_some_test_code()
```

This test case class will flush the `default` and `other` test databases after running `test_index_page_view`. You can also use `'__all__'` to specify that all of the test databases must be flushed.

The `databases` flag also controls which databases the [TransactionTestCase.fixtures](#django.test.TransactionTestCase.fixtures) are loaded into. By default, fixtures are only loaded into the `default` database.

Queries against databases not in `databases` will give assertion errors to prevent state leaking between tests.

By default, only the `default` database will be wrapped in a transaction during a `TestCase`’s execution and attempts to query other databases will result in assertion errors to prevent state leaking between tests.

Use the `databases` class attribute on the test class to request transaction wrapping against non-`default` databases.

For example:

```python
class OtherDBTests(TestCase):
    databases = {"other"}
    def test_other_db_query(self):
        ...
```

This test will only allow queries against the `other` database. Just like for [SimpleTestCase.databases](#django.test.SimpleTestCase.databases) and [TransactionTestCase.databases](#django.test.TransactionTestCase.databases), the `'__all__'` constant can be used to specify that the test should allow queries to all databases.

### Overriding Settings

> **Warning**
>
> Use the functions below to temporarily alter the value of settings in tests. Don’t manipulate `django.conf.settings` directly as Django won’t restore the original values after such manipulations.

#### SimpleTestCase.settings()

For testing purposes it’s often useful to change a setting temporarily and revert to the original value after running the testing code. For this use case Django provides a standard Python context manager (see [PEP 343](https://peps.python.org/pep-0343/)) called [settings()](#django.test.SimpleTestCase.settings), which can be used like this:

```python
from django.test import TestCase
class LoginTestCase(TestCase):
    def test_login(self):
        # First check for the default behavior
        response = self.client.get("/sekrit/")
        self.assertRedirects(response, "/accounts/login/?next=/sekrit/")
        # Then override the LOGIN_URL setting
        with self.settings(LOGIN_URL="/other/login/"):
            response = self.client.get("/sekrit/")
            self.assertRedirects(response, "/other/login/?next=/sekrit/")
```

This example will override the [LOGIN_URL](../../../ref/settings/#std-setting-LOGIN_URL) setting for the code in the `with` block and reset its value to the previous state afterward.

#### SimpleTestCase.modify_settings()

It can prove unwieldy to redefine settings that contain a list of values. In practice, adding or removing values is often sufficient. Django provides the [modify_settings()](#django.test.SimpleTestCase.modify_settings) context manager for easier settings changes:

```python
from django.test import TestCase
class MiddlewareTestCase(TestCase):
    def test_cache_middleware(self):
        with self.modify_settings(
            MIDDLEWARE={
                "append": "django.middleware.cache.FetchFromCacheMiddleware",
                "prepend": "django.middleware.cache.UpdateCacheMiddleware",
                "remove": [
                    "django.contrib.sessions.middleware.SessionMiddleware",
                    "django.contrib.auth.middleware.AuthenticationMiddleware",
                    "django.contrib.messages.middleware.MessageMiddleware",
                ],
            }
        ):
            response = self.client.get("/")
            # ...
```

For each action, you can supply either a list of values or a string. When the value already exists in the list, `append` and `prepend` have no effect; neither does `remove` when the value doesn’t exist.

#### override_settings(**kwargs)

In case you want to override a setting for a test method, Django provides the [override_settings()](#django.test.override_settings) decorator (see [PEP 318](https://peps.python.org/pep-0318/)). It’s used like this:

```python
from django.test import TestCase, override_settings
class LoginTestCase(TestCase):
    @override_settings(LOGIN_URL="/other/login/")
    def test_login(self):
        response = self.client.get("/sekrit/")
        self.assertRedirects(response, "/other/login/?next=/sekrit/")
```

The decorator can also be applied to [TestCase](#django.test.TestCase) classes:

```python
from django.test import TestCase, override_settings
@override_settings(LOGIN_URL="/other/login/")
class LoginTestCase(TestCase):
    def test_login(self):
        response = self.client.get("/sekrit/")
        self.assertRedirects(response, "/other/login/?next=/sekrit/")
```

#### modify_settings(*args, **kwargs)

Likewise, Django provides the [modify_settings()](#django.test.modify_settings) decorator:

```python
from django.test import TestCase, modify_settings
class MiddlewareTestCase(TestCase):
    @modify_settings(
        MIDDLEWARE={
            "append": "django.middleware.cache.FetchFromCacheMiddleware",
            "prepend": "django.middleware.cache.UpdateCacheMiddleware",
        }
    )
    def test_cache_middleware(self):
        response = self.client.get("/")
        # ...
```

The decorator can also be applied to test case classes:

```python
from django.test import TestCase, modify_settings
@modify_settings(
    MIDDLEWARE={
        "append": "django.middleware.cache.FetchFromCacheMiddleware",
        "prepend": "django.middleware.cache.UpdateCacheMiddleware",
    }
)
class MiddlewareTestCase(TestCase):
    def test_cache_middleware(self):
        response = self.client.get("/")
        # ...
```

> **Note**
>
> When given a class, these decorators modify the class directly and return it; they don’t create and return a modified copy of it. So if you try to tweak the above examples to assign the return value to a different name than `LoginTestCase` or `MiddlewareTestCase`, you may be surprised to find that the original test case classes are still equally affected by the decorator. For a given class, [modify_settings()](#django.test.modify_settings) is always applied after [override_settings()](#django.test.override_settings).

> **Warning**
>
> The settings file contains some settings that are only consulted during initialization of Django internals. If you change them with `override_settings`, the setting is changed if you access it via the `django.conf.settings` module, however, Django’s internals access it differently. Effectively, using [override_settings()](#django.test.override_settings) or [modify_settings()](#django.test.modify_settings) with these settings is probably not going to do what you expect it to do.

We do not recommend altering the [DATABASES](../../../ref/settings/#std-setting-DATABASES) setting. Altering the [CACHES](../../../ref/settings/#std-setting-CACHES) setting is possible, but a bit tricky if you are using internals that make using of caching, like [django.contrib.sessions](../../http/sessions/#module-django.contrib.sessions). For example, you will have to reinitialize the session backend in a test that uses cached sessions and overrides [CACHES](../../../ref/settings/#std-setting-CACHES).

Finally, avoid aliasing your settings as module-level constants as `override_settings()` won’t work on such values since they are only evaluated the first time the module is imported.

You can also simulate the absence of a setting by deleting it after settings have been overridden, like this:

```python
@override_settings()
def test_something(self):
    del settings.LOGIN_URL
    ...
```

When overriding settings, make sure to handle the cases in which your app’s code uses a cache or similar feature that retains state even if the setting is changed. Django provides the [django.test.signals.setting_changed](../../../ref/signals/#django.test.signals.setting_changed) signal that lets you register callbacks to clean up and otherwise reset state when settings are changed.

Django itself uses this signal to reset various data:

| Overridden settings | Data reset |
|---------------------|------------|
| USE_TZ, TIME_ZONE   | Databases timezone |
| TEMPLATES           | Template engines |
| FORM_RENDERER       | Default renderer |
| SERIALIZATION_MODULES | Serializers cache |
| LOCALE_PATHS, LANGUAGE_CODE | Default translation and loaded translations |
| STATIC_ROOT, STATIC_URL, STORAGES | Storages configuration |

> **Changed in Django 5.1:**
>
> Resetting the default renderer when the `FORM_RENDERER` setting is changed was added.

### Isolating Apps

#### utils.isolate_apps(*app_labels, attr_name=None, kwarg_name=None)

Registers the models defined within a wrapped context into their own isolated [apps](../../../ref/applications/#django.apps.apps) registry. This functionality is useful when creating model classes for tests, as the classes will be cleanly deleted afterward, and there is no risk of

---

# Testing Tools

## The Test Client

### Overview and a Quick Example

Django provides a test `Client` to simulate a user interacting with the code at the view level. The test `Client` is located in `django.test.Client` and is a Python class that acts as a dummy web browser for testing purposes.

### Making Requests

The test `Client` has methods that correspond to the standard HTTP methods. For example, `get()` simulates a GET request, `post()` simulates a POST request, and so on.

### Testing Responses

The test `Client` returns a `Response` object that contains the response to the request. The `Response` object has attributes such as `status_code`, `content`, and `context` that can be used to test the response.

### Exceptions

If you want to test that a view raises an exception, you can use the `assertRaises` method from the `unittest` module.

### Persistent State

The test `Client` maintains state between requests. This means that you can log in using one request and then make another request that requires authentication.

### Setting the Language

The test `Client` can be used to test views that use Django’s translation system. You can set the language for the test `Client` using the `headers` argument.

### Example

Here is an example of how to use the test `Client` to test a view:

```python
from django.test import TestCase

class MyViewTestCase(TestCase):
    def test_my_view(self):
        response = self.client.get('/my-url/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, world!')
```

## Provided Test Case Classes

Django provides several test case classes that can be used to test different aspects of a Django application.

### SimpleTestCase

`SimpleTestCase` is the simplest test case class provided by Django. It does not provide any database support, so it is useful for testing code that does not interact with the database.

### TransactionTestCase

`TransactionTestCase` is a test case class that provides database support. It creates a new database for each test and rolls back the database at the end of each test.

### TestCase

`TestCase` is a test case class that provides database support and test client support. It creates a new database for each test and rolls back the database at the end of each test. It also provides a test client that can be used to simulate user interactions with the code.

### LiveServerTestCase

`LiveServerTestCase` is a test case class that provides support for testing code that interacts with a live server. It starts a live server for each test and stops the server at the end of each test.

## Test Cases Features

### Default Test Client

Each test case class provided by Django has a default test client that can be used to simulate user interactions with the code.

### Customizing the Test Client

The test client can be customized by passing arguments to the test case class. For example, you can set the default headers for the test client by passing the `headers` argument to the test case class.

### Fixture Loading

Django provides support for loading fixtures into the database for testing purposes. Fixtures can be loaded using the `fixtures` attribute of the test case class.

### URLconf Configuration

The URLconf for the test client can be configured by setting the `urls` attribute of the test case class. This is useful for testing code that uses custom URLconfs.

### Multi-Database Support

Django provides support for testing code that interacts with multiple databases. The test case class can be configured to use multiple databases by setting the `databases` attribute.

### Overriding Settings

Django provides support for overriding settings for testing purposes. Settings can be overridden using the `override_settings` decorator or the `settings` context manager.

### Isolating Apps

Django provides support for isolating apps for testing purposes. Apps can be isolated using the `isolate_apps` decorator or the `isolate_apps` context manager.

### Emptying the Test Outbox

Django provides support for emptying the test outbox for testing purposes. The test outbox can be emptied using the `empty_outbox` method of the test case class.

### Assertions

Django provides several custom assertion methods that can be used to test web applications. These assertion methods are available on the test case class.

### Tagging Tests

Django provides support for tagging tests for testing purposes. Tests can be tagged using the `tag` decorator or the `tag` context manager.

## Testing Asynchronous Code

Django provides support for testing asynchronous code. Asynchronous code can be tested using the `AsyncClient` class.

## Email Services

Django provides support for testing email services. Email services can be tested using the `EmailTestCase` class.

## Management Commands

Django provides support for testing management commands. Management commands can be tested using the `call_command` function.

## Skipping Tests

Django provides support for skipping tests. Tests can be skipped using the `skipIf` and `skipUnless` decorators.