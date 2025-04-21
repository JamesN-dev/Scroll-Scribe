# How to create custom model fields

## Introduction

The [model reference](../../topics/db/models/) documentation explains how to use Django's standard field classes – `CharField`, `DateField`, etc. For many purposes, those classes are all you'll need. Sometimes, though, the Django version won't meet your precise requirements, or you'll want to use a field that is entirely different from those shipped with Django.

Django's built-in field types don't cover every possible database column type – only the common types, such as `VARCHAR` and `INTEGER`. For more obscure column types, such as geographic polygons or even user-created types such as [PostgreSQL custom types](https://www.postgresql.org/docs/current/sql-createtype.html), you can define your own Django `Field` subclasses.

Alternatively, you may have a complex Python object that can somehow be serialized to fit into a standard database column type. This is another case where a `Field` subclass will help you use your object with your models.

### Our example object

Creating custom fields requires a bit of attention to detail. To make things easier to follow, we'll use a consistent example throughout this document: wrapping a Python object representing the deal of cards in a hand of [Bridge](https://en.wikipedia.org/wiki/Contract_bridge). Don't worry, you don't have to know how to play Bridge to follow this example. You only need to know that 52 cards are dealt out equally to four players, who are traditionally called *north*, *east*, *south* and *west*. Our class looks something like this:

```python
class Hand:
    """A hand of cards (bridge style)"""
    def __init__(self, north, east, south, west):
        # Input parameters are lists of cards ('Ah', '9s', etc.)
        self.north = north
        self.east = east
        self.south = south
        self.west = west
        # ... (other possibly useful methods omitted) ...
```

This is an ordinary Python class, with nothing Django-specific about it. We'd like to be able to do things like this in our models (we assume the `hand` attribute on the model is an instance of `Hand`):

```python
example = MyModel.objects.get(pk=1)
print(example.hand.north)
new_hand = Hand(north, east, south, west)
example.hand = new_hand
example.save()
```

We assign to and retrieve from the `hand` attribute in our model just like any other Python class. The trick is to tell Django how to handle saving and loading such an object.

In order to use the `Hand` class in our models, we **do not** have to change this class at all. This is ideal, because it means you can easily write model support for existing classes where you cannot change the source code.

> **Note**
> 
> You might only be wanting to take advantage of custom database column types and deal with the data as standard Python types in your models; strings, or floats, for example. This case is similar to our `Hand` example and we'll note any differences as we go along.

## Background theory

### Database storage

Let's start with model fields. If you break it down, a model field provides a way to take a normal Python object – string, boolean, `datetime`, or something more complex like `Hand` – and convert it to and from a format that is useful when dealing with the database. (Such a format is also useful for serialization, but as we'll see later, that is easier once you have the database side under control).

Fields in a model must somehow be converted to fit into an existing database column type. Different databases provide different sets of valid column types, but the rule is still the same: those are the only types you have to work with. Anything you want to store in the database must fit into one of those types.

Normally, you're either writing a Django field to match a particular database column type, or you will need a way to convert your data to, say, a string.

For our `Hand` example, we could convert the card data to a string of 104 characters by concatenating all the cards together in a predetermined order – say, all the *north* cards first, then the *east*, *south* and *west* cards. So `Hand` objects can be saved to text or character columns in the database.

### What does a field class do?

All of Django's fields (and when we say *fields* in this document, we always mean model fields and not [form fields](../../ref/forms/fields/)) are subclasses of [`django.db.models.Field`](../../ref/models/fields/#django.db.models.Field). Most of the information that Django records about a field is common to all fields – name, help text, uniqueness and so forth. Storing all that information is handled by `Field`. We'll get into the precise details of what `Field` can do later on; for now, suffice it to say that everything descends from `Field` and then customizes key pieces of the class behavior.

It's important to realize that a Django field class is not what is stored in your model attributes. The model attributes contain normal Python objects. The field classes you define in a model are actually stored in the `Meta` class when the model class is created (the precise details of how this is done are unimportant here). This is because the field classes aren't necessary when you're just creating and modifying attributes. Instead, they provide the machinery for converting between the attribute value and what is stored in the database or sent to the [serializer](../../topics/serialization/).

Keep this in mind when creating your own custom fields. The Django `Field` subclass you write provides the machinery for converting between your Python instances and the database/serializer values in various ways (there are differences between storing a value and using a value for lookups, for example). If this sounds a bit tricky, don't worry – it will become clearer in the examples below. Just remember that you will often end up creating two classes when you want a custom field:

- The first class is the Python object that your users will manipulate. They will assign it to the model attribute, they will read from it for displaying purposes, things like that. This is the `Hand` class in our example.

- The second class is the `Field` subclass. This is the class that knows how to convert your first class back and forth between its permanent storage form and the Python form.

## Writing a field subclass

When planning your [`Field`](../../ref/models/fields/#django.db.models.Field) subclass, first give some thought to which existing [`Field`](../../ref/models/fields/#django.db.models.Field) class your new field is most similar to. Can you subclass an existing Django field and save yourself some work? If not, you should subclass the [`Field`](../../ref/models/fields/#django.db.models.Field) class, from which everything is descended.

Initializing your new field is a matter of separating out any arguments that are specific to your case from the common arguments and passing the latter to the `__init__()` method of [`Field`](../../ref/models/fields/#django.db.models.Field) (or your parent class).

In our example, we'll call our field `HandField`. (It's a good idea to call your [`Field`](../../ref/models/fields/#django.db.models.Field) subclass `<Something>Field`, so it's easily identifiable as a [`Field`](../../ref/models/fields/#django.db.models.Field) subclass.) It doesn't behave like any existing field, so we'll subclass directly from [`Field`](../../ref/models/fields/#django.db.models.Field):

```python
from django.db import models

class HandField(models.Field):
    description = "A hand of cards (bridge style)"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 104
        super().__init__(*args, **kwargs)
```

Our `HandField` accepts most of the standard field options (see the list below), but we ensure it has a fixed length, since it only needs to hold 52 card values plus their suits; 104 characters in total.

> **Note**
> 
> Many of Django's model fields accept options that they don't do anything with. For example, you can pass both [`editable`](../../ref/models/fields/#django.db.models.Field.editable) and [`auto_now`](../../ref/models/fields/#django.db.models.DateField.auto_now) to a [`django.db.models.DateField`](../../ref/models/fields/#django.db.models.DateField) and it will ignore the [`editable`](../../ref/models/fields/#django.db.models.Field.editable) parameter ([`auto_now`](../../ref/models/fields/#django.db.models.DateField.auto_now) being set implies `editable=False`). No error is raised in this case.
> 
> This behavior simplifies the field classes, because they don't need to check for options that aren't necessary. They pass all the options to the parent class and then don't use them later on. It's up to you whether you want your fields to be more strict about the options they select, or to use the more permissive behavior of the current fields.

The `Field.__init__()` method takes the following parameters:

- [`verbose_name`](../../ref/models/fields/#django.db.models.Field.verbose_name)
- `name`
- [`primary_key`](../../ref/models/fields/#django.db.models.Field.primary_key)
- [`max_length`](../../ref/models/fields/#django.db.models.CharField.max_length)
- [`unique`](../../ref/models/fields/#django.db.models.Field.unique)
- [`blank`](../../ref/models/fields/#django.db.models.Field.blank)
- [`null`](../../ref/models/fields/#django.db.models.Field.null)
- [`db_index`](../../ref/models/fields/#django.db.models.Field.db_index)
- `rel`: Used for related fields (like [`ForeignKey`](../../ref/models/fields/#django.db.models.ForeignKey)). For advanced use only.
- [`default`](../../ref/models/fields/#django.db.models.Field.default)
- [`editable`](../../ref/models/fields/#django.db.models.Field.editable)
- `serialize`: If `False`, the field will not be serialized when the model is passed to Django's [serializers](../../topics/serialization/). Defaults to `True`.
- [`unique_for_date`](../../ref/models/fields/#django.db.models.Field.unique_for_date)
- [`unique_for_month`](../../ref/models/fields/#django.db.models.Field.unique_for_month)
- [`unique_for_year`](../../ref/models/fields/#django.db.models.Field.unique_for_year)
- [`choices`](../../ref/models/fields/#django.db.models.Field.choices)
- [`help_text`](../../ref/models/fields/#django.db.models.Field.help_text)
- [`db_column`](../../ref/models/fields/#django.db.models.Field.db_column)
- [`db_tablespace`](../../ref/models/fields/#django.db.models.Field.db_tablespace): Only for index creation, if the backend supports [tablespaces](../../topics/db/tablespaces/). You can usually ignore this option.
- [`auto_created`](../../ref/models/fields/#django.db.models.Field.auto_created): `True` if the field was automatically created, as for the [`OneToOneField`](../../ref/models/fields/#django.db.models.OneToOneField) used by model inheritance. For advanced use only.

All of the options without an explanation in the above list have the same meaning they do for normal Django fields. See the [field documentation](../../ref/models/fields/) for examples and details.

(The content continues with more sections about field deconstruction, useful methods, and other advanced topics. Would you like me to continue converting the rest of the document?)