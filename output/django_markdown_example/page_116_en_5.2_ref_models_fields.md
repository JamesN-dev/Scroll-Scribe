# Model field reference

This document contains all the API references of `Field` including the [field options](#field-options) and [field types](#field-types) Django offers.

## See also

If the built-in fields don’t do the trick, you can try [django-localflavor](https://pypi.org/project/django-localflavor/) ([documentation](https://django-localflavor.readthedocs.io/)), which contains assorted pieces of code that are useful for particular countries and cultures.

Also, you can easily [write your own custom model fields](../../../howto/custom-model-fields/).

**Note**

Fields are defined in `django.db.models.fields`, but for convenience they’re imported into `django.db.models`. The standard convention is to use `from django.db import models` and refer to fields as `models.<Foo>Field`.

## Field options

The following arguments are available to all field types. All are optional.

### `null`

**Field.null**

If `True`, Django will store empty values as `NULL` in the database. Default is `False`.

Avoid using `null` on string-based fields such as `CharField` and `TextField`. The Django convention is to use an empty string, not `NULL`, as the “no data” state for string-based fields. If a string-based field has `null=False`, empty strings can still be saved for “no data”. If a string-based field has `null=True`, that means it has two possible values for “no data”: `NULL`, and the empty string. In most cases, it’s redundant to have two possible values for “no data”. One exception is when a `CharField` has both `unique=True` and `blank=True` set. In this situation, `null=True` is required to avoid unique constraint violations when saving multiple objects with blank values.

For both string-based and non-string-based fields, you will also need to set `blank=True` if you wish to permit empty values in forms, as the `null` parameter only affects database storage (see `blank`).

**Note**

When using the Oracle database backend, the value `NULL` will be stored to denote the empty string regardless of this attribute.

### `blank`

**Field.blank**

If `True`, the field is allowed to be blank. Default is `False`.

Note that this is different than `null`. `null` is purely database-related, whereas `blank` is validation-related. If a field has `blank=True`, form validation will allow entry of an empty value. If a field has `blank=False`, the field will be required.

#### Supplying missing values

`blank=True` can be used with fields having `null=False`, but this will require implementing `clean()` on the model in order to programmatically supply any missing values.

### `choices`

**Field.choices**

A mapping or iterable in the format described below to use as choices for this field. If choices are given, they’re enforced by [model validation](../../../topics/forms/modelforms/#django.forms.ModelForm) and the default form widget will be a select box with these choices instead of the standard text field.

If a mapping is given, the key element is the actual value to be set on the model, and the second element is the human readable name. For example:

```python
YEAR_IN_SCHOOL_CHOICES = {
    "FR": "Freshman",
    "SO": "Sophomore",
    "JR": "Junior",
    "SR": "Senior",
    "GR": "Graduate",
}
```

You can also pass a [sequence](https://docs.python.org/3/glossary.html#term-sequence) consisting itself of iterables of exactly two items (e.g. `[(A1, B1), (A2, B2), …]`). The first element in each tuple is the actual value to be set on the model, and the second element is the human-readable name. For example:

```python
YEAR_IN_SCHOOL_CHOICES = [
    ("FR", "Freshman"),
    ("SO", "Sophomore"),
    ("JR", "Junior"),
    ("SR", "Senior"),
    ("GR", "Graduate"),
]
```

`choices` can also be defined as a callable that expects no arguments and returns any of the formats described above. For example:

```python
def get_currencies():
    return {i: i for i in settings.CURRENCIES}

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=get_currencies)
```

Passing a callable for `choices` can be particularly handy when, for example, the choices are:

- the result of I/O-bound operations (which could potentially be cached), such as querying a table in the same or an external database, or accessing the choices from a static file.
- a list that is mostly stable but could vary from time to time or from project to project. Examples in this category are using third-party apps that provide a well-known inventory of values, such as currencies, countries, languages, time zones, etc.

Generally, it’s best to define choices inside a model class, and to define a suitably-named constant for each value:

```python
from django.db import models

class Student(models.Model):
    FRESHMAN = "FR"
    SOPHOMORE = "SO"
    JUNIOR = "JR"
    SENIOR = "SR"
    GRADUATE = "GR"
    YEAR_IN_SCHOOL_CHOICES = {
        FRESHMAN: "Freshman",
        SOPHOMORE: "Sophomore",
        JUNIOR: "Junior",
        SENIOR: "Senior",
        GRADUATE: "Graduate",
    }
    year_in_school = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default=FRESHMAN,
    )

    def is_upperclass(self):
        return self.year_in_school in {self.JUNIOR, self.SENIOR}
```

Though you can define a choices list outside of a model class and then refer to it, defining the choices and names for each choice inside the model class keeps all of that information with the class that uses it, and helps reference the choices (e.g, `Student.SOPHOMORE` will work anywhere that the `Student` model has been imported).

You can also collect your available choices into named groups that can be used for organizational purposes:

```python
MEDIA_CHOICES = {
    "Audio": {
        "vinyl": "Vinyl",
        "cd": "CD",
    },
    "Video": {
        "vhs": "VHS Tape",
        "dvd": "DVD",
    },
    "unknown": "Unknown",
}
```

The key of the mapping is the name to apply to the group and the value is the choices inside that group, consisting of the field value and a human-readable name for an option. Grouped options may be combined with ungrouped options within a single mapping (such as the `"unknown"` option in this example).

You can also use a sequence, e.g. a list of 2-tuples:

```python
MEDIA_CHOICES = [
    (
        "Audio",
        (
            ("vinyl", "Vinyl"),
            ("cd", "CD"),
        ),
    ),
    (
        "Video",
        (
            ("vhs", "VHS Tape"),
            ("dvd", "DVD"),
        ),
    ),
    ("unknown", "Unknown"),
]
```

Note that choices can be any sequence object – not necessarily a list or tuple. This lets you construct choices dynamically. But if you find yourself hacking `choices` to be dynamic, you’re probably better off using a proper database table with a `ForeignKey`. `choices` is meant for static data that doesn’t change much, if ever.

**Note**

A new migration is created each time the order of `choices` changes.

For each model field that has `choices` set, Django will normalize the choices to a list of 2-tuples and add a method to retrieve the human-readable name for the field’s current value. See [get_FOO_display()](../../../topics/forms/modelforms/#django.forms.ModelForm) in the database API documentation.

Unless `blank=False` is set on the field along with a `default` then a label containing `"---------"` will be rendered with the select box. To override this behavior, add a tuple to `choices` containing `None`; e.g. `(None, 'Your String For Display')`. Alternatively, you can use an empty string instead of `None` where this makes sense - such as on a `CharField`.

#### Enumeration types

In addition, Django provides enumeration types that you can subclass to define choices in a concise way:

```python
from django.utils.translation import gettext_lazy as _

class Student(models.Model):
    class YearInSchool(models.TextChoices):
        FRESHMAN = "FR", _("Freshman")
        SOPHOMORE = "SO", _("Sophomore")
        JUNIOR = "JR", _("Junior")
        SENIOR = "SR", _("Senior")
        GRADUATE = "GR", _("Graduate")

    year_in_school = models.CharField(
        max_length=2,
        choices=YearInSchool,
        default=YearInSchool.FRESHMAN,
    )

    def is_upperclass(self):
        return self.year_in_school in {
            self.YearInSchool.JUNIOR,
            self.YearInSchool.SENIOR,
        }
```

These work similar to [enum](https://docs.python.org/3/library/enum.html#module-enum) from Python’s standard library, but with some modifications:

- Enum member values are a tuple of arguments to use when constructing the concrete data type. Django supports adding an extra string value to the end of this tuple to be used as the human-readable name, or `label`. The `label` can be a lazy translatable string. Thus, in most cases, the member value will be a `(value, label)` 2-tuple. See below for [an example of subclassing choices](#field-choices-enum-subclassing) using a more complex data type. If a tuple is not provided, or the last item is not a (lazy) string, the `label` is [automatically generated](#field-choices-enum-auto-label) from the member name.
- A `.label` property is added on values, to return the human-readable name.
- A number of custom properties are added to the enumeration classes – `.choices`, `.labels`, `.values`, and `.names` – to make it easier to access lists of those separate parts of the enumeration.

**Warning**

These property names cannot be used as member names as they would conflict.

- The use of [enum.unique()](https://docs.python.org/3/library/enum.html#enum.unique) is enforced to ensure that values cannot be defined multiple times. This is unlikely to be expected in choices for a field.

Note that using `YearInSchool.SENIOR`, `YearInSchool['SENIOR']`, or `YearInSchool('SR')` to access or lookup enum members work as expected, as do the `.name` and `.value` properties on the members.

If you don’t need to have the human-readable names translated, you can have them inferred from the member name (replacing underscores with spaces and using title-case):

```python
>>> class Vehicle(models.TextChoices):
...     CAR = "C"
...     TRUCK = "T"
...     JET_SKI = "J"
...
>>> Vehicle.JET_SKI.label
'Jet Ski'
```

Since the case where the enum values need to be integers is extremely common, Django provides an `IntegerChoices` class. For example:

```python
class Card(models.Model):
    class Suit(models.IntegerChoices):
        DIAMOND = 1
        SPADE = 2
        HEART = 3
        CLUB = 4

    suit = models.IntegerField(choices=Suit)
```

It is also possible to make use of the [Enum Functional API](https://docs.python.org/3/howto/enum.html#functional-api) with the caveat that labels are automatically generated as highlighted above:

```python
>>> MedalType = models.TextChoices("MedalType", "GOLD SILVER BRONZE")
>>> MedalType.choices
[('GOLD', 'Gold'), ('SILVER', 'Silver'), ('BRONZE', 'Bronze')]
>>> Place = models.IntegerChoices("Place", "FIRST SECOND THIRD")
>>> Place.choices
[(1, 'First'), (2, 'Second'), (3, 'Third')]
```

If you require support for a concrete data type other than `int` or `str`, you can subclass `Choices` and the required concrete data type, e.g. [date](https://docs.python.org/3/library/datetime.html#datetime.date) for use with `DateField`:

```python
class MoonLandings(datetime.date, models.Choices):
    APOLLO_11 = 1969, 7, 20, "Apollo 11 (Eagle)"
    APOLLO_12 = 1969, 11, 19, "Apollo 12 (Intrepid)"
    APOLLO_14 = 1971, 2, 5, "Apollo 14 (Antares)"
    APOLLO_15 = 1971, 7, 30, "Apollo 15 (Falcon)"
    APOLLO_16 = 1972, 4, 21, "Apollo 16 (Orion)"
    APOLLO_17 = 1972, 12, 11, "Apollo 17 (Challenger)"
```

There are some additional caveats to be aware of:

- Enumeration types do not support [named groups](#field-choices-named-groups).
- Because an enumeration with a concrete data type requires all values to match the type, overriding the [blank label](#field-choices-blank-label) cannot be achieved by creating a member with a value of `None`. Instead, set the `__empty__` attribute on the class:

```python
class Answer(models.IntegerChoices):
    NO = 0, _("No")
    YES = 1, _("Yes")
    __empty__ = _("(Unknown)")
```

### `db_column`

**Field.db_column**

The name of the database column to use for this field. If this isn’t given, Django will use the field’s name.

If your database column name is an SQL reserved word, or contains characters that aren’t allowed in Python variable names – notably, the hyphen – that’s OK. Django quotes column and table names behind the scenes.

### `db_comment`

**Field.db_comment**

The comment on the database column to use for this field. It is useful for documenting fields for individuals with direct database access who may not be looking at your Django code. For example:

```python
pub_date = models.DateTimeField(
    db_comment="Date and time when the article was published",
)
```

### `db_default`

**Field.db_default**

The database-computed default value for this field. This can be a literal value or a database function, such as [Now](../../../topics/forms/modelforms/#django.forms.ModelForm):

```python
created = models.DateTimeField(db_default=Now())
```

More complex expressions can be used, as long as they are made from literals and database functions:

```python
month_due = models.DateField(
    db_default=TruncMonth(
        Now() + timedelta(days=90),
        output_field=models.DateField(),
    )
)
```

Database defaults cannot reference other fields or models. For example, this is invalid:

```python
end = models.IntegerField(db_default=F("start") + 50)
```

If both `db_default` and `Field.default` are set, `default` will take precedence when creating instances in Python code. `db_default` will still be set at the database level and will be used when inserting rows outside of the ORM or when adding a new field in a migration.

If a field has a `db_default` without a `default` set and no value is assigned to the field, a `DatabaseDefault` object is returned as the field value on unsaved model instances. The actual value for the field is determined by the database when the model instance is saved.

### `db_index`

**Field.db_index**

If `True`, a database index will be created for this field.

**Use the `indexes` option instead.**

Where possible, use the `Meta.indexes` option instead. In nearly all cases, `indexes` provides more functionality than `db_index`. `db_index` may be deprecated in the future.

### `db_tablespace`

**Field.db_tablespace**

The name of the [database tablespace](../../../topics/forms/modelforms/#django.forms.ModelForm) to use for this field’s index, if this field is indexed. The default is the project’s `DEFAULT_INDEX_TABLESPACE` setting, if set, or the `db_tablespace` of the model, if any. If the backend doesn’t support tablespaces for indexes, this option is ignored.

### `default`

**Field.default**

The default value for the field. This can be a value or a callable object. If callable it will be called every time a new object is created.

The default can’t be a mutable object (model instance, `list`, `set`, etc.), as a reference to the same instance of that object would be used as the default value in all new model instances. Instead, wrap the desired default in a callable. For example, if you want to specify a default `dict` for `JSONField`, use a function:

```python
def contact_default():
    return {"email": "to1@example.com"}

contact_info = JSONField("ContactInfo", default=contact_default)
```

`lambda`s can’t be used for field options like `default` because they can’t be [serialized by migrations](../../../topics/forms/modelforms/#django.forms.ModelForm). See that documentation for other caveats.

For fields like `ForeignKey` that map to model instances, defaults should be the value of the field they reference (`pk` unless `to_field` is set) instead of model instances.

The default value is used when new model instances are created and a value isn’t provided for the field. When the field is a primary key, the default is also used when the field is set to `None`.

The default value can also be set at the database level with `Field.db_default`.

### `editable`

**Field.editable**

If `False`, the field will not be displayed in the admin or any other `ModelForm`. It will also be skipped during [model validation](../../../topics/forms/modelforms/#django.forms.ModelForm). Default is `True`.

### `error_messages`

**Field.error_messages**

The `error_messages` argument lets you override the default messages that the field will raise. Pass in a dictionary with keys matching the error messages you want to override.

Error message keys include `null`, `blank`, `invalid`, `invalid_choice`, `unique`, and `unique_for_date`. Additional error message keys are specified for each field in the [Field types](#field-types) section below.

These error messages often don’t propagate to forms. See [Considerations regarding model’s error_messages](../../../topics/forms/modelforms/#django.forms.ModelForm).

### `help_text`

**Field.help_text**

Extra “help” text to be displayed with the form widget. It’s useful for documentation even if your field isn’t used on a form.

Note that this value is *not* HTML-escaped in automatically-generated forms. This lets you include HTML in `help_text` if you so desire. For example:

```python
help_text="Please use the following format: <em>YYYY-MM-DD</em>."
```

Alternatively you can use plain text and `django.utils.html.escape()` to escape any HTML special characters. Ensure that you escape any help text that may come from untrusted users to avoid a cross-site scripting attack.

### `primary_key`

**Field.primary_key**

If `True`, this field is the primary key for the model.

If you don’t specify `primary_key=True` for any field in your model and have not defined a composite primary key, Django will automatically add a field to hold the primary key. So, you don’t need to set `primary_key=True` on any of your fields unless you want to override the default primary-key behavior. The type of auto-created primary key fields can be specified per app in `AppConfig.default_auto_field` or globally in the `DEFAULT_AUTO_FIELD` setting. For more, see [Automatic primary key fields](../../../topics/forms/modelforms/#django.forms.ModelForm).

`primary_key=True` implies `null=False` and `unique=True`. Only one field per model can set `primary_key=True`. Composite primary keys must be defined using `CompositePrimaryKey` instead of setting this flag to `True` for all fields to maintain this invariant.

The primary key field is read-only. If you change the value of the primary key on an existing object and then save it, a new object will be created alongside the old one.

The primary key field is set to `None` when [deleting](../../../topics/forms/modelforms/#django.forms.ModelForm) an object.

**Changed in Django 5.2:**

The `CompositePrimaryKey` field was added.

### `unique`

**Field.unique**

If `True`, this field must be unique throughout the table.

This is enforced at the database level and by model validation. If you try to save a model with a duplicate value in a `unique` field, a `django.db.IntegrityError` will be raised by the model’s `save()` method.

This option is valid on all field types except `ManyToManyField` and `OneToOneField`.

Note that when `unique` is `True`, you don’t need to specify `db_index`, because `unique` implies the creation of an index.

### `unique_for_date`

**Field.unique_for_date**

Set this to the name of a `DateField` or `DateTimeField` to require that this field be unique for the value of the date field.

For example, if you have a field `title` that has `unique_for_date="pub_date"`, then Django wouldn’t allow the entry of two records with the same `title` and `pub_date`.

Note that if you set this to point to a `DateTimeField`, only the date portion of the field will be considered. Besides, when `USE_TZ` is `True`, the check will be performed in the [current time zone](../../../topics/forms/modelforms/#django.forms.ModelForm) at the time the object gets saved.

This is enforced by `Model.validate_unique()` during model validation but not at the database level. If any `unique_for_date` constraint involves fields that are not part of a `ModelForm` (for example, if one of the fields is listed in `exclude` or has `editable=False`), `Model.validate_unique()` will skip validation for that particular constraint.

### `unique_for_month`

**Field.unique_for_month**

Like `unique_for_date`, but requires the field to be unique with respect to the month.

### `unique_for_year`

**Field.unique_for_year**

Like `unique_for_date` and `unique_for_month`.

### `verbose_name`

**Field.verbose_name**

A human-readable name for the field. If the verbose name isn’t given, Django will automatically create it using the field’s attribute name, converting underscores to spaces. See [Verbose field names](../../../topics/forms/modelforms/#django.forms.ModelForm).

### `validators`

**Field.validators**

A list of validators to run for this field. See the [validators documentation](../../../topics/forms/modelforms/#django.forms.ModelForm) for more information.

## Field types

### `AutoField`

**class AutoField(**options)**

An `IntegerField` that automatically increments according to available IDs. You usually won’t need to use this directly; a primary key field will automatically be added to your model if you don’t specify otherwise. See [Automatic primary key fields](../../../topics/forms/modelforms/#django.forms.ModelForm).

### `BigAutoField`

**class BigAutoField(**options)**

A 64-bit integer, much like an `AutoField` except that it is guaranteed to fit numbers from `1` to `9223372036854775807`.

### `BigIntegerField`

**class BigIntegerField(**options)**

A 64-bit integer, much like an `IntegerField` except that it is guaranteed to fit numbers from `-9223372036854775808` to `9223372036854775807`. The default form widget for this field is a `NumberInput`.

### `BinaryField`

**class BinaryField(max_length=None, **options)**

A field to store raw binary data. It can be assigned `bytes`, `bytearray`, or `memoryview`.

By default, `BinaryField` sets `editable` to `False`, in which case it can’t be included in a `ModelForm`.

**BinaryField.max_length**

Optional. The maximum length (in bytes) of the field. The maximum length is enforced in Django’s validation using `MaxLengthValidator`.

#### Abusing `BinaryField`

Although you might think about storing files in the database, consider that it is bad design in 99% of the cases. This field is *not* a replacement for proper [static files](../../../topics/forms/modelforms/#django.forms.ModelForm) handling.

### `BooleanField`

**class BooleanField(**options)**

A true/false field.

The default form widget for this field is `CheckboxInput`, or `NullBooleanSelect` if `null=True`.

The default value of `BooleanField` is `None` when `Field.default` isn’t defined.

### `CompositePrimaryKey`

**New in Django 5.2.**

**class CompositePrimaryKey(*field_names, **options)**

A virtual field used for defining a composite primary key.

This field must be defined as the model’s `pk` attribute. If present, Django will create the underlying model table with a composite primary key.

The `*field_names` argument is a list of positional field names that compose the primary key.

See [Composite primary keys](../../../topics/forms/modelforms/#django.forms.ModelForm) for more details.

### `CharField`

**class CharField(max_length=None, **options)**

A string field, for small- to large-sized strings.

For large amounts of text, use `TextField`.

The default form widget for this field is a `TextInput`.

`CharField` has the following extra arguments:

**CharField.max_length**

The maximum length (in characters) of the field. The `max_length` is enforced at the database level and in Django’s validation using `MaxLengthValidator`. It’s required for all database backends included with Django except PostgreSQL and SQLite, which supports unlimited `VARCHAR` columns.

**Note**

If you are writing an application that must be portable to multiple database backends, you should be aware that there are restrictions on `max_length` for some backends. Refer to the [database backend notes](../../../topics/forms/modelforms/#django.forms.ModelForm) for details.

**Changed in Django 5.2:**

Support for unlimited `VARCHAR` columns was added on SQLite.

**CharField.db_collation**

Optional. The database collation name of the field.

**Note**

Collation names are not standardized. As such, this will not be portable across multiple database backends.

**Oracle**

Oracle supports collations only when the `MAX_STRING_SIZE` database initialization parameter is set to `EXTENDED`.

### `DateField`

**class DateField(auto_now=False, auto_now_add=False, **options)**

A date, represented in Python by a `datetime.date` instance. Has a few extra, optional arguments:

**DateField.auto_now**

Automatically set the field to now every time the object is saved. Useful for “last-modified” timestamps. Note that the current date is *always* used; it’s not just a default value that you can override.

The field is only automatically updated when calling `Model.save()`. The field isn’t updated when making updates to other fields in other ways such as `QuerySet.update()`, though you can specify a custom value for the field in an update like that.

**DateField.auto_now_add**

Automatically set the field to now when the object is first created. Useful for creation of timestamps. Note that the current date is *always* used; it’s not just a default value that you can override. So even if you set a value for this field when creating the object, it will be ignored. If you want to be able to modify this field, set the following instead of `auto_now_add=True`:

- For `DateField`: `default=date.today` - from `datetime.date.today()`
- For `DateTimeField`: `default=timezone.now` - from `django.utils.timezone.now()`

The default form widget for this field is a `DateInput`. The admin adds a JavaScript calendar, and a shortcut for “Today”. Includes an additional `invalid_date` error message key.

The options `auto_now_add`, `auto_now`, and `default` are mutually exclusive. Any combination of these options will result in an error.

**Note**

As currently implemented, setting `auto_now` or `auto_now_add` to `True` will cause the field to have `editable=False` and `blank=True` set.

**Note**

The `auto_now` and `auto_now_add` options will always use the date in the [default timezone](../../../topics/forms/modelforms/#django.forms.ModelForm) at the moment of creation or update. If you need something different, you may want to consider using your own callable default or overriding `save()` instead of using `auto_now` or `auto_now_add`; or using a `DateTimeField` instead of a `DateField` and deciding how to handle the conversion from datetime to date at display time.

**Warning**

Always use `DateField` with a `datetime.date` instance.

If you have a `datetime.datetime` instance, it’s recommended to convert it to a `datetime.date` first. If you don’t, `DateField` will localize the `datetime.datetime` to the [default timezone](../../../topics/forms/modelforms/#django.forms.ModelForm) and convert it to a `datetime.date` instance, removing its time component. This is true for both storage and comparison.

### `DateTimeField`

**class DateTimeField(auto_now=False, auto_now_add=False, **options)**

A date and time, represented in Python by a `datetime.datetime` instance. Takes the same extra arguments as `DateField`.

The default form widget for this field is a single `DateTimeInput`. The admin uses two separate `TextInput` widgets with JavaScript shortcuts.

**Warning**

Always use `DateTimeField` with a `datetime.datetime` instance.

If you have a `datetime.date` instance, it’s recommended to convert it to a `datetime.datetime` first. If you don’t, `DateTimeField` will use midnight in the [default timezone](../../../topics/forms/modelforms/#django.forms.ModelForm) for the time component. This is true for both storage and comparison. To compare the date portion of a `DateTimeField` with a `datetime.date` instance, use the `date` lookup.

### `DecimalField`

**class DecimalField(max_digits=None, decimal_places=None, **options)**

A fixed-precision decimal number, represented in Python by a `Decimal` instance. It validates the input using `DecimalValidator`.

Has the following **required** arguments:

**DecimalField.max_digits**

The maximum number of digits allowed in the number. Note that this number must be greater than or equal to `decimal_places`.

**DecimalField.decimal_places**

The number of decimal places to store with the number.

For example, to store numbers up to `999.99` with a resolution of 2 decimal places, you’d use:

```python
models.DecimalField(..., max_digits=5, decimal_places=2)
```

And to store numbers up to approximately one billion with a resolution of 10 decimal places:

```python
models.DecimalField(..., max_digits=19, decimal_places=10)
```

The default form widget for this field is a `NumberInput` when `localize` is `False` or `TextInput` otherwise.

**Note**

For more information about the differences between the `FloatField` and `DecimalField` classes, please see [FloatField vs. DecimalField](#floatfield-vs-decimalfield). You should also be aware of [SQLite limitations](../../../topics/forms/modelforms/#django.forms.ModelForm) of decimal fields.

### `DurationField`

**class DurationField(**options)**

A field for storing periods of time - modeled in Python by `timedelta`. When used on PostgreSQL, the data type used is an `interval` and on Oracle the data type is `INTERVAL DAY(9) TO SECOND(6)`. Otherwise a `bigint` of microseconds is used.

**Note**

Arithmetic with `DurationField` works in most cases. However on all databases other than PostgreSQL, comparing the value of a `DurationField` to arithmetic on `DateTimeField` instances will not work as expected.

### `EmailField`

**class EmailField(max_length=254, **options)**

A `CharField` that checks that the value is a valid email address using `EmailValidator`.

### `FileField`

**class FileField(upload_to='', storage=None, max_length=100, **options)**

A file-upload field.

**Note**

The `primary_key` argument isn’t supported and will raise an error if used.

Has the following optional arguments:

**FileField.upload_to**

This attribute provides a way of setting the upload directory and file name, and can be set in two ways. In both cases, the value is passed to the `Storage.save()` method.

If you specify a string value or a `Path`, it may contain `strftime()` formatting, which will be replaced by the date/time of the file upload (so that uploaded files don’t fill up the given directory). For example:

```python
class MyModel(models.Model):
    # file will be uploaded to MEDIA_ROOT/uploads
    upload = models.FileField(upload_to="uploads/")
    # or...
    # file will be saved to MEDIA_ROOT/uploads/2015/01/30
    upload = models.FileField(upload_to="uploads/%Y/%m/%d/")
```

If you are using the default `FileSystemStorage`, the string value will be appended to your `MEDIA_ROOT` path to form the location on the local filesystem where uploaded files will be stored. If you are using a different storage, check that storage’s documentation to see how it handles `upload_to`.

`upload_to` may also be a callable, such as a function. This will be called to obtain the upload path, including the filename. This callable must accept two arguments and return a Unix-style path (with forward slashes) to be passed along to the storage system. The two arguments are:

| Argument | Description |
|----------|-------------|
| `instance` | An instance of the model where the `FileField` is defined. More specifically, this is the particular instance where the current file is being attached. In most cases, this object will not have been saved to the database yet, so if it uses the default `AutoField`, *it might not yet have a value for its primary key field*. |
| `filename` | The filename that was originally given to the file. This may or may not be taken into account when determining the final destination path. |

For example:

```python
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.user.id, filename)

class MyModel(models.Model):
    upload = models.FileField(upload_to=user_directory_path)
```

**FileField.storage**

A storage object, or a callable which returns a storage object. This handles the storage and retrieval of your files. See [Managing files](../../../topics/forms/modelforms/#django.forms.ModelForm) for details on how to provide this object.

The default form widget for this field is a `ClearableFileInput`.

Using a `FileField` or an `ImageField` (see below) in a model takes a few steps:

1. In your settings file, you’ll need to define `MEDIA_ROOT` as the full path to a directory where you’d like Django to store uploaded files. (For performance, these files are not stored in the database.) Define `MEDIA_URL` as the base public URL of that directory. Make sure that this directory is writable by the web server’s user account.
2. Add the `FileField` or `ImageField` to your model, defining the `upload_to` option to specify a subdirectory of `MEDIA_ROOT` to use for uploaded files.
3. All that will be stored in your database is a path to the file (relative to `MEDIA_ROOT`). You’ll most likely want to use the convenience `url` attribute provided by Django. For example, if your `ImageField` is called `mug_shot`, you can get the absolute path to your image in a template with `{{ object.mug_shot.url }}`.

For example, say your `MEDIA_ROOT` is set to `'/home/media'`, and `upload_to` is set to `'photos/%Y/%m/%d'`. The `'%Y/%m/%d'` part of `upload_to` is `strftime()` formatting; `'%Y'` is the four-digit year, `'%m'` is the two-digit month and `'%d'` is the two-digit day. If you upload a file on Jan. 15, 2007, it will be saved in the directory `/home/media/photos/2007/01/15`.

If you wanted to retrieve the uploaded file’s on-disk filename, or the file’s size, you could use the `name` and `size` attributes respectively; for more information on the available attributes and methods, see the `File` class reference and the [Managing files](../../../topics/forms/modelforms/#django.forms.ModelForm) topic guide.

**Note**

The file is saved as part of saving the model in the database, so the actual file name used on disk cannot be relied on until after the model has been saved.

The uploaded file’s relative URL can be obtained using the `url` attribute. Internally, this calls the `url()` method of the underlying `Storage` class.

Note that whenever you deal with uploaded files, you should pay close attention to where you’re uploading them and what type of files they are, to avoid security holes. *Validate all uploaded files* so that you’re sure the files are what you think they are. For example, if you blindly let somebody upload files, without validation, to a directory that’s within your web server’s document root, then somebody could upload a CGI or PHP script and execute that script by visiting its URL on your site. Don’t allow that.

Also note that even an uploaded HTML file, since it can be executed by the browser (though not by the server), can pose security threats that are equivalent to XSS or CSRF attacks.

`FileField` instances are created in your database as `varchar` columns with a default max length of 100 characters. As with other fields, you can change the maximum length using the `max_length` argument.

#### `FileField` and `FieldFile`

**class FieldFile**

When you access a `FileField` on a model, you are given an instance of `FieldFile` as a proxy for accessing the underlying file.

The API of `FieldFile` mirrors that of `File`, with one key difference: *The object wrapped by the class is not necessarily a wrapper around Python’s built-in file object.* Instead, it is a wrapper around the result of the `Storage.open()` method, which may be a `File` object, or it may be a custom storage’s implementation of the `File` API.

In addition to the API inherited from `File` such as `read()` and `write()`, `FieldFile` includes several methods that can be used to interact with the underlying file:

**Warning**

Two methods of this class, `save()` and `delete()`, default to saving the model object of the associated `FieldFile` in the database.

**FieldFile.name**

The name of the file including the relative path from the root of the `Storage` of the associated `FileField`.

**FieldFile.path**

A read-only property to access the file’s local filesystem path by calling the `path()` method of the underlying `Storage` class.

**FieldFile.size**

The result of the underlying `Storage.size()` method.

**FieldFile.url**

A read-only property to access the file’s relative URL by calling the `url()` method of the underlying `Storage` class.

**FieldFile.open(mode='rb')**

Opens or reopens the file associated with this instance in the specified `mode`. Unlike the standard Python `open()` method, it doesn’t return a file descriptor.

Since the underlying file is opened implicitly when accessing it, it may be unnecessary to call this method except to reset the pointer to the underlying file or to change the `mode`.

**FieldFile.close()**

Behaves like the standard Python `file.close()` method and closes the file associated with this instance.

**FieldFile.save(name, content, save=True)**

This method takes a filename and file contents and passes them to the storage class for the field, then associates the stored file with the model field. If you want to manually associate file data with `FileField` instances on your model, the `save()` method is used to persist that file data.

Takes two required arguments: `name` which is the name of the file, and `content` which is an object containing the file’s contents. The optional `save` argument controls whether or not the model instance is saved after the file associated with this field has been altered. Defaults to `True`.

Note that the `content` argument should be an instance of `django.core.files.File`, not Python’s built-in file object. You can construct a `File` from an existing Python file object like this:

```python
from django.core.files import File
# Open an existing file using Python's built-in open()
f = open("/path/to/hello.world")
myfile = File(f)
```

Or you can construct one from a Python string like this:

```python
from django.core.files.base import ContentFile
myfile = ContentFile("hello world")
```

For more information, see [Managing files](../../../topics/forms/modelforms/#django.forms.ModelForm).

**FieldFile.delete(save=True)**

Deletes the file associated with this instance and clears all attributes on the field. Note: This method will close the file if it happens to be open when `delete()` is called.

The optional `save` argument controls whether or not the model instance is saved after the file associated with this field has been deleted. Defaults to `True`.

Note that when a model is deleted, related files are not deleted. If you need to cleanup orphaned files, you’ll need to handle it yourself (for instance, with a custom management command that can be run manually or scheduled to run periodically via e.g. cron).

### `FilePathField`

**class FilePathField(path='', match=None, recursive=False, allow_files=True, allow_folders=False, max_length=100, **options)**

A `CharField` whose choices are limited to the filenames in a certain directory on the filesystem. Has some special arguments, of which the first is **required**:

**FilePathField.path**

Required. The absolute filesystem path to a directory from which this `FilePathField` should get its choices. Example: `'/home/images'`.

`path` may also be a callable, such as a function to dynamically set the path at runtime. Example:

```python
import os
from django.conf import settings
from django.db import models

def images_path():
    return os.path.join(settings.LOCAL_FILE_DIR, "images")

class MyModel(models.Model):
    file = models.FilePathField(path=images_path)
```

**FilePathField.match**

Optional. A regular expression, as a string, that `FilePathField` will use to filter filenames. Note that the regex will be applied to the base filename, not the full path. Example: `'foo.*\.txt$'`, which will match a file called `foo23.txt` but not `bar.txt` or `foo23.png`.

**FilePathField.recursive**

Optional. Either `True` or `False`. Default is `False`. Specifies whether all subdirectories of `path` should be included

**FilePathField.allow_files**

Optional. Either `True` or `False`. Default is `True`. Specifies whether files in the specified location should be included. Either this or `allow_folders` must be `True`.

**FilePathField.allow_folders**

Optional. Either `True` or `False`. Default is `False`. Specifies whether folders in the specified location should be included. Either this or `allow_files` must be `True`.

The one potential gotcha is that `match` applies to the base filename, not the full path. So, this example:

```python
FilePathField(path="/home/images", match="foo.*", recursive=True)
```

…will match `/home/images/foo.png` but not `/home/images/foo/bar.png` because the `match` applies to the base filename (`foo.png` and `bar.png`).

`FilePathField` instances are created in your database as `varchar` columns with a default max length of 100 characters. As with other fields, you can change the maximum length using the `max_length` argument.

### `FloatField`

**class FloatField(**options)**

A floating-point number represented in Python by a `float` instance.

The default form widget for this field is a `NumberInput` when `localize` is `False` or `TextInput` otherwise.

**`FloatField` vs. `DecimalField`**

The `FloatField` class is sometimes mixed up with the `DecimalField` class. Although they both represent real numbers, they represent those numbers differently. `FloatField` uses Python’s `float` type internally, while `DecimalField` uses Python’s `Decimal` type. For information on the difference between the two, see Python’s documentation for the `decimal` module.

### `GeneratedField`

**class GeneratedField(expression, output_field, db_persist=None, **kwargs)**

A field that is always computed based on other fields in the model. This field is managed and updated by the database itself. Uses the `GENERATED ALWAYS` SQL syntax.

There are two kinds of generated columns: stored and virtual. A stored generated column is computed when it is written (inserted or updated) and occupies storage as if it were a regular column. A virtual generated column occupies no storage and is computed when it is read. Thus, a virtual generated column is similar to a view and a stored generated column is similar to a materialized view.

**GeneratedField.expression**

An `Expression` used by the database to automatically set the field value each time the model is changed.

The expressions should be deterministic and only reference fields within the model (in the same database table). Generated fields cannot reference other generated fields. Database backends can impose further restrictions.

**GeneratedField.output_field**

A model field instance to define the field’s data type.

**GeneratedField.db_persist**

Determines if the database column should occupy storage as if it were a real column. If `False`, the column acts as a virtual column and does not occupy database storage space.

PostgreSQL only supports persisted columns. Oracle only supports virtual columns.

**Refresh the data**

Since the database computes the value, the object must be reloaded to access the new value after `save()`, for example, by using `refresh_from_db()`.

**Database limitations**

There are many database-specific restrictions on generated fields that Django doesn’t validate and the database may raise an error e.g. PostgreSQL requires functions and operators referenced in a generated column to be marked as `IMMUTABLE`.

You should always check that `expression` is supported on your database. Check out [MariaDB](https://mariadb.com/kb/en/generated-columns/#expression-support), [MySQL](https://dev.mysql.com/doc/refman/en/create-table-generated-columns.html), [Oracle](https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/CREATE-TABLE.html#GUID-F9CE0CC3-13AE-4744-A43C-EAC7A71AAAB6__BABIIGBD), [PostgreSQL](https://www.postgresql.org/docs/current/ddl-generated-columns.html), or [SQLite](https://www.sqlite.org/gencol.html#limitations) docs.

### `GenericIPAddressField`

**class GenericIPAddressField(protocol='both', unpack_ipv4=False, **options)**

An IPv4 or IPv6 address, in string format (e.g. `192.0.2.30` or `2a02:42fe::4`). The default form widget for this field is a `TextInput`.

The IPv6 address normalization follows **RFC 4291 Section 2.2** section 2.2, including using the IPv4 format suggested in paragraph 3 of that section, like `::ffff:192.0.2.0`. For example, `2001:0::0:01` would be normalized to `2001::1`, and `::ffff:0a0a:0a0a` to `::ffff:10.10.10.10`. All characters are converted to lowercase.

**GenericIPAddressField.protocol**

Limits valid inputs to the specified protocol. Accepted values are `'both'` (default), `'IPv4'` or `'IPv6'`. Matching is case insensitive.

**GenericIPAddressField.unpack_ipv4**

Unpacks IPv4 mapped addresses like `::ffff:192.0.2.1`. If this option is enabled that address would be unpacked to `192.0.2.1`. Default is disabled. Can only be used when `protocol` is set to `'both'`.

If you allow for blank values, you have to allow for null values since blank values are stored as null.

### `ImageField`

**class ImageField(upload_to=None, height_field=None, width_field=None, max_length=100, **options)**

Inherits all attributes and methods from `FileField`, but also validates that the uploaded object is a valid image.

In addition to the special attributes that are available for `FileField`, an `ImageField` also has `height` and `width` attributes.

To facilitate querying on those attributes, `ImageField` has the following optional arguments:

**ImageField.height_field**

Name of a model field which is auto-populated with the height of the image each time an image object is set.

**ImageField.width_field**

Name of a model field which is auto-populated with the width of the image each time an image object is set.

Requires the [pillow](https://pypi.org/project/pillow/) library.

`ImageField` instances are created in your database as `varchar` columns with a default max length of 100 characters. As with other fields, you can change the maximum length using the `max_length` argument.

The default form widget for this field is a `ClearableFileInput`.

### `IntegerField`

**class IntegerField(**options)**

An integer. Values from `-2147483648` to `2147483647` are safe in all databases supported by Django.

It uses `MinValueValidator` and `MaxValueValidator` to validate the input based on the values that the default database supports.

The default form widget for this field is a `NumberInput` when `localize` is `False` or `TextInput` otherwise.

### `JSONField`

**class JSONField(encoder=None, decoder=None, **options)**

A field for storing JSON encoded data. In Python the data is represented in its Python native format: dictionaries, lists, strings, numbers, booleans and `None`.

`JSONField` is supported on MariaDB, MySQL, Oracle, PostgreSQL, and SQLite (with the [JSON1 extension enabled](../../../topics/forms/modelforms/#django.forms.ModelForm)).

**JSONField.encoder**

An optional `json.JSONEncoder` subclass to serialize data types not supported by the standard JSON serializer (e.g. `datetime.datetime` or `UUID`). For example, you can use the `DjangoJSONEncoder` class.

Defaults to `json.JSONEncoder`.

**JSONField.decoder**

An optional `json.JSONDecoder` subclass to deserialize the value retrieved from the

---

# Model Field Reference

## Field Options

### `null`

If `True`, Django will store empty values as `NULL` in the database. Default is `False`.

### `blank`

If `True`, the field is allowed to be blank. Default is `False`.

### `choices`

A list of two-tuples to use as choices for this field. If this is given, the default form widget will be a select box with these choices instead of the standard text field.

#### Enumeration Types

You can also use an enumeration type for the choices. For example:

```python
from django.db import models

class Runner(models.Model):
    MEDALS = (
        ('G', 'Gold'),
        ('S', 'Silver'),
        ('B', 'Bronze'),
    )
    name = models.CharField(max_length=60)
    medal = models.CharField(max_length=1, choices=MEDALS)
```

### `db_column`

The name of the database column to use for this field. If not specified, Django will use the field’s name.

### `db_comment`

The comment to include in the database schema for this field. This is not supported by all database backends.

### `db_default`

The default value for the database column. This is not used by Django, but is passed to the database when the table is created.

### `db_index`

If `True`, a database index will be created for this field.

### `db_tablespace`

The name of the database tablespace to use for this field. This is not supported by all database backends.

### `default`

The default value for the field. This can be a value or a callable object, in which case the object will be called every time a new object is created.

### `editable`

If `False`, the field will not be displayed in the admin or any other ModelForm. They are also skipped during model validation. Default is `True`.

### `error_messages`

A dictionary of error messages to use when validating this field. The keys are the error message keys, and the values are the error messages.

### `help_text`

Extra “help” text to be displayed with the form widget. It’s useful for documentation even if your field isn’t used on a form.

### `primary_key`

If `True`, this field is the primary key for the model.

### `unique`

If `True`, this field must be unique throughout the table.

### `unique_for_date`

If given, this field must be unique for the specified date field on the model.

### `unique_for_month`

If given, this field must be unique for the specified month field on the model.

### `unique_for_year`

If given, this field must be unique for the specified year field on the model.

### `verbose_name`

A verbose name for this field, for example “Person’s first name”.

### `validators`

A list of validators to run for this field.

## Field Types

### `AutoField`

An `IntegerField` that automatically increments according to available IDs. You usually won’t need to use this directly; a primary key field will automatically be added to your model if you don’t specify otherwise.

### `BigAutoField`

A 64-bit integer, much like an `AutoField` except that it is guaranteed to fit numbers from 1 to 9223372036854775807.

### `BigIntegerField`

A 64-bit integer, much like an `IntegerField` except that it is guaranteed to fit numbers from -9223372036854775808 to 9223372036854775807.

### `BinaryField`

A field to store raw binary data. It can be assigned bytes, bytearray, or memoryview objects, and is returned as a bytes object.

### `BooleanField`

A true/false field. The default form widget for this field is a CheckboxInput.

### `CompositePrimaryKey`

A composite primary key field. This field is used to define a primary key that consists of multiple fields.

### `CharField`

A field for storing strings. It is used to store short to medium-length strings. For large amounts of text, use `TextField`.

### `DateField`

A date, represented in Python by a `datetime.date` instance. Has some optional arguments for automatically populating the field with the current date.

### `DateTimeField`

A date and time, represented in Python by a `datetime.datetime` instance. Has some optional arguments for automatically populating the field with the current date and/or time.

### `DecimalField`

A fixed-point number, represented in Python by a `Decimal` instance. It is used to store numbers with a fixed number of decimal places.

### `DurationField`

A field for storing periods of time - modeled in Python by `timedelta`. When used on PostgreSQL, the data type used is an interval.

### `EmailField`

A `CharField` that checks that the value is a valid email address using `EmailValidator`.

### `FileField`

A field for uploading files. It has some additional attributes and methods.

#### `FileField` and `FieldFile`

`FileField` instances have two methods that are used to access the underlying file object: `open()` and `save()`. These methods are used to open and save the file, respectively.

### `FilePathField`

A `CharField` whose choices are limited to the filenames in a certain directory on the filesystem.

### `FloatField`

A floating-point number represented in Python by a `float` instance.

### `GeneratedField`

A field that is automatically computed by the database. It is similar to a view and a stored generated column is similar to a materialized view.

#### `GeneratedField.expression`

An `Expression` used by the database to automatically set the field value each time the model is changed.

#### `GeneratedField.output_field`

A model field instance to define the field’s data type.

#### `GeneratedField.db_persist`

Determines if the database column should occupy storage as if it were a real column. If `False`, the column acts as a virtual column and does not occupy database storage space.

### `GenericIPAddressField`

An IPv4 or IPv6 address, in string format (e.g. `192.0.2.30` or `2a02:42fe::4`).

#### `GenericIPAddressField.protocol`

Limits valid inputs to the specified protocol. Accepted values are `'both'` (default), `'IPv4'` or `'IPv6'`. Matching is case insensitive.

#### `GenericIPAddressField.unpack_ipv4`

Unpacks IPv4 mapped addresses like `::ffff:192.0.2.1`. If this option is enabled that address would be unpacked to `192.0.2.1`. Default is disabled. Can only be used when `protocol` is set to `'both'`.

### `ImageField`

Inherits all attributes and methods from `FileField`, but also validates that the uploaded object is a valid image.

#### `ImageField.height_field`

Name of a model field which is auto-populated with the height of the image each time an image object is set.

#### `ImageField.width_field`

Name of a model field which is auto-populated with the width of the image each time an image object is set.

### `IntegerField`

An integer. Values from -2147483648 to 2147483647 are safe in all databases supported by Django.

### `JSONField`

A field for storing JSON encoded data. In Python the data is represented in its Python native format: dictionaries, lists, strings, numbers, booleans and `None`.

#### `JSONField.encoder`

An optional `json.JSONEncoder` subclass to serialize data types not supported by the standard JSON serializer (e.g. `datetime.datetime` or `UUID`).

#### `JSONField.decoder`

An optional `json.JSONDecoder` subclass to deserialize the value retrieved from the database.

### `PositiveBigIntegerField`

Like a `PositiveIntegerField`, but only allows values under a certain (database-dependent) point. Values from 0 to 9223372036854775807 are safe in all databases supported by Django.

### `PositiveIntegerField`

Like an `IntegerField`, but must be either positive or zero (0). Values from 0 to 2147483647 are safe in all databases supported by Django. The value 0 is accepted for backward compatibility reasons.

### `PositiveSmallIntegerField`

Like a `PositiveIntegerField`, but only allows values under a certain (database-dependent) point. Values from 0 to 32767 are safe in all databases supported by Django.

### `SlugField`

Slug is a newspaper term. A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.

### `SmallAutoField`

Like an `AutoField`, but only allows values under a certain (database-dependent) limit. Values from 1 to 32767 are safe in all databases supported by Django.

### `SmallIntegerField`

Like an `IntegerField`, but only allows values under a certain (database-dependent) point. Values from -32768 to 32767 are safe in all databases supported by Django.

### `TextField`

A large text field. The default form widget for this field is a `Textarea`.

#### `TextField.db_collation`

Optional. The database collation name of the field.

### `TimeField`

A time, represented in Python by a `datetime.time` instance. Accepts the same auto-population options as `DateField`.

### `URLField`

A `CharField` for a URL, validated by `URLValidator`.

### `UUIDField`

A field for storing universally unique identifiers. Uses Python’s `UUID` class.

## Relationship Fields

### `ForeignKey`

A many-to-one relationship. Requires two positional arguments: the class to which the model is related and the `on_delete` option:

```python
from django.db import models

class Manufacturer(models.Model):
    name = models.TextField()

class Car(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
```

#### Database Representation

Behind the scenes, Django appends `"_id"` to the field name to create its database column name. In the above example, the database table for the `Car` model will have a `manufacturer_id` column.

#### Arguments

- `on_delete`: When an object referenced by a `ForeignKey` is deleted, Django will emulate the behavior of the SQL constraint specified by the `on_delete` argument.
- `limit_choices_to`: Sets a limit to the available choices for this field when this field is rendered using a `ModelForm` or the admin.
- `related_name`: The name to use for the relation from the related object back to this one.
- `related_query_name`: The name to use for the reverse filter name from the target model.
- `to_field`: The field on the related object that the relation is to.
- `db_constraint`: Controls whether or not a constraint should be created in the database for this foreign key.
- `swappable`: Controls the migration framework’s reaction if this `ForeignKey` is pointing at a swappable model.

### `ManyToManyField`

A many-to-many relationship. Requires a positional argument: the class to which the model is related, which works exactly the same as it does for `ForeignKey`, including recursive and lazy relationships.

#### Database Representation

Behind the scenes, Django creates an intermediary join table to represent the many-to-many relationship.

#### Arguments

- `related_name`: Same as `ForeignKey.related_name`.
- `related_query_name`: Same as `ForeignKey.related_query_name`.
- `limit_choices_to`: Same as `ForeignKey.limit_choices_to`.
- `symmetrical`: Only used in the definition of ManyToManyFields on self.
- `through`: Django will automatically generate a table to manage many-to-many relationships.
- `through_fields`: Only used when a custom intermediary model is specified.
- `db_table`: The name of the table to create for storing the many-to-many data.
- `db_constraint`: Controls whether or not constraints should be created in the database for the foreign keys in the intermediary table.
- `swappable`: Controls the migration framework’s reaction if this `ManyToManyField` is pointing at a swappable model.

### `OneToOneField`

A one-to-one relationship. Conceptually, this is similar to a `ForeignKey` with `unique=True`, but the “reverse” side of the relation will directly return a single object.

### Lazy Relationships

Lazy relationships allow referencing models by their names (as strings) or creating recursive relationships.

#### Recursive

To define a relationship where a model references itself, use `"self"` as the first argument of the relationship field:

```python
from django.db import models

class Manufacturer(models.Model):
    name = models.TextField()
    suppliers = models.ManyToManyField("self", symmetrical=False)
```

#### Relative

When a relationship needs to be created with a model that has not been defined yet, it can be referenced by its name rather than the model object itself:

```python
from django.db import models

class Car(models.Model):
    manufacturer = models.ForeignKey(
        "Manufacturer",
        on_delete=models.CASCADE,
    )

class Manufacturer(models.Model):
    name = models.TextField()
    suppliers = models.ManyToManyField("self", symmetrical=False)
```

#### Absolute

Absolute references specify a model using its `app_label` and class name, allowing for model references across different applications.

```python
class Car(models.Model):
    manufacturer = models.ForeignKey(
        "thirdpartyapp.Manufacturer",
        on_delete=models.CASCADE,
    )
```

## Field API Reference

### `Field`

`Field` is an abstract class that represents a database table column. Django uses fields to create the database table (`db_type()`), to map Python types to database (`get_prep_value()`) and vice-versa (`from_db_value()`).

#### `description`

A verbose description of the field, e.g. for the `django.contrib.admindocs` application.

#### `descriptor_class`

A class implementing the descriptor protocol that is instantiated and assigned to the model instance attribute.

#### `get_internal_type`

Returns a string naming this field for backend specific purposes. By default, it returns the class name.

#### `db_type`

Returns the database column data type for the `Field`, taking into account the `connection`.

#### `rel_db_type`

Returns the database column data type for fields such as `ForeignKey` and `OneToOneField` that point to the `Field`, taking into account the `connection`.

#### `get_prep_value`

Converts the value into the correct Python object. It acts as the reverse of `value_to_string()`, and is also called in `clean()`.

#### `get_db_prep_value`

Converts `value` to a backend-specific value. By default it returns `value` if `prepared=True` and `get_prep_value()` if is `False`.

#### `from_db_value`

Converts a value as returned by the database to a Python object. It is the reverse of `get_prep_value()`.

#### `get_db_prep_save`

Same as the `get_db_prep_value()`, but called when the field value must be *saved* to the database. By default returns `get_db_prep_value()`.

#### `pre_save`

Method called prior to `get_db_prep_save()` to prepare the value before being saved (e.g. for `DateField.auto_now`).

#### `to_python`

Converts the value into the correct Python object. It acts as the reverse of `value_to_string()`, and is also called in `clean()`.

#### `value_from_object`

Returns the field’s value for the given model instance.

#### `value_to_string`

Converts `obj` to a string. Used to serialize the value of the field.

#### `formfield`

Returns the default `django.forms.Field` of this field for `ModelForm`.

#### `deconstruct`

Returns a 4-tuple with enough information to recreate the field.

## Registering and Fetching Lookups

`Field` implements the lookup registration API. The API can be used to customize which lookups are available for a field class and its instances, and how lookups are fetched from a field.

## Field Attribute Reference

### Attributes for Fields

- `auto_created`: Boolean flag that indicates if the field was automatically created.
- `concrete`: Boolean flag that indicates if the field has a database column associated with it.
- `hidden`: Boolean flag that indicates if a field is hidden and should not be returned by `Options.get_fields()` by default.
- `is_relation`: Boolean flag that indicates if a field contains references to one or more other models for its functionality.
- `model`: Returns the model on which the field is defined.

### Attributes for Fields with Relations

- `many_to_many`: Boolean flag that is `True` if the field has a many-to-many relation; `False` otherwise.
- `many_to_one`: Boolean flag that is `True` if the field has a many-to-one relation, such as a `ForeignKey`; `False` otherwise.
- `one_to_many`: Boolean flag that is `True` if the field has a one-to-many relation, such as a `GenericRelation` or the reverse of a `ForeignKey`; `False` otherwise.
- `one_to_one`: Boolean flag that is `True` if the field has a one-to-one relation, such as a `OneToOneField`; `False` otherwise.
- `related_model`: Points to the model the field relates to.