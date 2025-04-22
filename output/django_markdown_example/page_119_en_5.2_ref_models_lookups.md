# Lookup API reference

This document has the API references of lookups, the Django API for building the `WHERE` clause of a database query. To learn how to *use* lookups, see [Making queries](https://docs.djangoproject.com/en/5.2/topics/db/queries/); to learn how to *create* new lookups, see [How to write custom lookups](https://docs.djangoproject.com/en/5.2/howto/custom-lookups/).

The lookup API has two components: a `RegisterLookupMixin` class that registers lookups, and the **Query Expression API**, a set of methods that a class has to implement to be registrable as a lookup.

Django has two base classes that follow the query expression API and from where all Django builtin lookups are derived:

- [`Lookup`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Lookup): to lookup a field (e.g. the `exact` of `field_name__exact`)
- [`Transform`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Transform): to transform a field

A lookup expression consists of three parts:

- Fields part (e.g. `Book.objects.filter(author__best_friends__first_name...);`)
- Transforms part (may be omitted) (e.g. `__lower__first3chars__reversed`)
- A lookup (e.g. `__icontains`) that, if omitted, defaults to `__exact`.

## Registration API

Django uses `RegisterLookupMixin` to give a class the interface to register lookups on itself or its instances. The two prominent examples are [`Field`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.Field), the base class of all model fields, and [`Transform`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Transform), the base class of all Django transforms.

### `class lookups.RegisterLookupMixin`

A mixin that implements the lookup API on a class.

#### `classmethod register_lookup(lookup, lookup_name=None)`

Registers a new lookup in the class or class instance. For example:

```python
DateField.register_lookup(YearExact)
User._meta.get_field("date_joined").register_lookup(MonthExact)
```

will register `YearExact` lookup on `DateField` and `MonthExact` lookup on the `User.date_joined` (you can use [Field Access API](https://docs.djangoproject.com/en/5.2/ref/models/meta/#model-meta-field-api) to retrieve a single field instance). It overrides a lookup that already exists with the same name. Lookups registered on field instances take precedence over the lookups registered on classes. `lookup_name` will be used for this lookup if provided, otherwise `lookup.lookup_name` will be used.

#### `get_lookup(lookup_name)`

Returns the [`Lookup`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Lookup) named `lookup_name` registered in the class or class instance depending on what calls it. The default implementation looks recursively on all parent classes and checks if any has a registered lookup named `lookup_name`, returning the first match. Instance lookups would override any class lookups with the same `lookup_name`.

#### `get_lookups()`

Returns a dictionary of each lookup name registered in the class or class instance mapped to the [`Lookup`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Lookup) class.

#### `get_transform(transform_name)`

Returns a [`Transform`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Transform) named `transform_name` registered in the class or class instance. The default implementation looks recursively on all parent classes to check if any has the registered transform named `transform_name`, returning the first match.

For a class to be a lookup, it must follow the [Query Expression API](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#the-query-expression-api). [`Lookup`](https://docs.djangoproject.com/en/5./ref2/models/lookups/#django.db.models.Lookup) and [`Transform`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Transform) naturally follow this API.

## The Query Expression API

The query expression API is a common set of methods that classes define to be usable in query expressions to translate themselves into SQL expressions. Direct field references, aggregates, and `Transform` are examples that follow this API. A class is said to follow the query expression API when it implements the following methods:

### `as_sql(compiler, connection)`

Generates the SQL fragment for the expression. Returns a tuple `(sql, params)`, where `sql` is the SQL string, and `params` is the list or tuple of query parameters. The `compiler` is an `SQLCompiler` object, which has a `compile()` method that can be used to compile other expressions. The `connection` is the connection used to execute the query.

Calling `expression.as_sql()` is usually incorrect - instead `compiler.compile(expression)` should be used. The `compiler.compile()` method will take care of calling vendor-specific methods of the expression.

Custom keyword arguments may be defined on this method if it’s likely that `as_vendorname()` methods or subclasses will need to supply data to override the generation of the SQL string. See [`Func.as_sql()`](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#django.db.models.Func.as_sql) for example usage.

### `as_vendorname(compiler, connection)`

Works like `as_sql()` method. When an expression is compiled by `compiler.compile()`, Django will first try to call `as_vendorname()`, where `vendorname` is the vendor name of the backend used for executing the query. The `vendorname` is one of `postgresql`, `oracle`, `sqlite`, or `mysql` for Django’s built-in backends.

### `get_lookup(lookup_name)`

Must return the lookup named `lookup_name`. For instance, by returning `self.output_field.get_lookup(lookup_name)`.

### `get_transform(transform_name)`

Must return the lookup named `transform_name`. For instance, by returning `self.output_field.get_transform(transform_name)`.

### `output_field`

Defines the type of class returned by the `get_lookup()` method. It must be a [`Field`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.Field) instance.

## `Transform` reference

### `class Transform`

A `Transform` is a generic class to implement field transformations. A prominent example is `__year` that transforms a `DateField` into a `IntegerField`.

The notation to use a `Transform` in a lookup expression is `<expression>__<transformation>` (e.g. `date__year`).

This class follows the [Query Expression API](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#the-query-expression-api), which implies that you can use `<expression>__<transform1>__<transform2>`. It’s a specialized [`Func()` expression](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#func-expressions) that only accepts one argument. It can also be used on the right-hand side of a filter or directly as an annotation.

#### `bilateral`

A boolean indicating whether this transformation should apply to both `lhs` and `rhs`. Bilateral transformations will be applied to `rhs` in the same order as they appear in the lookup expression. By default it is set to `False`. For example usage, see [How to write custom lookups](https://docs.djangoproject.com/en/5.2/howto/custom-lookups/).

#### `lhs`

The left-hand side - what is being transformed. It must follow the [Query Expression API](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#the-query-expression-api).

#### `lookup_name`

The name of the lookup, used for identifying it on parsing query expressions. It cannot contain the string `"__"`.

#### `output_field`

Defines the class this transformation outputs. It must be a [`Field`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.Field) instance. By default is the same as its `lhs.output_field`.

## `Lookup` reference

### `class Lookup`

A `Lookup` is a generic class to implement lookups. A lookup is a query expression with a left-hand side, [`lhs`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Lookup.lhs); a right-hand side, [`rhs`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Lookup.rhs); and a `lookup_name` that is used to produce a boolean comparison between `lhs` and `rhs` such as `lhs in rhs` or `lhs > rhs`.

The primary notation to use a lookup in an expression is `<lhs>__<lookup_name>=<rhs>`. Lookups can also be used directly in `QuerySet` filters:

```python
Book.objects.filter(LessThan(F("word_count"), 7500))
```

…or annotations:

```python
Book.objects.annotate(is_short_story=LessThan(F("word_count"), 7500))
```

#### `lhs`

The left-hand side - what is being looked up. The object typically follows the [Query Expression API](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#the-query-expression-api). It may also be a plain value.

#### `rhs`

The right-hand side - what `lhs` is being compared against. It can be a plain value, or something that compiles into SQL, typically an `F()` object or a `QuerySet`.

#### `lookup_name`

The name of this lookup, used to identify it on parsing query expressions. It cannot contain the string `"__"`.

#### `prepare_rhs`

Defaults to `True`. When [`rhs`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Lookup.rhs) is a plain value, [`prepare_rhs`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Lookup.prepare_rhs) determines whether it should be prepared for use as a parameter in a query. In order to do so, `lhs.output_field.get_prep_value()` is called if defined, or `rhs` is wrapped in [`Value()`](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#django.db.models.Value) otherwise.

#### `process_lhs(compiler, connection, lhs=None)`

Returns a tuple `(lhs_string, lhs_params)`, as returned by `compiler.compile(lhs)`. This method can be overridden to tune how the `lhs` is processed.

`compiler` is an `SQLCompiler` object, to be used like `compiler.compile(lhs)` for compiling `lhs`. The `connection` can be used for compiling vendor-specific SQL. If `lhs` is not `None`, use it as the processed `lhs` instead of `self.lhs`.

#### `process_rhs(compiler, connection)`

Behaves the same way as [`process_lhs()`](https://docs.djangoproject.com/en/5.2/ref/models/lookups/#django.db.models.Lookup.process_lhs), for the right-hand side.