# Validators

## Writing Validators

A validator is a callable that takes a value and raises a `ValidationError` if it doesn’t meet some criteria. Validators can be useful for reusing validation logic between different types of fields.

For example, here’s a validator that only allows even numbers:

```python
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_even(value):
    if value % 2 != 0:
        raise ValidationError(
            _("%(value)s is not an even number"),
            params={'value': value},
        )
```

You can add this to a model field via the field’s `validators` argument:

```python
from django.db import models

class MyModel(models.Model):
    even_field = models.IntegerField(validators=[validate_even])
```

Because values are converted to Python before validators are run, you can even use the same validator with forms:

```python
from django import forms

class MyForm(forms.Form):
    even_field = forms.IntegerField(validators=[validate_even])
```

You can also use a class with a `__call__() method` for more complex or configurable validators. `RegexValidator`, for example, uses this technique. If a class-based validator is used in the `validators` model field option, you should make sure it is serializable by the migration framework by adding `deconstruct()` and `__eq__()` methods.

## How Validators Are Run

See the [form validation](https://docs.djangoproject.com/en/5.2/forms/validation/) for more information on how validators are run in forms, and [Validating objects](https://docs.djangoproject.com/en/5.2/models/instances/#validating-objects) for how they’re run in models. Note that validators will not be run automatically when you save a model, but if you are using a `ModelForm`, it will run your validators on any fields that are included in your form. See the [ModelForm documentation](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/) for information on how model validation interacts with forms.

## Built-in Validators

The `django.core.validators` module contains a collection of callable validators for use with model and form fields. They’re used internally but are available for use with your own fields, too. They can be used in addition to, or in lieu of custom `field.clean()` methods.

### `RegexValidator`

```python
class RegexValidator(regex=None, message=None, code=None, inverse_match=None, flags=0)
```

#### Parameters:

- **regex** – If not `None`, overrides `regex`. Can be a regular expression string or a pre-compiled regular expression.
- **message** – If not `None`, overrides `message`.
- **code** – If not `None`, overrides `code`.
- **inverse_match** – If not `None`, overrides `inverse_match`.
- **flags** – If not `None`, overrides `flags`. In that case, `regex` must be a regular expression string, or `TypeError` is raised.

A `RegexValidator` searches the provided `value` for a given regular expression with `re.search()`. By default, raises a `ValidationError` with `message` and `code` if a match **is not** found. Its behavior can be inverted by setting `inverse_match` to `True`, in which case the `ValidationError` is raised when a match **is** found.

- **regex**: The regular expression pattern to search for within the provided `value`, using `re.search()`. This may be a string or a pre-compiled regular expression created with `re.compile()`. Defaults to the empty string, which will be found in every possible `value`.
- **message**: The error message used by `ValidationError` if validation fails. Defaults to `"Enter a valid value"`.
- **code**: The error code used by `ValidationError` if validation fails. Defaults to `"invalid"`.
- **inverse_match**: The match mode for `regex`. Defaults to `False`.
- **flags**: The regex flags used when compiling the regular expression string `regex`. If `regex` is a pre-compiled regular expression, and `flags` is overridden, `TypeError` is raised. Defaults to `0`.

### `EmailValidator`

```python
class EmailValidator(message=None, code=None, allowlist=None)
```

#### Parameters:

- **message** – If not `None`, overrides `message`.
- **code** – If not `None`, overrides `code`.
- **allowlist** – If not `None`, overrides `allowlist`.

An `EmailValidator` ensures that a value looks like an email, and raises a `ValidationError` with `message` and `code` if it doesn’t. Values longer than 320 characters are always considered invalid.

- **message**: The error message used by `ValidationError` if validation fails. Defaults to `"Enter a valid email address"`.
- **code**: The error code used by `ValidationError` if validation fails. Defaults to `"invalid"`.
- **allowlist**: Allowlist of email domains. By default, a regular expression (the `domain_regex` attribute) is used to validate whatever appears after the `@` sign. However, if that string appears in the `allowlist`, this validation is bypassed. If not provided, the default `allowlist` is `['localhost']`. Other domains that don’t contain a dot won’t pass validation, so you’d need to add them to the `allowlist` as necessary.

### `DomainNameValidator`

**New in Django 5.1.**

```python
class DomainNameValidator(accept_idna=True, message=None, code=None)
```

A `RegexValidator` subclass that ensures a value looks like a domain name. Values longer than 255 characters are always considered invalid. IP addresses are not accepted as valid domain names.

In addition to the optional arguments of its parent `RegexValidator` class, `DomainNameValidator` accepts an extra optional attribute:

- **accept_idna**: Determines whether to accept internationalized domain names, that is, domain names that contain non-ASCII characters. Defaults to `True`.

### `URLValidator`

```python
class URLValidator(schemes=None, regex=None, message=None, code=None)
```

A `RegexValidator` subclass that ensures a value looks like a URL, and raises an error code of `'invalid'` if it doesn’t. Values longer than `max_length` characters are always considered invalid.

Loopback addresses and reserved IP spaces are considered valid. Literal IPv6 addresses ([RFC 3986 Section 3.2.2](https://datatracker.ietf.org/doc/html/rfc3986.html#section-3.2.2)) and Unicode domains are both supported.

In addition to the optional arguments of its parent `RegexValidator` class, `URLValidator` accepts an extra optional attribute:

- **schemes**: URL/URI scheme list to validate against. If not provided, the default list is `['http', 'https', 'ftp', 'ftps']`. As a reference, the IANA website provides a full list of [valid URI schemes](https://www.iana.org/assignments/uri-schemes/uri-schemes.xhtml).

  **Warning**: Values starting with `file:///` will not pass validation even when the `file` scheme is provided. Valid values must contain a host.

- **max_length**: The maximum length of values that could be considered valid. Defaults to 2048 characters.

### `validate_email`

An `EmailValidator` instance without any customizations.

### `validate_domain_name`

**New in Django 5.1.**

A `DomainNameValidator` instance without any customizations.

### `validate_slug`

A `RegexValidator` instance that ensures a value consists of only letters, numbers, underscores or hyphens.

### `validate_unicode_slug`

A `RegexValidator` instance that ensures a value consists of only Unicode letters, numbers, underscores, or hyphens.

### `validate_ipv4_address`

A `RegexValidator` instance that ensures a value looks like an IPv4 address.

### `validate_ipv6_address`

Uses `django.utils.ipv6` to check the validity of an IPv6 address.

### `validate_ipv46_address`

Uses both `validate_ipv4_address` and `validate_ipv6_address` to ensure a value is either a valid IPv4 or IPv6 address.

### `validate_comma_separated_integer_list`

A `RegexValidator` instance that ensures a value is a comma-separated list of integers.

### `int_list_validator`

```python
int_list_validator(sep=',', message=None, code='invalid', allow_negative=False)
```

Returns a `RegexValidator` instance that ensures a string consists of integers separated by `sep`. It allows negative integers when `allow_negative` is `True`.

### `MaxValueValidator`

```python
class MaxValueValidator(limit_value, message=None)
```

Raises a `ValidationError` with a code of `'max_value'` if `value` is greater than `limit_value`, which may be a callable.

### `MinValueValidator`

```python
class MinValueValidator(limit_value, message=None)
```

Raises a `ValidationError` with a code of `'min_value'` if `value` is less than `limit_value`, which may be a callable.

### `MaxLengthValidator`

```python
class MaxLengthValidator(limit_value, message=None)
```

Raises a `ValidationError` with a code of `'max_length'` if the length of `value` is greater than `limit_value`, which may be a callable.

### `MinLengthValidator`

```python
class MinLengthValidator(limit_value, message=None)
```

Raises a `ValidationError` with a code of `'min_length'` if the length of `value` is less than `limit_value`, which may be a callable.

### `DecimalValidator`

```python
class DecimalValidator(max_digits, decimal_places)
```

Raises `ValidationError` with the following codes:

- `'max_digits'` if the number of digits is larger than `max_digits`.
- `'max_decimal_places'` if the number of decimals is larger than `decimal_places`.
- `'max_whole_digits'` if the number of whole digits is larger than the difference between `max_digits` and `decimal_places`.

### `FileExtensionValidator`

```python
class FileExtensionValidator(allowed_extensions, message, code)
```

Raises a `ValidationError` with a code of `'invalid_extension'` if the extension of `value.name` (`value` is a `File`) isn’t found in `allowed_extensions`. The extension is compared case-insensitively with `allowed_extensions`.

**Warning**: Don’t rely on validation of the file extension to determine a file’s type. Files can be renamed to have any extension no matter what data they contain.

### `validate_image_file_extension`

Uses Pillow to ensure that `value.name` (`value` is a `File`) has [a valid image extension](https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html).

### `ProhibitNullCharactersValidator`

```python
class ProhibitNullCharactersValidator(message=None, code=None)
```

Raises a `ValidationError` if `str(value)` contains one or more null characters (`'\x00'`).

#### Parameters:

- **message** – If not `None`, overrides `message`.
- **code** – If not `None`, overrides `code`.

- **message**: The error message used by `ValidationError` if validation fails. Defaults to `"Null characters are not allowed."`.
- **code**: The error code used by `ValidationError` if validation fails. Defaults to `"null_characters_not_allowed"`.

### `StepValueValidator`

```python
class StepValueValidator(limit_value, message=None, offset=None)
```

Raises a `ValidationError` with a code of `'step_size'` if `value` is not an integral multiple of `limit_value`, which can be a float, integer or decimal value or a callable. When `offset` is set, the validation occurs against `limit_value` plus `offset`. For example, for `StepValueValidator(3, offset=1.4)` valid values include `1.4`, `4.4`, `7.4`, `10.4`, and so on.