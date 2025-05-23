# The Forms API

## Bound and unbound forms

A `Form` instance is either **bound** to a set of data, or **unbound**.

- If it’s **bound** to a set of data, it’s capable of validating that data and rendering the form as HTML with the data displayed in the HTML.
- If it’s **unbound**, it cannot do validation (because there’s no data to validate!), but it can still render the blank form as HTML.

### Form

To create an unbound `Form` instance, instantiate the class:

```python
>>> f = ContactForm()
```

To bind data to a form, pass the data as a dictionary as the first parameter to your `Form` class constructor:

```python
>>> data = {
... "subject":"hello",
... "message":"Hi there",
... "sender":"foo@example.com",
... "cc_myself":True,
... }
>>> f = ContactForm(data)
```

In this dictionary, the keys are the field names, which correspond to the attributes in your `Form` class. The values are the data you’re trying to validate. These will usually be strings, but there’s no requirement that they be strings; the type of data you pass depends on the `Field`, as we’ll see in a moment.

### Form.is_bound

If you need to distinguish between bound and unbound form instances at runtime, check the value of the form’s `is_bound` attribute:

```python
>>> f = ContactForm()
>>> f.is_bound
False
>>> f = ContactForm({"subject":"hello"})
>>> f.is_bound
True
```

Note that passing an empty dictionary creates a **bound** form with empty data:

```python
>>> f = ContactForm({})
>>> f.is_bound
True
```

If you have a bound `Form` instance and want to change the data somehow, or if you want to bind an unbound `Form` instance to some data, create another `Form` instance. There is no way to change data in a `Form` instance. Once a `Form` instance has been created, you should consider its data immutable, whether it has data or not.

## Using forms to validate data

### Form.clean()

Implement a `clean()` method on your `Form` when you must add custom validation for fields that are interdependent. See [Cleaning and validating fields that depend on each other](https://docs.djangoproject.com/en/5.2/ref/forms/validation/#validating-fields-with-clean) for example usage.

### Form.is_valid()

The primary task of a `Form` object is to validate data. With a bound `Form` instance, call the `is_valid()` method to run validation and return a boolean designating whether the data was valid:

```python
>>> data = {
... "subject":"hello",
... "message":"Hi there",
... "sender":"foo@example.com",
... "cc_myself":True,
... }
>>> f = ContactForm(data)
>>> f.is_valid()
True
```

Let’s try with some invalid data. In this case, `subject` is blank (an error, because all fields are required by default) and `sender` is not a valid email address:

```python
>>> data = {
... "subject":"",
... "message":"Hi there",
... "sender":"invalid email address",
... "cc_myself":True,
... }
>>> f = ContactForm(data)
>>> f.is_valid()
False
```

### Form.errors

Access the `errors` attribute to get a dictionary of error messages:

```python
>>> f.errors
{'sender': ['Enter a valid email address.'], 'subject': ['This field is required.']}
```

In this dictionary, the keys are the field names, and the values are lists of strings representing the error messages. The error messages are stored in lists because a field can have multiple error messages.

You can access `errors` without having to call `is_valid()` first. The form’s data will be validated the first time either you call `is_valid()` or access `errors`.

The validation routines will only get called once, regardless of how many times you access `errors` or call `is_valid()`. This means that if validation has side effects, those side effects will only be triggered once.

### Form.errors.as_data()

Returns a `dict` that maps fields to their original `ValidationError` instances.

```python
>>> f.errors.as_data()
{'sender': [ValidationError(['Enter a valid email address.'])],
'subject': [ValidationError(['This field is required.'])]}
```

Use this method anytime you need to identify an error by its `code`. This enables things like rewriting the error’s message or writing custom logic in a view when a given error is present. It can also be used to serialize the errors in a custom format (e.g. XML); for instance, `as_json()` relies on `as_data()`.

The need for the `as_data()` method is due to backwards compatibility. Previously `ValidationError` instances were lost as soon as their **rendered** error messages were added to the `Form.errors` dictionary. Ideally `Form.errors` would have stored `ValidationError` instances and methods with an `as_` prefix could render them, but it had to be done the other way around in order not to break code that expects rendered error messages in `Form.errors`.

### Form.errors.as_json(escape_html=False)

Returns the errors serialized as JSON.

```python
>>> f.errors.as_json()
{"sender": [{"message": "Enter a valid email address.", "code": "invalid"}],
"subject": [{"message": "This field is required.", "code": "required"}]}
```

By default, `as_json()` does not escape its output. If you are using it for something like AJAX requests to a form view where the client interprets the response and inserts errors into the page, you’ll want to be sure to escape the results on the client-side to avoid the possibility of a cross-site scripting attack. You can do this in JavaScript with `element.textContent = errorText` or with jQuery’s `$(el).text(errorText)` (rather than its `.html()` function).

If for some reason you don’t want to use client-side escaping, you can also set `escape_html=True` and error messages will be escaped so you can use them directly in HTML.

### Form.errors.get_json_data(escape_html=False)

Returns the errors as a dictionary suitable for serializing to JSON. `Form.errors.as_json()` returns serialized JSON, while this returns the error data before it’s serialized.

The `escape_html` parameter behaves as described in `Form.errors.as_json()`.

### Form.add_error(field, error)

This method allows adding errors to specific fields from within the `Form.clean()` method, or from outside the form altogether; for instance from a view.

The `field` argument is the name of the field to which the errors should be added. If its value is `None` the error will be treated as a non-field error as returned by `Form.non_field_errors()`.

The `error` argument can be a string, or preferably an instance of `ValidationError`. See [Raising ValidationError](https://docs.djangoproject.com/en/5.2/ref/forms/validation/#raising-validation-error) for best practices when defining form errors.

Note that `Form.add_error()` automatically removes the relevant field from `cleaned_data`.

### Form.has_error(field, code=None)

This method returns a boolean designating whether a field has an error with a specific error `code`. If `code` is `None`, it will return `True` if the field contains any errors at all.

To check for non-field errors use `NON_FIELD_ERRORS` as the `field` parameter.

### Form.non_field_errors()

This method returns the list of errors from `Form.errors` that aren’t associated with a particular field. This includes `ValidationError`s that are raised in `Form.clean()` and errors added using `Form.add_error(None, "...")`.

## Behavior of unbound forms

It’s meaningless to validate a form with no data, but, for the record, here’s what happens with unbound forms:

```python
>>> f = ContactForm()
>>> f.is_valid()
False
>>> f.errors
{}
```

## Initial form values

### Form.initial

Use `initial` to declare the initial value of form fields at runtime. For example, you might want to fill in a `username` field with the username of the current session.

To accomplish this, use the `initial` argument to a `Form`. This argument, if given, should be a dictionary mapping field names to initial values. Only include the fields for which you’re specifying an initial value; it’s not necessary to include every field in your form. For example:

```python
>>> f = ContactForm(initial={"subject":"Hi there!"})
```

These values are only displayed for unbound forms, and they’re not used as fallback values if a particular value isn’t provided.

If a `Field` defines `initial` and you include `initial` when instantiating the `Form`, then the latter `initial` will have precedence. In this example, `initial` is provided both at the field level and at the form instance level, and the latter gets precedence:

```python
>>> from django import forms
>>> class CommentForm(forms.Form):
... name = forms.CharField(initial="class")
... url = forms.URLField()
... comment = forms.CharField()
...
>>> f = CommentForm(initial={"name":"instance"}, auto_id=False)
>>> print(f)
<div>Name:<input type="text" name="name" value="instance" required></div>
<div>Url:<input type="url" name="url" required></div>
<div>Comment:<input type="text" name="comment" required></div>
```

### Form.get_initial_for_field(field, field_name)

Returns the initial data for a form field. It retrieves the data from `Form.initial` if present, otherwise trying `Field.initial`. Callable values are evaluated.

It is recommended to use `BoundField.initial` over `get_initial_for_field()` because `BoundField.initial` has a simpler interface. Also, unlike `get_initial_for_field()`, `BoundField.initial` caches its values. This is useful especially when dealing with callables whose return values can change (e.g. `datetime.now` or `uuid.uuid4`):

```python
>>> import uuid
>>> class UUIDCommentForm(CommentForm):
... identifier = forms.UUIDField(initial=uuid.uuid4)
...
>>> f = UUIDCommentForm()
>>> f.get_initial_for_field(f.fields["identifier"], "identifier")
UUID('972ca9e4-7bfe-4f5b-af7d-07b3aa306334')
>>> f.get_initial_for_field(f.fields["identifier"], "identifier")
UUID('1b411fab-844e-4dec-bd4f-e9b0495f04d0')
>>> # Using BoundField.initial, for comparison
>>> f["identifier"].initial
UUID('28a09c59-5f00-4ed9-9179-a3b074fa9c30')
>>> f["identifier"].initial
UUID('28a09c59-5f00-4ed9-9179-a3b074fa9c30')
```

## Checking which form data has changed

### Form.has_changed()

Use the `has_changed()` method on your `Form` when you need to check if the form data has been changed from the initial data.

```python
>>> data = {
... "subject":"hello",
... "message":"Hi there",
... "sender":"foo@example.com",
... "cc_myself":True,
... }
>>> f = ContactForm(data, initial=data)
>>> f.has_changed()
False
```

When the form is submitted, we reconstruct it and provide the original data so that the comparison can be done:

```python
>>> f = ContactForm(request.POST, initial=data)
>>> f.has_changed()
```

`has_changed()` will be `True` if the data from `request.POST` differs from what was provided in `initial` or `False` otherwise. The result is computed by calling `Field.has_changed()` for each field in the form.

### Form.changed_data

The `changed_data` attribute returns a list of the names of the fields whose values in the form’s bound data (usually `request.POST`) differ from what was provided in `initial`. It returns an empty list if no data differs.

```python
>>> f = ContactForm(request.POST, initial=data)
>>> if f.has_changed():
... print("The following fields changed: %s" % ", ".join(f.changed_data))
...
>>> f.changed_data
['subject', 'message']
```

## Accessing the fields from the form

### Form.fields

You can access the fields of `Form` instance from its `fields` attribute:

```python
>>> for row in f.fields.values():
... print(row)
...
<django.forms.fields.CharField object at 0x7ffaac632510>
<django.forms.fields.URLField object at 0x7ffaac632f90>
<django.forms.fields.CharField object at 0x7ffaac3aa050>
>>> f.fields["name"]
<django.forms.fields.CharField object at 0x7ffaac6324d0>
```

You can alter the field and `BoundField` of `Form` instance to change the way it is presented in the form:

```python
>>> f.as_div().split("</div>")[0]
'<div><label for="id_subject">Subject:</label><input type="text" name="subject" maxlength="100" required id="id_subject"></div>'
>>> f["subject"].label = "Topic"
>>> f.as_div().split("</div>")[0]
'<div><label for="id_subject">Topic:</label><input type="text" name="subject" maxlength="100" required id="id_subject"></div>'
```

Beware not to alter the `base_fields` attribute because this modification will influence all subsequent `ContactForm` instances within the same Python process:

```python
>>> f.base_fields["subject"].label_suffix = "?"
>>> another_f = ContactForm(auto_id=False)
>>> another_f.as_div().split("</div>")[0]
'<div><label for="id_subject">Subject?</label><input type="text" name="subject" maxlength="100" required id="id_subject"></div>'
```

## Accessing “clean” data

### Form.cleaned_data

Each field in a `Form` class is responsible not only for validating data, but also for “cleaning” it – normalizing it to a consistent format. This is a nice feature, because it allows data for a particular field to be input in a variety of ways, always resulting in consistent output.

For example, `DateField` normalizes input into a Python `datetime.date` object. Regardless of whether you pass it a string in the format `'1994-07-15'`, a `datetime.date` object, or a number of other formats, `DateField` will always normalize it to a `datetime.date` object as long as it’s valid.

Once you’ve created a `Form` instance with a set of data and validated it, you can access the clean data via its `cleaned_data` attribute:

```python
>>> data = {
... "subject":"hello",
... "message":"Hi there",
... "sender":"foo@example.com",
... "cc_myself":True,
... }
>>> f = ContactForm(data)
>>> f.is_valid()
True
>>> f.cleaned_data
{'cc_myself': True, 'message': 'Hi there', 'sender': 'foo@example.com', 'subject': 'hello'}
```

Note that any text-based field – such as `CharField` or `EmailField` – always cleans the input into a string. We’ll cover the encoding implications later in this document.

If your data does **not** validate, the `cleaned_data` dictionary contains only the valid fields:

```python
>>> data = {
... "subject":"",
... "message":"Hi there",
... "sender":"invalid email address",
... "cc_myself":True,
... }
>>> f = ContactForm(data)
>>> f.is_valid()
False
>>> f.cleaned_data
{'cc_myself': True, 'message': 'Hi there'}
```

`cleaned_data` will always **only** contain a key for fields defined in the `Form`, even if you pass extra data when you define the `Form`. In this example, we pass a bunch of extra fields to the `ContactForm` constructor, but `cleaned_data` contains only the form’s fields:

```python
>>> data = {
... "subject":"hello",
... "message":"Hi there",
... "sender":"foo@example.com",
... "cc_myself":True,
... "extra_field_1":"foo",
... "extra_field_2":"bar",
... "extra_field_3":"baz",
... }
>>> f = ContactForm(data)
>>> f.is_valid()
True
>>> f.cleaned_data
# Doesn't contain extra_field_1, etc.
{'cc_myself': True, 'message': 'Hi there', 'sender': 'foo@example.com', 'subject': 'hello'}
```

When the `Form` is valid, `cleaned_data` will include a key and value for **all** its fields, even if the data didn’t include a value for some optional fields. In this example, the data dictionary doesn’t include a value for the `nick_name` field, but `cleaned_data` includes it, with an empty value:

```python
>>> from django import forms
>>> class OptionalPersonForm(forms.Form):
... first_name = forms.CharField()
... last_name = forms.CharField()
... nick_name = forms.CharField(required=False)
...
>>> data = {"first_name":"John", "last_name":"Lennon"}
>>> f = OptionalPersonForm(data)
>>> f.is_valid()
True
>>> f.cleaned_data
{'nick_name': '', 'first_name': 'John', 'last_name': 'Lennon'}
```

In this above example, the `cleaned_data` value for `nick_name` is set to an empty string, because `nick_name` is `CharField`, and `CharField`s treat empty values as an empty string. Each field type knows what its “blank” value is – e.g., for `DateField`, it’s `None` instead of the empty string. For full details on each field’s behavior in this case, see the “Empty value” note for each field in the [Built-in Field classes](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#built-in-fields) section below.

You can write code to perform validation for particular form fields (based on their name) or for the form as a whole (considering combinations of various fields). More information about this is in [Form and field validation](https://docs.djangoproject.com/en/5.2/ref/forms/validation/).

## Outputting forms as HTML

The second task of a `Form` object is to render itself as HTML. To do so, `print` it:

```python
>>> f = ContactForm()
>>> print(f)
<div><label for="id_subject">Subject:</label><input type="text" name="subject" maxlength="100" required id="id_subject"></div>
<div><label for="id_message">Message:</label><input type="text" name="message" required id="id_message"></div>
<div><label for="id_sender">Sender:</label><input type="email" name="sender" required id="id_sender"></div>
<div><label for="id_cc_myself">Cc myself:</label><input type="checkbox" name="cc_myself" id="id_cc_myself"></div>
```

If the form is bound to data, the HTML output will include that data appropriately. For example, if a field is represented by an `<input type="text">`, the data will be in the `value` attribute. If a field is represented by an `<input type="checkbox">`, then that HTML will include `checked` if appropriate:

```python
>>> data = {
... "subject":"hello",
... "message":"Hi there",
... "sender":"foo@example.com",
... "cc_myself":True,
... }
>>> f = ContactForm(data)
>>> print(f)
<div><label for="id_subject">Subject:</label><input type="text" name="subject" value="hello" maxlength="100" required id="id_subject"></div>
<div><label for="id_message">Message:</label><input type="text" name="message" value="Hi there" required id="id_message"></div>
<div><label for="id_sender">Sender:</label><input type="email" name="sender" value="foo@example.com" required id="id_sender"></div>
<div><label for="id_cc_myself">Cc myself:</label><input type="checkbox" name="cc_myself" id="id_cc_myself" checked></div>
```

This default output wraps each field with a `<div>`. Notice the following:

- For flexibility, the output does **not** include the `<form>` and `</form>` tags or an `<input type="submit">` tag. It’s your job to do that.
- Each field type has a default HTML representation. `CharField` is represented by an `<input type="text">` and `EmailField` by an `<input type="email">`. `BooleanField(null=False)` is represented by an `<input type="checkbox">`. Note these are merely sensible defaults; you can specify which HTML to use for a given field by using widgets, which we’ll explain shortly.
- The HTML `name` for each tag is taken directly from its attribute name in the `ContactForm` class.
- The text label for each field – e.g. `'Subject:'`, `'Message:'` and `'Cc myself:'` is generated from the field name by converting all underscores to spaces and upper-casing the first letter. Again, note these are merely sensible defaults; you can also specify labels manually.
- Each text label is surrounded in an HTML `<label>` tag, which points to the appropriate form field via its `id`. Its `id`, in turn, is generated by prepending `id_` to the field name. The `id` attributes and `<label>` tags are included in the output by default, to follow best practices, but you can change that behavior.
- The output uses HTML5 syntax, targeting `<!DOCTYPE html>`. For example, it uses boolean attributes such as `checked` rather than the XHTML style of `checked='checked'`.

Although `<div>` output is the default output style when you `print` a form you can customize the output by using your own form template which can be set site-wide, per-form, or per-instance. See [Reusable form templates](https://docs.djangoproject.com/en/5.2/topics/forms/#reusable-form-templates).

### Default rendering

The default rendering when you `print` a form uses the following methods and attributes.

#### Form.template_name

The name of the template rendered if the form is cast into a string, e.g. via `print(form)` or in a template via `{{ form }}`.

By default, a property returning the value of the renderer’s `form_template_name`. You may set it as a string template name in order to override that for a particular form class.

#### Form.render(template_name=None, context=None, renderer=None)

The render method is called by `__str__` as well as the `Form.as_div()`, `Form.as_table()`, `Form.as_p()`, and `Form.as_ul()` methods. All arguments are optional and default to:

- `template_name`: `Form.template_name`
- `context`: Value returned by `Form.get_context()`
- `renderer`: Value returned by `Form.default_renderer`

By passing `template_name` you can customize the template used for just a single call.

#### Form.get_context()

Return the template context for rendering the form.

The available context is:

- `form`: The bound form.
- `fields`: All bound fields, except the hidden fields.
- `hidden_fields`: All hidden bound fields.
- `errors`: All non field related or hidden field related form errors.

#### Form.template_name_label

The template used to render a field’s `<label>`, used when calling `BoundField.label_tag()`/`legend_tag()`. Can be changed per form by overriding this attribute or more generally by overriding the default template, see also [Overriding built-in form templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#overriding-built-in-form-templates).

### Output styles

The recommended approach for changing form output style is to set a custom form template either site-wide, per-form, or per-instance. See [Reusable form templates](https://docs.djangoproject.com/en/5.2/topics/forms/#reusable-form-templates) for examples.

The following helper functions are provided for backward compatibility and are a proxy to `Form.render()` passing a particular `template_name` value.

> **Note**
>
> Of the framework provided templates and output styles, the default `as_div()` is recommended over the `as_p()`, `as_table()`, and `as_ul()` versions as the template implements `<fieldset>` and `<legend>` to group related inputs and is easier for screen reader users to navigate.

Each helper pairs a form method with an attribute giving the appropriate template name.

#### Form.as_div()

##### Form.template_name_div

The template used by `as_div()`. Default: `'django/forms/div.html'`.

##### Form.as_div()

`as_div()` renders the form as a series of `<div>` elements, with each `<div>` containing one field, such as:

```python
>>> f = ContactForm()
>>> f.as_div()
```

… gives HTML like:

```html
<div>
<label for="id_subject">Subject:</label>
<input type="text" name="subject" maxlength="100" required id="id_subject">
</div>
<div>
<label for="id_message">Message:</label>
<input type="text" name="message" required id="id_message">
</div>
<div>
<label for="id_sender">Sender:</label>
<input type="email" name="sender" required id="id_sender">
</div>
<div>
<label for="id_cc_myself">Cc myself:</label>
<input type="checkbox" name="cc_myself" id="id_cc_myself">
</div>
```

#### Form.as_p()

##### Form.template_name_p

The template used by `as_p()`. Default: `'django/forms/p.html'`.

##### Form.as_p()

`as_p()` renders the form as a series of `<p>` tags, with each `<p>` containing one field:

```python
>>> f = ContactForm()
>>> f.as_p()
'<p><label for="id_subject">Subject:</label> <input id="id_subject" type="text" name="subject" maxlength="100" required></p>\n<p><label for="id_message">Message:</label> <input type="text" name="message" id="id_message" required></p>\n<p><label for="id_sender">Sender:</label> <input type="text" name="sender" id="id_sender" required></p>\n<p><label for="id_cc_myself">Cc myself:</label> <input type="checkbox" name="cc_myself" id="id_cc_myself"></p>'
>>> print(f.as_p())
<p><label for="id_subject">Subject:</label> <input id="id_subject" type="text" name="subject" maxlength="100" required></p>
<p><label for="id_message">Message:</label> <input type="text" name="message" id="id_message" required></p>
<p><label for="id_sender">Sender:</label> <input type="email" name="sender" id="id_sender" required></p>
<p><label for="id_cc_myself">Cc myself:</label> <input type="checkbox" name="cc_myself" id="id_cc_myself"></p>
```

#### Form.as_ul()

##### Form.template_name_ul

The template used by `as_ul()`. Default: `'django/forms/ul.html'`.

##### Form.as_ul()

`as_ul()` renders the form as a series of `<li>` tags, with each `<li>` containing one field. It does **not** include the `<ul>` or `</ul>`, so that you can specify any HTML attributes on the `<ul>` for flexibility:

```python
>>> f = ContactForm()
>>> f.as_ul()
'<li><label for="id_subject">Subject:</label> <input id="id_subject" type="text" name="subject" maxlength="100" required></li>\n<li><label for="id_message">Message:</label> <input type="text" name="message" id="id_message" required></li>\n<li><label for="id_sender">Sender:</label> <input type="email" name="sender" id="id_sender" required></li>\n<li><label for="id_cc_myself">Cc myself:</label> <input type="checkbox" name="cc_myself" id="id_cc_myself"></li>'
>>> print(f.as_ul())
<li><label for="id_subject">Subject:</label> <input id="id_subject" type="text" name="subject" maxlength="100" required></li>
<li><label for="id_message">Message:</label> <input type="text" name="message" id="id_message" required></li>
<li><label for="id_sender">Sender:</label> <input type="email" name="sender" id="id_sender" required></li>
<li><label for="id_cc_myself">Cc myself:</label> <input type="checkbox" name="cc_myself" id="id_cc_myself"></li>
```

#### Form.as_table()

##### Form.template_name_table

The template used by `as_table()`. Default: `'django/forms/table.html'`.

##### Form.as_table()

`as_table()` renders the form as an HTML `<table>`:

```python
>>> f = ContactForm()
>>> f.as_table()
'<tr><th><label for="id_subject">Subject:</label></th><td><input id="id_subject" type="text" name="subject" maxlength="100" required></td></tr>\n<tr><th><label for="id_message">Message:</label></th><td><input type="text" name="message" id="id_message" required></td></tr>\n<tr><th><label for="id_sender">Sender:</label></th><td><input type="email" name="sender" id="id_sender" required></td></tr>\n<tr><th><label for="id_cc_myself">Cc myself:</label></th><td><input type="checkbox" name="cc_myself" id="id_cc_myself"></td></tr>'
>>> print(f.as_table())
<tr><th><label for="id_subject">Subject:</label></th><td><input id="id_subject" type="text" name="subject" maxlength="100" required></td></tr>
<tr><th><label for="id_message">Message:</label></th><td><input type="text" name="message" id="id_message" required></td></tr>
<tr><th><label for="id_sender">Sender:</label></th><td><input type="email" name="sender" id="id_sender" required></td></tr>
<tr><th><label for="id_cc_myself">Cc myself:</label></th><td><input type="checkbox" name="cc_myself" id="id_cc_myself"></td></tr>
```

### Styling required or erroneous form rows

#### Form.error_css_class

#### Form.required_css_class

It’s pretty common to style form rows and fields that are required or have errors. For example, you might want to present required form rows in bold and highlight errors in red.

The `Form` class has a couple of hooks you can use to add `class` attributes to required rows or to rows with errors: set the `Form.error_css_class` and/or `Form.required_css_class` attributes:

```python
from django import forms
class ContactForm(forms.Form):
    error_css_class = "error"
    required_css_class = "required"
    # ... and the rest of your fields here
```

Once you’ve done that, rows will be given `"error"` and/or `"required"` classes, as needed. The HTML will look something like:

```python
>>> f = ContactForm(data)
>>> print(f)
<div class="required"><label for="id_subject" class="required">Subject:</label> ...
<div class="required"><label for="id_message" class="required">Message:</label> ...
<div class="required"><label for="id_sender" class="required">Sender:</label> ...
<div><label for="id_cc_myself">Cc myself:</label> ...
>>> f["subject"].label_tag()
<label class="required" for="id_subject">Subject:</label>
>>> f["subject"].legend_tag()
<legend class="required" for="id_subject">Subject:</legend>
>>> f["subject"].label_tag(attrs={"class":"foo"})
<label for="id_subject" class="foo required">Subject:</label>
>>> f["subject"].legend_tag(attrs={"class":"foo"})
<legend for="id_subject" class="foo required">Subject:</legend>
```

You may further modify the rendering of form rows by using a [custom BoundField](https://docs.djangoproject.com/en/5.2/ref/forms/api/#custom-boundfield).

### Configuring form elements’ HTML `id` attributes and `<label>` tags

#### Form.auto_id

By default, the form rendering methods include:

- HTML `id` attributes on the form elements.
- The corresponding `<label>` tags around the labels. An HTML `<label>` tag designates which label text is associated with which form element. This small enhancement makes forms more usable and more accessible to assistive devices. It’s always a good idea to use `<label>` tags.

The `id` attribute values are generated by prepending `id_` to the form field names. This behavior is configurable, though, if you want to change the `id` convention or remove HTML `id` attributes and `<label>` tags entirely.

Use the `auto_id` argument to the `Form` constructor to control the `id` and label behavior. This argument must be `True`, `False` or a string.

If `auto_id` is `False`, then the form output will not include `<label>` tags nor `id` attributes:

```python
>>> f = ContactForm(auto_id=False)
>>> print(f)
<div>Subject:<input type="text" name="subject" maxlength="100" required></div>
<div>Message:<textarea name="message" cols="40" rows="10" required></textarea></div>
<div>Sender:<input type="email" name="sender" required></div>
<div>Cc myself:<input type="checkbox" name="cc_myself"></div>
```

If `auto_id` is set to `True`, then the form output **will** include `<label>` tags and will use the field name as its `id` for each form field:

```python
>>> f = ContactForm(auto_id=True)
>>> print(f)
<div><label for="subject">Subject:</label><input type="text" name="subject" maxlength="100" required id="subject"></div>
<div><label for="message">Message:</label><textarea name="message" cols="40" rows="10" required id="message"></textarea></div>
<div><label for="sender">Sender:</label><input type="email" name="sender" required id="sender"></div>
<div><label for="cc_myself">Cc myself:</label><input type="checkbox" name="cc_myself" id="cc_myself"></div>
```

If `auto_id` is set to a string containing the format character `'%s'`, then the form output will include `<label>` tags, and will generate `id` attributes based on the format string. For example, for a format string `'field_%s'`, a field named `subject` will get the `id` value `'field_subject'`. Continuing our example:

```python
>>> f = ContactForm(auto_id="id_for_%s")
>>> print(f)
<div><label for="id_for_subject">Subject:</label><input type="text" name="subject" maxlength="100" required id="id_for_subject"></div>
<div><label for="id_for_message">Message:</label><textarea name="message" cols="40" rows="10" required id="id_for_message"></textarea></div>
<div><label for="id_for_sender">Sender:</label><input type="email" name="sender" required id="id_for_sender"></div>
<div><label for="id_for_cc_myself">Cc myself:</label><input type="checkbox" name="cc_myself" id="id_for_cc_myself"></div>
```

If `auto_id` is set to any other true value – such as a string that doesn’t include `%s` – then the library will act as if `auto_id` is `True`.

By default, `auto_id` is set to the string `'id_%s'`.

#### Form.label_suffix

A translatable string (defaults to a colon (`:`) in English) that will be appended after any label name when a form is rendered.

It’s possible to customize that character, or omit it entirely, using the `label_suffix` parameter:

```python
>>> f = ContactForm(auto_id="id_for_%s", label_suffix="")
>>> print(f)
<div><label for="id_for_subject">Subject</label><input type="text" name="subject" maxlength="100" required id="id_for_subject"></div>
<div><label for="id_for_message">Message</label><textarea name="message" cols="40" rows="10" required id="id_for_message"></textarea></div>
<div><label for="id_for_sender">Sender</label><input type="email" name="sender" required id="id_for_sender"></div>
<div><label for="id_for_cc_myself">Cc myself</label><input type="checkbox" name="cc_myself" id="id_for_cc_myself"></div>
>>> f = ContactForm(auto_id="id_for_%s", label_suffix=" ->")
>>> print(f)
<div><label for="id_for_subject">Subject -&gt;</label><input type="text" name="subject" maxlength="100" required id="id_for_subject"></div>
<div><label for="id_for_message">Message -&gt;</label><textarea name="message" cols="40" rows="10" required id="id_for_message"></textarea></div>
<div><label for="id_for_sender">Sender -&gt;</label><input type="email" name="sender" required id="id_for_sender"></div>
<div><label for="id_for_cc_myself">Cc myself -&gt;</label><input type="checkbox" name="cc_myself" id="id_for_cc_myself"></div>
```

Note that the label suffix is added only if the last character of the label isn’t a punctuation character (in English, those are `.`, `!`, `?` or `:`).

Fields can also define their own `label_suffix`. This will take precedence over `Form.label_suffix`. The suffix can also be overridden at runtime using the `label_suffix` parameter to `label_tag()`/ `legend_tag()`.

#### Form.use_required_attribute

When set to `True` (the default), required form fields will have the `required` HTML attribute.

[Formsets](https://docs.djangoproject.com/en/5.2/topics/forms/formsets/) instantiate forms with `use_required_attribute=False` to avoid incorrect browser validation when adding and deleting forms from a formset.

### Configuring the rendering of a form’s widgets

#### Form.default_renderer

Specifies the [renderer](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/) to use for the form. Defaults to `None` which means to use the default renderer specified by the `FORM_RENDERER` setting.

You can set this as a class attribute when declaring your form or use the `renderer` argument to `Form.__init__()`. For example:

```python
from django import forms
class MyForm(forms.Form):
    default_renderer = MyRenderer()
```

or:

```python
form = MyForm(renderer=MyRenderer())
```

### Notes on field ordering

In the `as_p()`, `as_ul()` and `as_table()` shortcuts, the fields are displayed in the order in which you define them in your form class. For example, in the `ContactForm` example, the fields are defined in the order `subject`, `message`, `sender`, `cc_myself`. To reorder the HTML output, change the order in which those fields are listed in the class.

There are several other ways to customize the order:

#### Form.field_order

By default `Form.field_order=None`, which retains the order in which you define the fields in your form class. If `field_order` is a list of field names, the fields are ordered as specified by the list and remaining fields are appended according to the default order. Unknown field names in the list are ignored. This makes it possible to disable a field in a subclass by setting it to `None` without having to redefine ordering.

You can also use the `Form.field_order` argument to a `Form` to override the field order. If a `Form` defines `field_order` **and** you include `field_order` when instantiating the `Form`, then the latter `field_order` will have precedence.

#### Form.order_fields(field_order)

You may rearrange the fields any time using `order_fields()` with a list of field names as in `field_order`.

### How errors are displayed

If you render a bound `Form` object, the act of rendering will automatically run the form’s validation if it hasn’t already happened, and the HTML output will include the validation errors as a `<ul class="errorlist">`.

The following:

```python
>>> data = {
... "subject":"",
... "message":"Hi there",
... "sender":"invalid email address",
... "cc_myself":True,
... }
>>> ContactForm(data).as_div()
```

… gives HTML like:

```html
<div>
<label for="id_subject">Subject:</label>
<ul class="errorlist" id="id_subject_error"><li>This field is required.</li></ul>
<input type="text" name="subject" maxlength="100" required aria-invalid="true" aria-describedby="id_subject_error" id="id_subject">
</div>
<div>
<label for="id_message">Message:</label>
<textarea name="message" cols="40" rows="10" required id="id_message">Hi there</textarea>
</div>
<div>
<label for="id_sender">Sender:</label>
<ul class="errorlist" id="id_sender_error"><li>Enter a valid email address.</li></ul>
<input type="email" name="sender" value="invalid email address" maxlength="320" required aria-invalid="true" aria-describedby="id_sender_error" id="id_sender">
</div>
<div>
<label for="id_cc_myself">Cc myself:</label>
<input type="checkbox" name="cc_myself" id="id_cc_myself" checked>
</div>
```

Django’s default form templates will associate validation errors with their input by using the `aria-describedby` HTML attribute when the field has an `auto_id` and a custom `aria-describedby` is not provided. If a custom `aria-describedby` is set when defining the widget this will override the default value.

If the widget is rendered in a `<fieldset>` then `aria-describedby` is added to this element, otherwise it is added to the widget’s HTML element (e.g. `<input>`).

> **Changed in Django 5.2:**
>
> `aria-describedby` was added to associate errors with its input.

### Customizing the error list format

#### ErrorList(initlist=None, error_class=None, renderer=None, field_id=None)

By default, forms use `django.forms.utils.ErrorList` to format validation errors. `ErrorList` is a list like object where `initlist` is the list of errors. In addition this class has the following attributes and methods.

> **Changed in Django 5.2:**
>
> The `field_id` argument was added.

##### ErrorList.error_class

The CSS classes to be used when rendering the error list. Any provided classes are added to the default `errorlist` class.

##### ErrorList.renderer

Specifies the [renderer](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/) to use for `ErrorList`. Defaults to `None` which means to use the default renderer specified by the `FORM_RENDERER` setting.

##### ErrorList.field_id

> **New in Django 5.2.**

An `id` for the field for which the errors relate. This allows an HTML `id` attribute to be added in the error template and is useful to associate the errors with the field. The default template uses the format `id="{{ field_id }}_error"` and a value is provided by `Form.add_error()` using the field’s `auto_id`.

##### ErrorList.template_name

The name of the template used when calling `__str__` or `render()`. By default this is `'django/forms/errors/list/default.html'` which is a proxy for the `'ul.html'` template.

##### ErrorList.template_name_text

The name of the template used when calling `as_text()`. By default this is `'django/forms/errors/list/text.html'`. This template renders the errors as a list of bullet points.

##### ErrorList.template_name_ul

The name of the template used when calling `as_ul()`. By default this is `'django/forms/errors/list/ul.html'`. This template renders the errors in `<li>` tags with a wrapping `<ul>` with the CSS classes as defined by `error_class`.

##### ErrorList.get_context()

Return context for rendering of errors in a template.

The available context is:

- `errors` : A list of the errors.
- `error_class` : A string of CSS classes.

##### ErrorList.render(template_name=None, context=None, renderer=None)

The render method is called by `__str__` as well as by the `as_ul()` method.

All arguments are optional and will default to:

- `template_name`: Value returned by `template_name`
- `context`: Value returned by `get_context()`
- `renderer`: Value returned by `renderer`

##### ErrorList.as_text()

Renders the error list using the template defined by `template_name_text`.

##### ErrorList.as_ul()

Renders the error list using the template defined by `template_name_ul`.

If you’d like to customize the rendering of errors this can be achieved by overriding the `template_name` attribute or more generally by overriding the default template, see also [Overriding built-in form templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#overriding-built-in-form-templates).

### More granular output

The `as_p()`, `as_ul()`, and `as_table()` methods are shortcuts – they’re not the only way a form object can be displayed.

#### BoundField

Used to display HTML or access attributes for a single field of a `Form` instance.

The `__str__()` method of this object displays the HTML for this field.

You can use `Form.bound_field_class` and `Field.bound_field_class` to specify a different `BoundField` class per form or per field, respectively.

See [Customizing BoundField](https://docs.djangoproject.com/en/5.2/ref/forms/api/#custom-boundfield) for examples of overriding a `BoundField`.

To retrieve a single `BoundField`, use dictionary lookup syntax on your form using the field’s name as the key:

```python
>>> form = ContactForm()
>>> print(form["subject"])
<input id="id_subject" type="text" name="subject" maxlength="100" required>
```

To retrieve all `BoundField` objects, iterate the form:

```python
>>> form = ContactForm()
>>> for boundfield in form:
... print(boundfield)
...
<input id="id_subject" type="text" name="subject" maxlength="100" required>
<input type="text" name="message" id="id_message" required>
<input type="email" name="sender" id="id_sender" required>
<input type="checkbox" name="cc_myself" id="id_cc_myself">
```

The field-specific output honors the form object’s `auto_id` setting:

```python
>>> f = ContactForm(auto_id=False)
>>> print(f["message"])
<input type="text" name="message" required>
>>> f = ContactForm(auto_id="id_%s")
>>> print(f["message"])
<input type="text" name="message" id="id_message" required>
```

#### Attributes of BoundField

##### BoundField.aria_describedby

> **New in Django 5.2.**

Returns an `aria-describedby` reference to associate a field with its help text and errors. Returns `None` if `aria-describedby` is set in `Widget.attrs` to preserve the user defined attribute when rendering the form.

##### BoundField.auto_id

The HTML ID attribute for this `BoundField`. Returns an empty string if `Form.auto_id` is `False`.

##### BoundField.data

This property returns the data for this `BoundField` extracted by the widget’s `value_from_datadict()` method, or `None` if it wasn’t given:

```python
>>> unbound_form = ContactForm()
>>> print(unbound_form["subject"].data)
None
>>> bound_form = ContactForm(data={"subject":"My Subject"})
>>> print(bound_form["subject"].data)
My Subject
```

##### BoundField.errors

A [list-like object](https://docs.djangoproject.com/en/5.2/ref/forms/api/#ref-forms-error-list-format) that is displayed as an HTML `<ul class="errorlist">` when printed:

```python
>>> data = {"subject":"hi", "message":"", "sender":"", "cc_myself":""}
>>> f = ContactForm(data, auto_id=False)
>>> print(f["message"])
<input type="text" name="message" required aria-invalid="true">
>>> f["message"].errors
['This field is required.']
>>> print(f["message"].errors)
<ul class="errorlist"><li>This field is required.</li></ul>
>>> f["subject"].errors
[]
>>> print(f["subject"].errors)
>>>
>>> str(f["subject"].errors)
''
```

When rendering a field with errors, `aria-invalid="true"` will be set on the field’s widget to indicate there is an error to screen reader users.

##### BoundField.field

The form `Field` instance from the form class that this `BoundField` wraps.

##### BoundField.form

The `Form` instance this `BoundField` is bound to.

##### BoundField.help_text

The `help_text` of the field.

##### BoundField.html_name

The name that will be used in the widget’s HTML `name` attribute. It takes the `prefix` into account.

##### BoundField.id_for_label

Use this property to render the ID of this field. For example, if you are manually constructing a `<label>` in your template (despite the fact that `label_tag()`/`legend_tag()` will do this for you):

```html
<label for="{{ form.my_field.id_for_label }}">...{{ my_field }}</label>
```

By default, this will be the field’s name prefixed by `id_` ("`id_my_field`" for the example above). You may modify the ID by setting `attrs` on the field’s widget. For example, declaring a field like this:

```python
my_field = forms.CharField(widget=forms.TextInput(attrs={"id":"myFIELD"}))
```

and using the template above, would render something like:

```html
<label for="myFIELD">...<input id="myFIELD" type="text" name="my_field" required>
```

##### BoundField.initial

Use `BoundField.initial` to retrieve initial data for a form field. It retrieves the data from `Form.initial` if present, otherwise trying `Field.initial`. Callable values are evaluated. See [Initial form values](https://docs.djangoproject.com/en/5.2/ref/forms/api/#ref-forms-initial-form-values) for more examples.

`BoundField.initial` caches its return value, which is useful especially when dealing with callables whose return values can change (e.g. `datetime.now` or `uuid.uuid4`):

```python
>>> from datetime import datetime
>>> class DatedCommentForm(CommentForm):
... created = forms.DateTimeField(initial=datetime.now)
...
>>> f = DatedCommentForm()
>>> f["created"].initial
datetime.datetime(2021, 7, 27, 9, 5, 54)
>>> f["created"].initial
datetime.datetime(2021, 7, 27, 9, 5, 54)
```

Using `BoundField.initial` is recommended over `get_initial_for_field()`.

##### BoundField.is_hidden

Returns `True` if this `BoundField`’s widget is hidden.

##### BoundField.label

The `label` of the field. This is used in `label_tag()`/`legend_tag()`.

##### BoundField.name

The name of this field in the form:

```python
>>> f = ContactForm()
>>> print(f["subject"].name)
subject
>>> print(f["message"].name)
message
```

##### BoundField.template_name

The name of the template rendered with `BoundField.as_field_group()`.

A property returning the value of the `template_name` if set otherwise `field_template_name`.

##### BoundField.use_fieldset

Returns the value of this BoundField widget’s `use_fieldset` attribute.

##### BoundField.widget_type

Returns the lowercased class name of the wrapped field’s widget, with any trailing `input` or `widget` removed. This may be used when building forms where the layout is dependent upon the widget type. For example:

```html
{% for field in form %}
{% if field.widget_type == 'checkbox' %}
# render one way
{% else %}
# render another way
{% endif %}
{% endfor %}
```

#### Methods of BoundField

##### BoundField.as_field_group()

Renders the field using `BoundField.render()` with default values which renders the `BoundField`, including its label, help text and errors using the template’s `template_name` if set otherwise `field_template_name`

##### BoundField.as_hidden(attrs=None, **kwargs)

Returns a string of HTML for representing this as an `<input type="hidden">`.

`**kwargs` are passed to `as_widget()`.

This method is primarily used internally. You should use a widget instead.

##### BoundField.as_widget(widget=None, attrs=None, only_initial=False)

Renders the field by rendering the passed widget, adding any HTML attributes passed as `attrs`. If no widget is specified, then the field’s default widget will be used.

`only_initial` is used by Django internals and should not be set explicitly.

##### BoundField.css_classes(extra_classes=None)

When you use Django’s rendering shortcuts, CSS classes are used to indicate required form fields or fields that contain errors. If you’re manually rendering a form, you can access these CSS classes using the `css_classes` method:

```python
>>> f = ContactForm(data={"message":""})
>>> f["message"].css_classes()
'required'
```

If you want to provide some additional classes in addition to the error and required classes that may be required, you can provide those classes as an argument:

```python
>>> f = ContactForm(data={"message":""})
>>> f["message"].css_classes("foo bar")
'foo bar required'
```

##### BoundField.get_context()

Return the template context for rendering the field. The available context is `field` being the instance of the bound field.

##### BoundField.label_tag(contents=None, attrs=None, label_suffix=None, tag=None)

Renders a label tag for the form field using the template specified by `Form.template_name_label`.

The available context is:

- `field`: This instance of the `BoundField`.
- `contents`: By default a concatenated string of `BoundField.label` and `Form.label_suffix` (or `Field.label_suffix`, if set). This can be overridden by the `contents` and `label_suffix` arguments.
- `attrs`: A `dict` containing `for`, `Form.required_css_class`, and `id`. `id` is generated by the field’s widget `attrs` or `BoundField.auto_id`. Additional attributes can be provided by the `attrs` argument.
- `use_tag`: A boolean which is `True` if the label has an `id`. If `False` the default template omits the `tag`.
- `tag`: An optional string to customize the tag, defaults to `label`.

> **Tip**
>
> In your template `field` is the instance of the `BoundField`. Therefore `field.field` accesses `BoundField.field` being the field you declare, e.g. `forms.CharField`.

To separately render the label tag of a form field, you can call its `label_tag()` method:

```python
>>> f = ContactForm(data={"message":""})
>>> print(f["message"].label_tag())
<label for="id_message">Message:</label>
```

If you’d like to customize the rendering this can be achieved by overriding the `Form.template_name_label` attribute or more generally by overriding the default template, see also [Overriding built-in form templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#overriding-built-in-form-templates).

##### BoundField.legend_tag(contents=None, attrs=None, label_suffix=None)

Calls `label_tag()` with `tag='legend'` to render the label with `<legend>` tags. This is useful when rendering radio and multiple checkbox widgets where `<legend>` may be more appropriate than a `<label>`.

##### BoundField.render(template_name=None, context=None, renderer=None)

The render method is called by `as_field_group`. All arguments are optional and default to:

- `template_name`: `BoundField.template_name`
- `context`: Value returned by `BoundField.get_context()`
- `renderer`: Value returned by `Form.default_renderer`

By passing `template_name` you can customize the template used for just a single call.

##### BoundField.value()

Use this method to render the raw value of this field as it would be rendered by a `Widget`:

```python
>>> initial = {"subject":"welcome"}
>>> unbound_form = ContactForm(initial=initial)
>>> bound_form = ContactForm(data={"subject":"hi"}, initial=initial)
>>> print(unbound_form["subject"].value())
welcome
>>> print(bound_form["subject"].value())
hi
```

### Customizing BoundField

#### Form.bound_field_class

> **New in Django 5.2.**

Define a custom `BoundField` class to use when rendering the form. This takes precedence over the project-level `BaseRenderer.bound_field_class` (along with a custom `FORM_RENDERER`), but can be overridden by the field-level `Field.bound_field_class`.

If not defined as a class variable, `bound_field_class` can be set via the `bound_field_class` argument in the `Form` or `Field` constructor.

For compatibility reasons, a custom form field can still override `Field.get_bound_field()` to use a custom class, though any of the previous options are preferred.

You may want to use a custom `BoundField` if you need to access some additional information about a form field in a template and using a subclass of `Field` isn’t sufficient.

For example, if you have a `GPSCoordinatesField`, and want to be able to access additional information about the coordinates in a template, this could be implemented as follows:

```python
class GPSCoordinatesBoundField(BoundField):
    @property
    def country(self):
        """ Return the country the coordinates lie in or None if it can't be
         determined.
        """
        value = self.value()
        if value:
            return get_country_from_coordinates(value)
        else:
            return None
class GPSCoordinatesField(Field):
    bound_field_class = GPSCoordinatesBoundField
```

Now you can access the country in a template with `{{ form.coordinates.country }}`.

You may also want to customize the default form field template rendering. For example, you can override `BoundField.label_tag()` to add a custom class:

```python
class StyledLabelBoundField(BoundField):
    def label_tag(self, contents=None, attrs=None, label_suffix=None, tag=None):
        attrs = attrs or {}
        attrs["class"] = "wide"
        return super().label_tag(contents, attrs, label_suffix, tag)
class UserForm(forms.Form):
    bound_field_class = StyledLabelBoundField
    name = CharField()
```

This would update the default form rendering:

```python
>>> f = UserForm()
>>> print(f["name"].label_tag)
<label for="id_name" class="wide">Name:</label>
```

To add a CSS class to the wrapping HTML element of all fields, a `BoundField` can be overridden to return a different collection of CSS classes:

```python
class WrappedBoundField(BoundField):
    def css_classes(self, extra_classes=None):
        parent_css_classes = super().css_classes(extra_classes)
        return f"field-class {parent_css_classes}".strip()
class UserForm(forms.Form):
    bound_field_class = WrappedBoundField
    name = CharField()
```

This would update the form rendering as follows:

```python
>>> f = UserForm()
>>> print(f)
<div class="field-class"><label for="id_name">Name:</label><input type="text" name="name" required id="id_name"></div>
```

Alternatively, to override the `BoundField` class at the project level, `BaseRenderer.bound_field_class` can be defined on a custom `FORM_RENDERER`:

```python
mysite/renderers.py

from django.forms.renderers import DjangoTemplates
from .forms import CustomBoundField
class CustomRenderer(DjangoTemplates):
    bound_field_class = CustomBoundField
```

```python
settings.py

FORM_RENDERER = "mysite.renderers.CustomRenderer"
```

### Binding uploaded files to a form

Dealing with forms that have `FileField` and `ImageField` fields is a little more complicated than a normal form.

Firstly, in order to upload files, you’ll need to make sure that your `<form>` element correctly defines the `enctype` as `"multipart/form-data"`:

```html
<form enctype="multipart/form-data" method="post" action="/foo/">
```

Secondly, when you use the form, you need to bind the file data. File data is handled separately to normal form data, so when your form contains a `FileField` and `ImageField`, you will need to specify a second argument when you bind your form. So if we extend

---

## Bound and Unbound Forms

### Bound and Unbound Forms

- `id` is generated by the field’s widget `attrs` or `BoundField.auto_id`. Additional attributes can be provided by the `attrs` argument.
- `use_tag`: A boolean which is `True` if the label has an `id`. If `False` the default template omits the `tag`.
- `tag`: An optional string to customize the tag, defaults to `label`.

### Tip

In your template `field` is the instance of the `BoundField`. Therefore `field.field` accesses `BoundField.field` being the field you declare, e.g. `forms.CharField`.

To separately render the label tag of a form field, you can call its `label_tag()` method:

```python
>>> f = ContactForm(data={"message": ""})
>>> print(f["message"].label_tag())
<label for="id_message">Message:</label>
```

If you’d like to customize the rendering this can be achieved by overriding the `Form.template_name_label` attribute or more generally by overriding the default template, see also [Overriding built-in form templates](../renderers/#overriding-built-in-form-templates).

### BoundField.legend_tag(contents=None, attrs=None, label_suffix=None)

Calls `label_tag()` with `tag='legend'` to render the label with `<legend>` tags. This is useful when rendering radio and multiple checkbox widgets where `<legend>` may be more appropriate than a `<label>`.

### BoundField.render(template_name=None, context=None, renderer=None)

The render method is called by `as_field_group`. All arguments are optional and default to:

- `template_name`: `BoundField.template_name`
- `context`: Value returned by `BoundField.get_context()`
- `renderer`: Value returned by `Form.default_renderer`

By passing `template_name` you can customize the template used for just a single call.

### BoundField.value()

Use this method to render the raw value of this field as it would be rendered by a `Widget`:

```python
>>> initial = {"subject": "welcome"}
>>> unbound_form = ContactForm(initial=initial)
>>> bound_form = ContactForm(data={"subject": "hi"}, initial=initial)
>>> print(unbound_form["subject"].value())
welcome
>>> print(bound_form["subject"].value())
hi
```

## Customizing BoundField

### Form.bound_field_class

New in Django 5.2.

Define a custom `BoundField` class to use when rendering the form. This takes precedence over the project-level `BaseRenderer.bound_field_class` (along with a custom `FORM_RENDERER`), but can be overridden by the field-level `Field.bound_field_class`.

If not defined as a class variable, `bound_field_class` can be set via the `bound_field_class` argument in the `Form` or `Field` constructor.

For compatibility reasons, a custom form field can still override `Field.get_bound_field()` to use a custom class, though any of the previous options are preferred.

You may want to use a custom `BoundField` if you need to access some additional information about a form field in a template and using a subclass of `Field` isn’t sufficient.

For example, if you have a `GPSCoordinatesField`, and want to be able to access additional information about the coordinates in a template, this could be implemented as follows:

```python
class GPSCoordinatesBoundField(BoundField):
    @property
    def country(self):
        """ Return the country the coordinates lie in or None if it can't be determined. """
        value = self.value()
        if value:
            return get_country_from_coordinates(value)
        else:
            return None

class GPSCoordinatesField(Field):
    bound_field_class = GPSCoordinatesBoundField
```

Now you can access the country in a template with `{{ form.coordinates.country }}`.

You may also want to customize the default form field template rendering. For example, you can override `BoundField.label_tag()` to add a custom class:

```python
class StyledLabelBoundField(BoundField):
    def label_tag(self, contents=None, attrs=None, label_suffix=None, tag=None):
        attrs = attrs or {}
        attrs["class"] = "wide"
        return super().label_tag(contents, attrs, label_suffix, tag)

class UserForm(forms.Form):
    bound_field_class = StyledLabelBoundField
    name = CharField()
```

This would update the default form rendering:

```python
>>> f = UserForm()
>>> print(f["name"].label_tag)
<label for="id_name" class="wide">Name:</label>
```

To add a CSS class to the wrapping HTML element of all fields, a `BoundField` can be overridden to return a different collection of CSS classes:

```python
class WrappedBoundField(BoundField):
    def css_classes(self, extra_classes=None):
        parent_css_classes = super().css_classes(extra_classes)
        return f"field-class {parent_css_classes}".strip()

class UserForm(forms.Form):
    bound_field_class = WrappedBoundField
    name = CharField()
```

This would update the form rendering as follows:

```python
>>> f = UserForm()
>>> print(f)
<div class="field-class"><label for="id_name">Name:</label><input type="text" name="name" required id="id_name"></div>
```

Alternatively, to override the `BoundField` class at the project level, `BaseRenderer.bound_field_class` can be defined on a custom `FORM_RENDERER`:

```python
# mysite/renderers.py
from django.forms.renderers import DjangoTemplates
from .forms import CustomBoundField

class CustomRenderer(DjangoTemplates):
    bound_field_class = CustomBoundField
```

```python
# settings.py
FORM_RENDERER = "mysite.renderers.CustomRenderer"
```

## Binding Uploaded Files to a Form

Dealing with forms that have `FileField` and `ImageField` fields is a little more complicated than a normal form.

Firstly, in order to upload files, you’ll need to make sure that your `<form>` element correctly defines the `enctype` as `"multipart/form-data"`:

```html
<form enctype="multipart/form-data" method="post" action="/foo/">
```

Secondly, when you use the form, you need to bind the file data. File data is handled separately to normal form data, so when your form contains a `FileField` and `ImageField`, you will need to specify a second argument when you bind your form. So if we extend our ContactForm to include an `ImageField` called `mugshot`, we need to bind the file data containing the mugshot image:

```python
# Bound form with an image field
>>> from django.core.files.uploadedfile import SimpleUploadedFile
>>> data = {
... "subject": "hello",
... "message": "Hi there",
... "sender": "foo@example.com",
... "cc_myself": True,
...}
>>> file_data = {"mugshot": SimpleUploadedFile("face.jpg", b"file data")}
>>> f = ContactFormWithMugshot(data, file_data)
```

In practice, you will usually specify `request.FILES` as the source of file data (just like you use `request.POST` as the source of form data):

```python
# Bound form with an image field, data from the request
>>> f = ContactFormWithMugshot(request.POST, request.FILES)
```

Constructing an unbound form is the same as always – omit both form data *and* file data:

```python
# Unbound form with an image field
>>> f = ContactFormWithMugshot()
```

### Testing for Multipart Forms

#### Form.is_multipart()

If you’re writing reusable views or templates, you may not know ahead of time whether your form is a multipart form or not. The `is_multipart()` method tells you whether the form requires multipart encoding for submission:

```python
>>> f = ContactFormWithMugshot()
>>> f.is_multipart()
True
```

Here’s an example of how you might use this in a template:

```html
{% if form.is_multipart %}
<form enctype="multipart/form-data" method="post" action="/foo/">
{% else %}
<form method="post" action="/foo/">
{% endif %}
{{ form }}
</form>
```

## Subclassing Forms

If you have multiple `Form` classes that share fields, you can use subclassing to remove redundancy.

When you subclass a custom `Form` class, the resulting subclass will include all fields of the parent class(es), followed by the fields you define in the subclass.

In this example, `ContactFormWithPriority` contains all the fields from `ContactForm`, plus an additional field, `priority`. The `ContactForm` fields are ordered first:

```python
>>> class ContactFormWithPriority(ContactForm):
... priority = forms.CharField()
...
>>> f = ContactFormWithPriority(auto_id=False)
>>> print(f)
<div>Subject:<input type="text" name="subject" maxlength="100" required></div>
<div>Message:<textarea name="message" cols="40" rows="10" required></textarea></div>
<div>Sender:<input type="email" name="sender" required></div>
<div>Cc myself:<input type="checkbox" name="cc_myself"></div>
<div>Priority:<input type="text" name="priority" required></div>
```

It’s possible to subclass multiple forms, treating forms as mixins. In this example, `BeatleForm` subclasses both `PersonForm` and `InstrumentForm` (in that order), and its field list includes the fields from the parent classes:

```python
>>> from django import forms
>>> class PersonForm(forms.Form):
... first_name = forms.CharField()
... last_name = forms.CharField()
...
>>> class InstrumentForm(forms.Form):
... instrument = forms.CharField()
...
>>> class BeatleForm(InstrumentForm, PersonForm):
... haircut_type = forms.CharField()
...
>>> b = BeatleForm(auto_id=False)
>>> print(b)
<div>First name:<input type="text" name="first_name" required></div>
<div>Last name:<input type="text" name="last_name" required></div>
<div>Instrument:<input type="text" name="instrument" required></div>
<div>Haircut type:<input type="text" name="haircut_type" required></div>
```

It’s possible to declaratively remove a `Field` inherited from a parent class by setting the name of the field to `None` on the subclass. For example:

```python
>>> from django import forms
>>> class ParentForm(forms.Form):
... name = forms.CharField()
... age = forms.IntegerField()
...
>>> class ChildForm(ParentForm):
... name = None
...
>>> list(ChildForm().fields)
['age']
```

## Prefixes for Forms

### Form.prefix

You can put several Django forms inside one `<form>` tag. To give each `Form` its own namespace, use the `prefix` keyword argument:

```python
>>> mother = PersonForm(prefix="mother")
>>> father = PersonForm(prefix="father")
>>> print(mother)
<div><label for="id_mother-first_name">First name:</label><input type="text" name="mother-first_name" required id="id_mother-first_name"></div>
<div><label for="id_mother-last_name">Last name:</label><input type="text" name="mother-last_name" required id="id_mother-last_name"></div>
>>> print(father)
<div><label for="id_father-first_name">First name:</label><input type="text" name="father-first_name" required id="id_father-first_name"></div>
<div><label for="id_father-last_name">Last name:</label><input type="text" name="father-last_name" required id="id_father-last_name"></div>
```

The prefix can also be specified on the form class:

```python
>>> class PersonForm(forms.Form):
... ...
... prefix = "person"
...
```