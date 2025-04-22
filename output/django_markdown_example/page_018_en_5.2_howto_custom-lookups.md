# How to write custom lookups

Django offers a wide variety of [built-in lookups](../../ref/models/querysets/#field-lookups) for filtering (for example, `exact` and `icontains`). This documentation explains how to write custom lookups and how to alter the working of existing lookups. For the API references of lookups, see the [Lookup API reference](../../ref/models/lookups/).

## A lookup example

Let's start with a small custom lookup. We will write a custom lookup `ne` which works opposite to `exact`. `Author.objects.filter(name__ne='Jack')` will translate to the SQL:

```sql
"author"."name" <> 'Jack'
```

This SQL is backend independent, so we don't need to worry about different databases.

There are two steps to making this work. Firstly we need to implement the lookup, then we need to tell Django about it:

```python
from django.db.models import Lookup

class NotEqual(Lookup):
    lookup_name = "ne"
    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s <> %s" % (lhs, rhs), params
```

To register the `NotEqual` lookup we will need to call `register_lookup` on the field class we want the lookup to be available for. In this case, the lookup makes sense on all `Field` subclasses, so we register it with `Field` directly:

```python
from django.db.models import Field
Field.register_lookup(NotEqual)
```

Lookup registration can also be done using a decorator pattern:

```python
from django.db.models import Field

@Field.register_lookup
class NotEqualLookup(Lookup):
    ...
```

We can now use `foo__ne` for any field `foo`. You will need to ensure that this registration happens before you try to create any querysets using it. You could place the implementation in a `models.py` file, or register the lookup in the `ready()` method of an `AppConfig`.

## A transformer example

The custom lookup above is great, but in some cases you may want to be able to chain lookups together. For example, let's suppose we are building an application where we want to make use of the `abs()` operator. We have an `Experiment` model which records a start value, end value, and the change (start - end). We would like to find all experiments where the change was equal to a certain amount (`Experiment.objects.filter(change__abs=27)`), or where it did not exceed a certain amount (`Experiment.objects.filter(change__abs__lt=27)`).

> **Note**: This example is somewhat contrived, but it nicely demonstrates the range of functionality which is possible in a database backend independent manner, and without duplicating functionality already in Django.

We will start by writing an `AbsoluteValue` transformer. This will use the SQL function `ABS()` to transform the value before comparison:

```python
from django.db.models import Transform

class AbsoluteValue(Transform):
    lookup_name = "abs"
    function = "ABS"
```

Next, let's register it for `IntegerField`:

```python
from django.db.models import IntegerField
IntegerField.register_lookup(AbsoluteValue)
```

Now, the queryset `Experiment.objects.filter(change__abs=27)` will generate the following SQL:

```sql
SELECT ... WHERE ABS("experiments"."change") = 27
```

## Writing an efficient `abs__lt` lookup

When using the above written `abs` lookup, the SQL produced will not use indexes efficiently in some cases. In particular, when we use `change__abs__lt=27`, this is equivalent to `change__gt=-27` AND `change__lt=27`.

So we would like `Experiment.objects.filter(change__abs__lt=27)` to generate the following SQL:

```sql
SELECT .. WHERE "experiments"."change" < 27 AND "experiments"."change" > -27
```

The implementation is:

```python
from django.db.models import Lookup

class AbsoluteValueLessThan(Lookup):
    lookup_name = "lt"
    def as_sql(self, compiler, connection):
        lhs, lhs_params = compiler.compile(self.lhs.lhs)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params + lhs_params + rhs_params
        return "%s < %s AND %s > -%s" % (lhs, rhs, lhs, rhs), params

AbsoluteValue.register_lookup(AbsoluteValueLessThan)
```

> **Note**: In fact, most lookups with `__abs` could be implemented as range queries like this, and on most database backends it is likely to be more sensible to do so as you can make use of the indexes.

## A bilateral transformer example

In some cases you may want the transformation to be applied to both the left-hand side and the right-hand side. Let's examine case-insensitive transformations:

```python
from django.db.models import Transform

class UpperCase(Transform):
    lookup_name = "upper"
    function = "UPPER"
    bilateral = True
```

Register it for `CharField` and `TextField`:

```python
from django.db.models import CharField, TextField
CharField.register_lookup(UpperCase)
TextField.register_lookup(UpperCase)
```

Now, `Author.objects.filter(name__upper="doe")` will generate a case insensitive query:

```sql
SELECT ... WHERE UPPER("author"."name") = UPPER('doe')
```

## Writing alternative implementations for existing lookups

Sometimes different database vendors require different SQL for the same operation. For this example we will rewrite a custom implementation for MySQL for the NotEqual operator:

```python
class MySQLNotEqual(NotEqual):
    def as_mysql(self, compiler, connection, **extra_context):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s != %s" % (lhs, rhs), params

Field.register_lookup(MySQLNotEqual)
```

## How Django determines the lookups and transforms which are used

In some cases you may wish to dynamically change which `Transform` or `Lookup` is returned based on the name passed in:

```python
class CoordinatesField(Field):
    def get_lookup(self, lookup_name):
        if lookup_name.startswith("x"):
            try:
                dimension = int(lookup_name.removeprefix("x"))
            except ValueError:
                pass
            else:
                return get_coordinate_lookup(dimension)
        return super().get_lookup(lookup_name)
```

When filtering, the resolution follows these rules:
- `.filter(myfield__mylookup)` calls `myfield.get_lookup('mylookup')`
- `.filter(myfield__mytransform__mylookup)` calls `myfield.get_transform('mytransform')`, then `mytransform.get_lookup('mylookup')`
- `.filter(myfield__mytransform)` will first try `myfield.get_lookup('mytransform')`, then fall back to `myfield.get_transform('mytransform')` and `mytransform.get_lookup('exact')`