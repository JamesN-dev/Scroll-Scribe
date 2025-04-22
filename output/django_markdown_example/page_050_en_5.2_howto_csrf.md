# How to use Django's CSRF protection

To take advantage of CSRF protection in your views, follow these steps:

1. The CSRF middleware is activated by default in the `MIDDLEWARE` setting. If you override that setting, remember that `'django.middleware.csrf.CsrfViewMiddleware'` should come before any view middleware that assume that CSRF attacks have been dealt with.

   If you disabled it, which is not recommended, you can use `csrf_protect()` on particular views you want to protect.

2. In any template that uses a POST form, use the `csrf_token` tag inside the `<form>` element if the form is for an internal URL, e.g.:

   ```
   <form method="post">{% csrf_token %}
   ```

   This should not be done for POST forms that target external URLs, since that would cause the CSRF token to be leaked, leading to a vulnerability.

3. In the corresponding view functions, ensure that `RequestContext` is used to render the response so that `{% csrf_token %}` will work properly. If you're using the `render()` function, generic views, or contrib apps, you are covered already since these all use `RequestContext`.

## Using CSRF protection with AJAX

While the above method can be used for AJAX POST requests, it has some inconveniences: you have to remember to pass the CSRF token in as POST data with every POST request. For this reason, there is an alternative method: on each XMLHttpRequest, set a custom `X-CSRFToken` header to the value of the CSRF token.

### Acquiring the token if `CSRF_USE_SESSIONS` and `CSRF_COOKIE_HTTPONLY` are `False`

The recommended source for the token is the `csrftoken` cookie. You can acquire the token like this:

```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');
```

### Setting the token on the AJAX request

Finally, you'll need to set the header on your AJAX request. Using the `fetch()` API:

```javascript
const request = new Request(
    /* URL */,
    {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin' // Do not send CSRF token to another domain.
    }
);
fetch(request).then(function(response) {
    // ...
});
```

## Using CSRF protection in Jinja2 templates

Django's Jinja2 template backend adds `{{ csrf_input }}` to the context of all templates which is equivalent to `{% csrf_token %}` in the Django template language:

```
<form method="post">{{ csrf_input }}
```

## Using the decorator method

Rather than adding `CsrfViewMiddleware` as a blanket protection, you can use the `csrf_protect()` decorator on particular views that need the protection. Use of the decorator by itself is not recommended, since if you forget to use it, you will have a security hole.

## Handling rejected requests

By default, a '403 Forbidden' response is sent to the user if an incoming request fails the checks performed by `CsrfViewMiddleware`. 

CSRF failures are logged as warnings to the `django.security.csrf` logger.

## Edge Cases

### Disabling CSRF protection for just a few views

Solution: use `csrf_exempt()` for views that don't need protection.

### Protecting a page that uses AJAX without an HTML form

Solution: use `ensure_csrf_cookie()` on the view that sends the page.

## CSRF protection in reusable applications

It is recommended that developers of reusable apps use the `csrf_protect` decorator on their views to ensure security against CSRF.