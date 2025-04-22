# QuerySet API Reference

This document describes the details of the `QuerySet` API. It builds on the material presented in the [model](https://docs.djangoproject.com/en/5.2/topics/db/models/) and [database query](https://docs.djangoproject.com/en/5.2/topics/db/queries/) guides, so you’ll probably want to read and understand those documents before reading this one.

Throughout this reference we’ll use the [example blog models](https://docs.djangoproject.com/en/5.2/topics/db/queries/#queryset-model-example) presented in the [database query guide](https://docs.djangoproject.com/en/5.2/topics/db/queries/).

## When QuerySets are evaluated

Internally, a `QuerySet` can be constructed, filtered, sliced, and generally passed around without actually hitting the database. No database activity actually occurs until you do something to evaluate the queryset.

You can evaluate a `QuerySet` in the following ways:

- **Iteration.** A `QuerySet` is iterable, and it executes its database query the first time you iterate over it. For example, this will print the headline of all entries in the database:

    ```python
    for e in Entry.objects.all():
        print(e.headline)
    ```

    Note: Don’t use this if all you want to do is determine if at least one result exists. It’s more efficient to use [`exists()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.exists).

- **Asynchronous iteration.** A `QuerySet` can also be iterated over using `async for`:

    ```python
    async for e in Entry.objects.all():
        results.append(e)
    ```

    Both synchronous and asynchronous iterators of QuerySets share the same underlying cache.

- **Slicing.** As explained in [Limiting QuerySets](https://docs.djangoproject.com/en/5.2/topics/db/queries/#limiting-querysets), a `QuerySet` can be sliced, using Python’s array-slicing syntax. Slicing an unevaluated `QuerySet` usually returns another unevaluated `QuerySet`, but Django will execute the database query if you use the “step” parameter of slice syntax, and will return a list. Slicing a `QuerySet` that has been evaluated also returns a list.

    Also note that even though slicing an unevaluated `QuerySet` returns another unevaluated `QuerySet`, modifying it further (e.g., adding more filters, or modifying ordering) is not allowed, since that does not translate well into SQL and it would not have a clear meaning either.

- **Pickling/Caching.** See the following section for details of what is involved when [pickling QuerySets](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#pickling-querysets). The important thing for the purposes of this section is that the results are read from the database.

- **repr().** A `QuerySet` is evaluated when you call `repr()` on it. This is for convenience in the Python interactive interpreter, so you can immediately see your results when using the API interactively.

- **len().** A `QuerySet` is evaluated when you call `len()` on it. This, as you might expect, returns the length of the result list.

    Note: If you only need to determine the number of records in the set (and don’t need the actual objects), it’s much more efficient to handle a count at the database level using SQL’s `SELECT COUNT(*)`. Django provides a [`count()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.count) method for precisely this reason.

- **list().** Force evaluation of a `QuerySet` by calling `list()` on it. For example:

    ```python
    entry_list = list(Entry.objects.all())
    ```

- **bool().** Testing a `QuerySet` in a boolean context, such as using `bool()`, `or`, `and` or an `if` statement, will cause the query to be executed. If there is at least one result, the `QuerySet` is `True`, otherwise `False`. For example:

    ```python
    if Entry.objects.filter(headline="Test"):
        print("There is at least one Entry with the headline Test")
    ```

    Note: If you only want to determine if at least one result exists (and don’t need the actual objects), it’s more efficient to use [`exists()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.exists).

## Pickling QuerySets

If you [pickle](https://docs.python.org/3/library/pickle.html#module-pickle) a `QuerySet`, this will force all the results to be loaded into memory prior to pickling. Pickling is usually used as a precursor to caching and when the cached queryset is reloaded, you want the results to already be present and ready for use (reading from the database can take some time, defeating the purpose of caching). This means that when you unpickle a `QuerySet`, it contains the results at the moment it was pickled, rather than the results that are currently in the database.

If you only want to pickle the necessary information to recreate the `QuerySet` from the database at a later time, pickle the `query` attribute of the `QuerySet`. You can then recreate the original `QuerySet` (without any results loaded) using some code like this:

```python
>>> import pickle
>>> query = pickle.loads(s)  # Assuming 's' is the pickled string.
>>> qs = MyModel.objects.all()
>>> qs.query = query  # Restore the original 'query'.
```

The `query` attribute is an opaque object. It represents the internals of the query construction and is not part of the public API. However, it is safe (and fully supported) to pickle and unpickle the attribute’s contents as described here.

### Restrictions on `QuerySet.values_list()`

If you recreate [`QuerySet.values_list()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.values_list) using the pickled `query` attribute, it will be converted to [`QuerySet.values()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.values):

```python
>>> import pickle
>>> qs = Blog.objects.values_list("id", "name")
>>> qs <QuerySet [(1, 'Beatles Blog')]>
>>> reloaded_qs = Blog.objects.all()
>>> reloaded_qs.query = pickle.loads(pickle.dumps(qs.query))
>>> reloaded_qs <QuerySet [{'id': 1, 'name': 'Beatles Blog'}]>
```

### You can’t share pickles between versions

Pickles of `QuerySet` objects are only valid for the version of Django that was used to generate them. If you generate a pickle using Django version N, there is no guarantee that pickle will be readable with Django version N+1. Pickles should not be used as part of a long-term archival strategy.

Since pickle compatibility errors can be difficult to diagnose, such as silently corrupted objects, a `RuntimeWarning` is raised when you try to unpickle a queryset in a Django version that is different than the one in which it was pickled.

## QuerySet API

Here’s the formal declaration of a `QuerySet`:

```python
class QuerySet(model=None, query=None, using=None, hints=None)
```

Usually when you’ll interact with a `QuerySet` you’ll use it by [chaining filters](https://docs.djangoproject.com/en/5.2/topics/db/queries/#chaining-filters). To make this work, most `QuerySet` methods return new querysets. These methods are covered in detail later in this section.

The `QuerySet` class has the following public attributes you can use for introspection:

- **ordered**: `True` if the `QuerySet` is ordered — i.e. has an [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by) clause or a default ordering on the model. `False` otherwise.

- **db**: The database that will be used if this query is executed now.

Note: The `query` parameter to `QuerySet` exists so that specialized query subclasses can reconstruct internal query state. The value of the parameter is an opaque representation of that query state and is not part of a public API.

## Methods that return new QuerySets

Django provides a range of `QuerySet` refinement methods that modify either the types of results returned by the `QuerySet` or the way its SQL query is executed.

Note: These methods do not run database queries, therefore they are **safe to** **run in asynchronous code**, and do not have separate asynchronous versions.

### `filter()`

```python
filter(*args, **kwargs)
```

Returns a new `QuerySet` containing objects that match the given lookup parameters.

The lookup parameters (`**kwargs`) should be in the format described in [Field lookups](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#field-lookups) below. Multiple parameters are joined via `AND` in the underlying SQL statement.

If you need to execute more complex queries (for example, queries with `OR` statements), you can use [`Q` objects](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.Q) (`*args`).

### `exclude()`

```python
exclude(*args, **kwargs)
```

Returns a new `QuerySet` containing objects that do *not* match the given lookup parameters.

The lookup parameters (`**kwargs`) should be in the format described in [Field lookups](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#field-lookups) below. Multiple parameters are joined via `AND` in the underlying SQL statement, and the whole thing is enclosed in a `NOT()`.

This example excludes all entries whose `pub_date` is later than 2005-1-3 AND whose `headline` is “Hello”:

```python
Entry.objects.exclude(pub_date__gt=datetime.date(2005, 1, 3), headline="Hello")
```

In SQL terms, that evaluates to:

```sql
SELECT... WHERE NOT (pub_date > '2005-1-3' AND headline = 'Hello')
```

This example excludes all entries whose `pub_date` is later than 2005-1-3 OR whose headline is “Hello”:

```python
Entry.objects.exclude(pub_date__gt=datetime.date(2005, 1, 3)).exclude(headline="Hello")
```

In SQL terms, that evaluates to:

```sql
SELECT... WHERE NOT pub_date > '2005-1-3' AND NOT headline = 'Hello'
```

Note the second example is more restrictive.

If you need to execute more complex queries (for example, queries with `OR` statements), you can use [`Q` objects](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.Q) (`*args`).

### `annotate()`

```python
annotate(*args, **kwargs)
```

Annotates each object in the `QuerySet` with the provided list of [query expressions](https://docs.djangoproject.com/en/5.2/ref/models/expressions/) or [`Q` objects](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.Q). Each object can be annotated with:

- a simple value, via `Value()`;
- a reference to a field on the model (or any related models), via `F()`;
- a boolean, via `Q()`; or
- a result from an aggregate expression (averages, sums, etc.) computed over the objects that are related to the objects in the `QuerySet`.

Each argument to `annotate()` is an annotation that will be added to each object in the `QuerySet` that is returned.

The aggregation functions that are provided by Django are described in [Aggregation Functions](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#aggregation-functions) below.

Annotations specified using keyword arguments will use the keyword as the alias for the annotation. Anonymous arguments will have an alias generated for them based upon the name of the aggregate function and the model field that is being aggregated. Only aggregate expressions that reference a single field can be anonymous arguments. Everything else must be a keyword argument.

For example, if you were manipulating a list of blogs, you may want to determine how many entries have been made in each blog:

```python
>>> from django.db.models import Count
>>> q = Blog.objects.annotate(Count("entry"))  # The name of the first blog
>>> q[0].name 'Blogasaurus'
# The number of entries on the first blog
>>> q[0].entry__count 42
```

The `Blog` model doesn’t define an `entry__count` attribute by itself, but by using a keyword argument to specify the aggregate function, you can control the name of the annotation:

```python
>>> q = Blog.objects.annotate(number_of_entries=Count("entry"))
# The number of entries on the first blog, using the name provided
>>> q[0].number_of_entries 42
```

For an in-depth discussion of aggregation, see [the topic guide on Aggregation](https://docs.djangoproject.com/en/5.2/topics/db/aggregation/).

### `alias()`

```python
alias(*args, **kwargs)
```

Same as [`annotate()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.annotate), but instead of annotating objects in the `QuerySet`, saves the expression for later reuse with other `QuerySet` methods. This is useful when the result of the expression itself is not needed but it is used for filtering, ordering, or as a part of a complex expression. Not selecting the unused value removes redundant work from the database which should result in better performance.

For example, if you want to find blogs with more than 5 entries, but are not interested in the exact number of entries, you could do this:

```python
>>> from django.db.models import Count
>>> blogs = Blog.objects.alias(entries=Count("entry")).filter(entries__gt=5)
```

`alias()` can be used in conjunction with [`annotate()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.annotate), [`exclude()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.exclude), [`filter()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.filter), [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by), and [`update()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.update). To use aliased expression with other methods (e.g. [`aggregate()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.aggregate)), you must promote it to an annotation:

```python
Blog.objects.alias(entries=Count("entry")).annotate(
    entries=F("entries"),
).aggregate(Sum("entries"))
```

[`filter()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.filter) and [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by) can take expressions directly, but expression construction and usage often does not happen in the same place (for example, `QuerySet` method creates expressions, for later use in views). `alias()` allows building complex expressions incrementally, possibly spanning multiple methods and modules, refer to the expression parts by their aliases and only use [`annotate()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.annotate) for the final result.

### `order_by()`

```python
order_by(*fields)
```

By default, results returned by a `QuerySet` are ordered by the ordering tuple given by the `ordering` option in the model’s `Meta`. You can override this on a per-`QuerySet` basis by using the `order_by` method.

Example:

```python
Entry.objects.filter(pub_date__year=2005).order_by("-pub_date", "headline")
```

The result above will be ordered by `pub_date` descending, then by `headline` ascending. The negative sign in front of `"-pub_date"` indicates *descending* order. Ascending order is implied. To order randomly, use `"?"`, like so:

```python
Entry.objects.order_by("?")
```

Note: `order_by('?')` queries may be expensive and slow, depending on the database backend you’re using.

To order by a field in a different model, use the same syntax as when you are querying across model relations. That is, the name of the field, followed by a double underscore (`__`), followed by the name of the field in the new model, and so on for as many models as you want to join. For example:

```python
Entry.objects.order_by("blog__name", "headline")
```

If you try to order by a field that is a relation to another model, Django will use the default ordering on the related model, or order by the related model’s primary key if there is no [`Meta.ordering`](https://docs.djangoproject.com/en/5.2/ref/models/options/#django.db.models.Options.ordering) specified. For example, since the `Blog` model has no default ordering specified:

```python
Entry.objects.order_by("blog")
```

…is identical to:

```python
Entry.objects.order_by("blog__id")
```

If `Blog` had `ordering = ['name']`, then the first queryset would be identical to:

```python
Entry.objects.order_by("blog__name")
```

You can also order by [query expressions](https://docs.djangoproject.com/en/5.2/ref/models/expressions/) by calling [`asc()`](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#django.db.models.Expression.asc) or [`desc()`](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#django.db.models.Expression.desc) on the expression:

```python
Entry.objects.order_by(Coalesce("summary", "headline").desc())
```

[`asc()`](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#django.db.models.Expression.asc) and [`desc()`](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#django.db.models.Expression.desc) have arguments (`nulls_first` and `nulls_last`) that control how null values are sorted.

Be cautious when ordering by fields in related models if you are also using [`distinct()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct). See the note in [`distinct()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct) for an explanation of how related model ordering can change the expected results.

Note: It is permissible to specify a multi-valued field to order the results by (for example, a [`ManyToManyField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ManyToManyField) field, or the reverse relation of a [`ForeignKey`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey) field).

Consider this case:

```python
class Event(Model):
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children",
    )
    date = models.DateField()
    Event.objects.order_by("children__date")
```

Here, there could potentially be multiple ordering data for each `Event`; each `Event` with multiple `children` will be returned multiple times into the new `QuerySet` that `order_by()` creates. In other words, using `order_by()` on the `QuerySet` could return more items than you were working on to begin with - which is probably neither expected nor useful.

Thus, take care when using multi-valued field to order the results. **If** you can be sure that there will only be one ordering piece of data for each of the items you’re ordering, this approach should not present problems. If not, make sure the results are what you expect.

There’s no way to specify whether ordering should be case sensitive. With respect to case-sensitivity, Django will order results however your database backend normally orders them.

You can order by a field converted to lowercase with [`Lower`](https://docs.djangoproject.com/en/5.2/ref/models/database-functions/#django.db.models.functions.Lower) which will achieve case-consistent ordering:

```python
Entry.objects.order_by(Lower("headline").desc())
```

If you don’t want any ordering to be applied to a query, not even the default ordering, call [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by) with no parameters.

You can tell if a query is ordered or not by checking the [`QuerySet.ordered`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.ordered) attribute, which will be `True` if the `QuerySet` has been ordered in any way.

Each `order_by()` call will clear any previous ordering. For example, this query will be ordered by `pub_date` and not `headline`:

```python
Entry.objects.order_by("headline").order_by("pub_date")
```

Warning: Ordering is not a free operation. Each field you add to the ordering incurs a cost to your database. Each foreign key you add will implicitly include all of its default orderings as well.

If a query doesn’t have an ordering specified, results are returned from the database in an unspecified order. A particular ordering is guaranteed only when ordering by a set of fields that uniquely identify each object in the results. For example, if a `name` field isn’t unique, ordering by it won’t guarantee objects with the same name always appear in the same order.

### `reverse()`

```python
reverse()
```

Use the `reverse()` method to reverse the order in which a queryset’s elements are returned. Calling `reverse()` a second time restores the ordering back to the normal direction.

To retrieve the “last” five items in a queryset, you could do this:

```python
my_queryset.reverse()[:5]
```

Note that this is not quite the same as slicing from the end of a sequence in Python. The above example will return the last item first, then the penultimate item and so on. If we had a Python sequence and looked at `seq[-5:]`, we would see the fifth-last item first. Django doesn’t support that mode of access (slicing from the end), because it’s not possible to do it efficiently in SQL.

Also, note that `reverse()` should generally only be called on a `QuerySet` which has a defined ordering (e.g., when querying against a model which defines a default ordering, or when using [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by)). If no such ordering is defined for a given `QuerySet`, calling `reverse()` on it has no real effect (the ordering was undefined prior to calling `reverse()`, and will remain undefined afterward).

### `distinct()`

```python
distinct(*fields)
```

Returns a new `QuerySet` that uses `SELECT DISTINCT` in its SQL query. This eliminates duplicate rows from the query results.

By default, a `QuerySet` will not eliminate duplicate rows. In practice, this is rarely a problem, because simple queries such as `Blog.objects.all()` don’t introduce the possibility of duplicate result rows. However, if your query spans multiple tables, it’s possible to get duplicate results when a `QuerySet` is evaluated. That’s when you’d use `distinct()`.

Note: Any fields used in an [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by) call are included in the SQL `SELECT` columns. This can sometimes lead to unexpected results when used in conjunction with `distinct()`. If you order by fields from a related model, those fields will be added to the selected columns and they may make otherwise duplicate rows appear to be distinct. Since the extra columns don’t appear in the returned results (they are only there to support ordering), it sometimes looks like non-distinct results are being returned.

Similarly, if you use a [`values()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.values) query to restrict the columns selected, the columns used in any [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by) (or default model ordering) will still be involved and may affect uniqueness of the results.

The moral here is that if you are using `distinct()` be careful about ordering by related models. Similarly, when using `distinct()` and [`values()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.values) together, be careful when ordering by fields not in the [`values()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.values) call.

On PostgreSQL only, you can pass positional arguments (`*fields`) in order to specify the names of fields to which the `DISTINCT` should apply. This translates to a `SELECT DISTINCT ON` SQL query. Here’s the difference. For a normal `distinct()` call, the database compares *each* field in each row when determining which rows are distinct. For a `distinct()` call with specified field names, the database will only compare the specified field names.

Note: When you specify field names, you *must* provide an [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by) in the `QuerySet`, and the fields in `order_by()` must start with the fields in `distinct()`, in the same order.

For example, `SELECT DISTINCT ON (a)` gives you the first row for each value in column `a`. If you don’t specify an order, you’ll get some arbitrary row.

Examples (those after the first will only work on PostgreSQL):

```python
>>> Author.objects.distinct()
[...]
>>> Entry.objects.order_by("pub_date").distinct("pub_date")
[...]
>>> Entry.objects.order_by("blog").distinct("blog")
[...]
>>> Entry.objects.order_by("author", "pub_date").distinct("author", "pub_date")
[...]
>>> Entry.objects.order_by("blog__name", "mod_date").distinct("blog__name", "mod_date")
[...]
>>> Entry.objects.order_by("author", "pub_date").distinct("author")
[...]
```

Note: Keep in mind that [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by) uses any default related model ordering that has been defined. You might have to explicitly order by the relation `_id` or referenced field to make sure the `DISTINCT ON` expressions match those at the beginning of the `ORDER BY` clause. For example, if the `Blog` model defined an [`ordering`](https://docs.djangoproject.com/en/5.2/ref/models/options/#django.db.models.Options.ordering) by `name`:

```python
Entry.objects.order_by("blog").distinct("blog")
```

…wouldn’t work because the query would be ordered by `blog__name` thus mismatching the `DISTINCT ON` expression. You’d have to explicitly order by the relation `_id` field (`blog_id` in this case) or the referenced one (`blog__pk`) to make sure both expressions match.

### `values()`

```python
values(*fields, **expressions)
```

Returns a `QuerySet` that returns dictionaries, rather than model instances, when used as an iterable.

Each of those dictionaries represents an object, with the keys corresponding to the attribute names of model objects.

This example compares the dictionaries of `values()` with the normal model objects:

```python
# This list contains a Blog object.
>>> Blog.objects.filter(name__startswith="Beatles")
<QuerySet [<Blog: Beatles Blog>]>
# This list contains a dictionary.
>>> Blog.objects.filter(name__startswith="Beatles").values()
<QuerySet [{'id': 1, 'name': 'Beatles Blog', 'tagline': 'All the latest Beatles news.'}]>
```

The `values()` method takes optional positional arguments, `*fields`, which specify field names to which the `SELECT` should be limited. If you specify the fields, each dictionary will contain only the field keys/values for the fields you specify. If you don’t specify the fields, each dictionary will contain a key and value for every field in the database table.

Example:

```python
>>> Blog.objects.values()
<QuerySet [{'id': 1, 'name': 'Beatles Blog', 'tagline': 'All the latest Beatles news.'}]>
>>> Blog.objects.values("id", "name")
<QuerySet [{'id': 1, 'name': 'Beatles Blog'}]>
```

The `values()` method also takes optional keyword arguments, `**expressions`, which are passed through to [`annotate()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.annotate):

```python
>>> from django.db.models.functions import Lower
>>> Blog.objects.values(lower_name=Lower("name"))
<QuerySet [{'lower_name': 'beatles blog'}]>
```

You can use built-in and [custom lookups](https://docs.djangoproject.com/en/5.2/howto/custom-lookups/) in ordering. For example:

```python
>>> from django.db.models import CharField
>>> from django.db.models.functions import Lower
>>> CharField.register_lookup(Lower)
>>> Blog.objects.values("name__lower")
<QuerySet [{'name__lower': 'beatles blog'}]>
```

An aggregate within a `values()` clause is applied before other arguments within the same `values()` clause. If you need to group by another value, add it to an earlier `values()` clause instead. For example:

```python
>>> from django.db.models import Count
>>> Blog.objects.values("entry__authors", entries=Count("entry"))
<QuerySet [{'entry__authors': 1, 'entries': 20}, {'entry__authors': 1, 'entries': 13}]>
>>> Blog.objects.values("entry__authors").annotate(entries=Count("entry"))
<QuerySet [{'entry__authors': 1, 'entries': 33}]>
```

A few subtleties that are worth mentioning:

- If you have a field called `foo` that is a [`ForeignKey`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey), the default `values()` call will return a dictionary key called `foo_id`, since this is the name of the hidden model attribute that stores the actual value (the `foo` attribute refers to the related model). When you are calling `values()` and passing in field names, you can pass in either `foo` or `foo_id` and you will get back the same thing (the dictionary key will match the field name you passed in).

    For example:

    ```python
    >>> Entry.objects.values()
    <QuerySet [{'blog_id': 1, 'headline': 'First Entry', ...}, ...]>
    >>> Entry.objects.values("blog")
    <QuerySet [{'blog': 1}, ...]>
    >>> Entry.objects.values("blog_id")
    <QuerySet [{'blog_id': 1}, ...]>
    ```

- When using `values()` together with [`distinct()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct), be aware that ordering can affect the results. See the note in [`distinct()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct) for details.

- If you use a `values()` clause after an [`extra()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.extra) call, any fields defined by a `select` argument in the [`extra()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.extra) must be explicitly included in the `values()` call. Any [`extra()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.extra) call made after a `values()` call will have its extra selected fields ignored.

- Calling [`only()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.only) and [`defer()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.defer) after `values()` doesn’t make sense, so doing so will raise a `TypeError`.

- Combining transforms and aggregates requires the use of two [`annotate()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.annotate) calls, either explicitly or as keyword arguments to [`values()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.values). As above, if the transform has been registered on the relevant field type the first [`annotate()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.annotate) can be omitted, thus the following examples are equivalent:

    ```python
    >>> from django.db.models import CharField, Count
    >>> from django.db.models.functions import Lower
    >>> CharField.register_lookup(Lower)
    >>> Blog.objects.values("entry__authors__name__lower").annotate(entries=Count("entry"))
    <QuerySet [{'entry__authors__name__lower': 'test author', 'entries': 33}]>
    >>> Blog.objects.values(entry__authors__name__lower=Lower("entry__authors__name")).annotate(
    ... entries=Count("entry")
    ... )
    <QuerySet [{'entry__authors__name__lower': 'test author', 'entries': 33}]>
    >>> Blog.objects.annotate(entry__authors__name__lower=Lower("entry__authors__name")).values(
    ... "entry__authors__name__lower"
    ... ).annotate(entries=Count("entry"))
    <QuerySet [{'entry__authors__name__lower': 'test author', 'entries': 33}]>
    ```

It is useful when you know you’re only going to need values from a small number of the available fields and you won’t need the functionality of a model instance object. It’s more efficient to select only the fields you need to use.

Finally, note that you can call `filter()`, `order_by()`, etc. after the `values()` call, that means that these two calls are identical:

```python
Blog.objects.values().order_by("id")
Blog.objects.order_by("id").values()
```

The people who made Django prefer to put all the SQL-affecting methods first, followed (optionally) by any output-affecting methods (such as `values()`), but it doesn’t really matter. This is your chance to really flaunt your individualism.

You can also refer to fields on related models with reverse relations through [`OneToOneField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.OneToOneField), [`ForeignKey`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey) and [`ManyToManyField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ManyToManyField) attributes:

```python
>>> Blog.objects.values("name", "entry__headline")
<QuerySet [{'name': 'My blog', 'entry__headline': 'An entry'},
 {'name': 'My blog', 'entry__headline': 'Another entry'}, ...]>
```

Warning: Because [`ManyToManyField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ManyToManyField) attributes and reverse relations can have multiple related rows, including these can have a multiplier effect on the size of your result set. This will be especially pronounced if you include multiple such fields in your `values()` query, in which case all possible combinations will be returned.

Special values for `JSONField` on SQLite

Due to the way the `JSON_EXTRACT` and `JSON_TYPE` SQL functions are implemented on SQLite, and lack of the `BOOLEAN` data type, `values()` will return `True`, `False`, and `None` instead of `"true"`, `"false"`, and `"null"` strings for [`JSONField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.JSONField) key transforms.

Changed in Django 5.2: The `SELECT` clause generated when using `values()` was updated to respect the order of the specified `*fields` and `**expressions`.

### `values_list()`

```python
values_list(*fields, flat=False, named=False)
```

This is similar to `values()` except that instead of returning dictionaries, it returns tuples when iterated over. Each tuple contains the value from the respective field or expression passed into the `values_list()` call — so the first item is the first field, etc. For example:

```python
>>> Entry.objects.values_list("id", "headline")
<QuerySet [(1, 'First entry'), ...]>
>>> from django.db.models.functions import Lower
>>> Entry.objects.values_list("id", Lower("headline"))
<QuerySet [(1, 'first entry'), ...]>
```

If you only pass in a single field, you can also pass in the `flat` parameter. If `True`, this will mean the returned results are single values, rather than 1-tuples. An example should make the difference clearer:

```python
>>> Entry.objects.values_list("id").order_by("id")
<QuerySet[(1,), (2,), (3,), ...]>
>>> Entry.objects.values_list("id", flat=True).order_by("id")
<QuerySet [1, 2, 3, ...]>
```

It is an error to pass in `flat` when there is more than one field.

You can pass `named=True` to get results as a [`namedtuple()`](https://docs.python.org/3/library/collections.html#collections.namedtuple):

```python
>>> Entry.objects.values_list("id", "headline", named=True)
<QuerySet [Row(id=1, headline='First entry'), ...]>
```

Using a named tuple may make use of the results more readable, at the expense of a small performance penalty for transforming the results into a named tuple.

If you don’t pass any values to `values_list()`, it will return all the fields in the model, in the order they were declared.

A common need is to get a specific field value of a certain model instance. To achieve that, use `values_list()` followed by a `get()` call:

```python
>>> Entry.objects.values_list("headline", flat=True).get(pk=1)
'First entry'
```

`values()` and `values_list()` are both intended as optimizations for a specific use case: retrieving a subset of data without the overhead of creating a model instance. This metaphor falls apart when dealing with many-to-many and other multivalued relations (such as the one-to-many relation of a reverse foreign key) because the “one row, one object” assumption doesn’t hold.

For example, notice the behavior when querying across a [`ManyToManyField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ManyToManyField):

```python
>>> Author.objects.values_list("name", "entry__headline")
<QuerySet [('Noam Chomsky', 'Impressions of Gaza'),
 ('George Orwell', 'Why Socialists Do Not Believe in Fun'),
 ('George Orwell', 'In Defence of English Cooking'),
 ('Don Quixote', None)]>
```

Authors with multiple entries appear multiple times and authors without any entries have `None` for the entry headline.

Similarly, when querying a reverse foreign key, `None` appears for entries not having any author:

```python
>>> Entry.objects.values_list("authors")
<QuerySet [('Noam Chomsky',), ('George Orwell',), (None,)]>
```

Special values for `JSONField` on SQLite

Due to the way the `JSON_EXTRACT` and `JSON_TYPE` SQL functions are implemented on SQLite, and lack of the `BOOLEAN` data type, `values_list()` will return `True`, `False`, and `None` instead of `"true"`, `"false"`, and `"null"` strings for [`JSONField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.JSONField) key transforms.

Changed in Django 5.2: The `SELECT` clause generated when using `values_list()` was updated to respect the order of the specified `*fields`.

### `dates()`

```python
dates(field, kind, order='ASC')
```

Returns a `QuerySet` that evaluates to a list of [`datetime.date`](https://docs.python.org/3/library/datetime.html#datetime.date) objects representing all available dates of a particular kind within the contents of the `QuerySet`.

`field` should be the name of a `DateField` of your model. `kind` should be either `"year"`, `"month"`, `"week"`, or `"day"`. Each [`datetime.date`](https://docs.python.org/3/library/datetime.html#datetime.date) object in the result list is “truncated” to the given `type`.

- `"year"` returns a list of all distinct year values for the field.
- `"month"` returns a list of all distinct year/month values for the field.
- `"week"` returns a list of all distinct year/week values for the field. All dates will be a Monday.
- `"day"` returns a list of all distinct year/month/day values for the field.

`order`, which defaults to `'ASC'`, should be either `'ASC'` or `'DESC'`. This specifies how to order the results.

Examples:

```python
>>> Entry.objects.dates("pub_date", "year")
[datetime.date(2005, 1, 1)]
>>> Entry.objects.dates("pub_date", "month")
[datetime.date(2005, 2, 1), datetime.date(2005, 3, 1)]
>>> Entry.objects.dates("pub_date", "week")
[datetime.date(2005, 2, 14), datetime.date(2005, 3, 14)]
>>> Entry.objects.dates("pub_date", "day")
[datetime.date(2005, 2, 20), datetime.date(2005, 3, 20)]
>>> Entry.objects.dates("pub_date", "day", order="DESC")
[datetime.date(2005, 3, 20), datetime.date(2005, 2, 20)]
>>> Entry.objects.filter(headline__contains="Lennon").dates("pub_date", "day")
[datetime.date(2005, 3, 20)]
```

### `datetimes()`

```python
datetimes(field_name, kind, order='ASC', tzinfo=None)
```

Returns a `QuerySet` that evaluates to a list of [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) objects representing all available dates of a particular kind within the contents of the `QuerySet`.

`field_name` should be the name of a `DateTimeField` of your model.

`kind` should be either `"year"`, `"month"`, `"week"`, `"day"`, `"hour"`, `"minute"`, or `"second"`. Each [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) object in the result list is “truncated” to the given `type`.

`order`, which defaults to `'ASC'`, should be either `'ASC'` or `'DESC'`. This specifies how to order the results.

`tzinfo` defines the time zone to which datetimes are converted prior to truncation. Indeed, a given datetime has different representations depending on the time zone in use. This parameter must be a [`datetime.tzinfo`](https://docs.python.org/3/library/datetime.html#datetime.tzinfo) object. If it’s `None`, Django uses the [current time zone](https://docs.djangoproject.com/en/5.2/topics/i18n/timezones/#default-current-time-zone). It has no effect when [`USE_TZ`](https://docs.djangoproject.com/en/5.2/settings/#std-setting-USE_TZ) is `False`.

Note: This function performs time zone conversions directly in the database. As a consequence, your database must be able to interpret the value of `tzinfo.tzname(None)`. This translates into the following requirements:

- SQLite: no requirements. Conversions are performed in Python.
- PostgreSQL: no requirements (see [Time Zones](https://www.postgresql.org/docs/current/datatype-datetime.html#DATATYPE-TIMEZONES)).
- Oracle: no requirements (see [Choosing a Time Zone File](https://docs.oracle.com/en/database/oracle/oracle-database/18/nlspg/datetime-data-types-and-time-zone-support.html#GUID-805AB986-DE12-4FEA-AF56-5AABCD2132DF)).
- MySQL: load the time zone tables with [mysql_tzinfo_to_sql](https://dev.mysql.com/doc/refman/en/mysql-tzinfo-to-sql.html).

### `none()`

```python
none()
```

Calling `none()` will create a queryset that never returns any objects and no query will be executed when accessing the results. A `qs.none()` queryset is an instance of `EmptyQuerySet`.

Examples:

```python
>>> Entry.objects.none()
<QuerySet []>
>>> from django.db.models.query import EmptyQuerySet
>>> isinstance(Entry.objects.none(), EmptyQuerySet)
True
```

### `all()`

```python
all()
```

Returns a *copy* of the current `QuerySet` (or `QuerySet` subclass). This can be useful in situations where you might want to pass in either a model manager or a `QuerySet` and do further filtering on the result. After calling `all()` on either object, you’ll definitely have a `QuerySet` to work with.

When a `QuerySet` is [evaluated](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#when-querysets-are-evaluated), it typically caches its results. If the data in the database might have changed since a `QuerySet` was evaluated, you can get updated results for the same query by calling `all()` on a previously evaluated `QuerySet`.

### `union()`

```python
union(*other_qs, all=False)
```

Uses SQL’s `UNION` operator to combine the results of two or more `QuerySet`s. For example:

```python
>>> qs1.union(qs2, qs3)
```

The `UNION` operator selects only distinct values by default. To allow duplicate values, use the `all=True` argument.

`union()`, `intersection()`, and `difference()` return model instances of the type of the first `QuerySet` even if the arguments are `QuerySet`s of other models. Passing different models works as long as the `SELECT` list is the same in all `QuerySet`s (at least the types, the names don’t matter as long as the types are in the same order). In such cases, you must use the column names from the first `QuerySet` in `QuerySet` methods applied to the resulting `QuerySet`. For example:

```python
>>> qs1 = Author.objects.values_list("name")
>>> qs2 = Entry.objects.values_list("headline")
>>> qs1.union(qs2).order_by("name")
```

In addition, only `LIMIT`, `OFFSET`, `COUNT(*)`, `ORDER BY`, and specifying columns (i.e. slicing, [`count()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.count), [`exists()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.exists), [`order_by()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by), and [`values()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.values)/[`values_list()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.values_list)) are allowed on the resulting `QuerySet`. Further, databases place restrictions on what operations are allowed in the combined queries. For example, most databases don’t allow `LIMIT` or `OFFSET` in the combined queries.

### `intersection()`

```python
intersection(*other_qs)
```

Uses SQL’s `INTERSECT` operator to return the shared elements of two or more `QuerySet`s. For example:

```python
>>> qs1.intersection(qs2, qs3)
```

See [`union()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.union) for some restrictions.

### `difference()`

```python
difference(*other_qs)
```

Uses SQL’s `EXCEPT` operator to keep only elements present in the `QuerySet` but not in some other `QuerySet`s. For example:

```python
>>> qs1.difference(qs2, qs3)
```

See [`union()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.union) for some restrictions.

### `select_related()`

```python
select_related(*fields)
```

Returns a `QuerySet` that will “follow” foreign-key relationships, selecting additional related-object data when it executes its query. This is a performance booster which results in a single more complex query but means later use of foreign-key relationships won’t require database queries.

The following examples illustrate the difference between plain lookups and `select_related()` lookups. Here’s standard lookup:

```python
# Hits the database.
e = Entry.objects.get(id=5)
# Hits the database again to get the related Blog object.
b = e.blog
```

And here’s `select_related` lookup:

```python
# Hits the database.
e = Entry.objects.select_related("blog").get(id=5)
# Doesn't hit the database, because e.blog has been prepopulated
# in the previous query.
b = e.blog
```

You can use `select_related()` with any queryset of objects:

```python
from django.utils import timezone
# Find all the blogs with entries scheduled to be published in the future.
blogs = set()
for e in Entry.objects.filter(pub_date__gt=timezone.now()).select_related("blog"):
    # Without select_related(), this would make a database query for each
    # loop iteration in order to fetch the related blog for each entry.
    blogs.add(e.blog)
```

The order of `filter()` and `select_related()` chaining isn’t important. These querysets are equivalent:

```python
Entry.objects.filter(pub_date__gt=timezone.now()).select_related("blog")
Entry.objects.select_related("blog").filter(pub_date__gt=timezone.now())
```

You can follow foreign keys in a similar way to querying them. If you have the following models:

```python
from django.db import models
class City(models.Model):
    # ...
    pass
class Person(models.Model):
    # ...
    hometown = models.ForeignKey(
        City, on_delete=models.SET_NULL, blank=True, null=True,
    )
class Book(models.Model):
    # ...
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
```

… then a call to `Book.objects.select_related('author__hometown').get(id=4)` will cache the related `Person` *and* the related `City`:

```python
# Hits the database with joins to the author and hometown tables.
b = Book.objects.select_related("author__hometown").get(id=4)
p = b.author
# Doesn't hit the database.
c = p.hometown
# Doesn't hit the database.
# Without select_related()...
b = Book.objects.get(id=4)
# Hits the database.
p = b.author
# Hits the database.
c = p.hometown
# Hits the database.
```

You can refer to any [`ForeignKey`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey) or [`OneToOneField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.OneToOneField) relation in the list of fields passed to `select_related()`.

You can also refer to the reverse direction of a [`OneToOneField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.OneToOneField) in the list of fields passed to `select_related` — that is, you can traverse a [`OneToOneField`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.OneToOneField) back to the object on which the field is defined. Instead of specifying the field name, use the [`related_name`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey.related_name) for the field on the related object.

There may be some situations where you wish to call `select_related()` with a lot of related objects, or where you don’t know all of the relations. In these cases it is possible to call `select_related()` with no arguments. This will follow all non-null foreign keys it can find - nullable foreign keys must be specified. This is not recommended in most cases as it is likely to make the underlying query more complex, and return more data, than is actually needed.

If you need to clear the list of related fields added by past calls of `select_related` on a `QuerySet`, you can pass `None` as a parameter:

```python
>>> without_relations = queryset.select_related(None)
```

Chaining `select_related` calls works in a similar way to other methods - that is that `select_related('foo', 'bar')` is equivalent to `select_related('foo').select_related('bar')`.

### `prefetch_related()`

```python
prefetch_related(*lookups)
```

Returns a `QuerySet` that will automatically retrieve, in a single batch, related objects for each of the specified lookups.

This has a similar purpose to `select_related`, in that both are designed to stop the deluge of database queries that is caused by accessing related objects, but the strategy is quite different.

`select_related` works by creating an SQL join and including the fields of the related object in the `SELECT` statement. For this reason, `select_related` gets the related objects in the same database query. However, to avoid the much larger result set that would result from joining across a ‘many’ relationship, `select_related` is limited to single-valued relationships - foreign key and one-to-one.

`prefetch_related`, on the other hand, does a separate lookup for each relationship, and does the ‘joining’ in Python. This allows it to prefetch many-to-many, many-to-one, and [`GenericRelation`](https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericRelation) objects which cannot be done using `select_related`, in addition to the foreign key and one-to-one relationships that are supported by `select_related`. It also supports prefetching of [`GenericForeignKey`](https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey), however, the queryset for each `ContentType` must be provided in the `querysets` parameter of [`GenericPrefetch`](https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/#django.contrib.contenttypes.prefetch.GenericPrefetch).

For example, suppose you have these models:

```python
from django.db import models
class Topping(models.Model):
    name = models.CharField(max_length=30)
class Pizza(models.Model):
    name = models.CharField(max_length=50)
    toppings = models.ManyToManyField(Topping)
    def __str__(self):
        return "%s (%s)" % (
            self.name, ", ".join(topping.name for topping in self.toppings.all()),
        )
```

and run:

```python
>>> Pizza.objects.all()
["Hawaiian (ham, pineapple)", "Seafood (prawns, smoked salmon)..."]
```

The problem with this is that every time `Pizza.__str__()` asks for `self.toppings.all()` it has to query the database, so `Pizza.objects.all()` will run a query on the Toppings table for **every** item in the Pizza `QuerySet`.

We can reduce to just two queries using `prefetch_related`:

```python
>>> Pizza.objects.prefetch_related("toppings")
```

This implies a `self.toppings.all()` for each `Pizza`; now each time `self.toppings.all()` is called, instead of having to go to the database for the items, it will find them in a prefetched `QuerySet` cache that was populated in a single query.

That is, all the relevant toppings will have been fetched in a single query, and used to make `QuerySet` instances that have a pre-filled cache of the relevant results; these are then used in the `self.toppings.all()` calls.

The additional queries in `prefetch_related()` are executed after the `QuerySet` has begun to be evaluated and the primary query has been executed.

Note that there is no mechanism to prevent another database query from altering the items in between the execution of the primary query and the additional queries, which could produce an inconsistent result. For example, if a `Pizza` is deleted after the primary query has executed, its toppings will not be returned in the additional query, and it will seem like the pizza has no toppings:

```python
>>> Pizza.objects.prefetch_related("toppings")
# "Hawaiian" Pizza was deleted in another shell.
<QuerySet [<Pizza: Hawaiian ()>, <Pizza: Seafood (prawns, smoked salmon)>]>
```

If you have an iterable of model instances, you can prefetch related attributes on those instances using the [`prefetch_related_objects()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.prefetch_related_objects) function.

Note that the result cache of the primary `QuerySet` and all specified related objects will then be fully loaded into memory. This changes the typical behavior of a `QuerySet`, which normally tries to avoid loading all objects into memory before they are needed, even after a query has been executed in the database.

Note: Remember that, as always with `QuerySet` objects, any subsequent chained methods which imply a different database query will ignore previously cached results, and retrieve data using a fresh database query. So, if you write the following:

```python
>>> pizzas = Pizza.objects.prefetch_related("toppings")
>>> [list(pizza.toppings.filter(spicy=True)) for pizza in pizzas]
```

…then the fact that `pizza.toppings.all()` has been prefetched will not help you. The `prefetch_related('toppings')` implied `pizza.toppings.all()`, but `pizza.toppings.filter()` is a new and different query. The prefetched cache can’t help here; in fact it hurts performance, since you have done a database query that you haven’t used. So use this feature with caution!

Also, if you call the database-altering methods [`add()`](https://docs.djangoproject.com/en/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.add), [`create()`](https://docs.djangoproject.com/en/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.create), [`remove()`](https://docs.djangoproject.com/en/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.remove), [`clear()`](https://docs.djangoproject.com/en/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.clear) or [`set()`](https://docs.djangoproject.com/en/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.set), on [`related` managers](https://docs.djangoproject.com/en/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager), any prefetched cache for the relation will be cleared.

You can also use the normal join syntax to do related fields of related fields. Suppose we have an additional model to the example above:

```python
class Restaurant(models.Model):
    pizzas = models.ManyToManyField(Pizza, related_name="restaurants")
    best_pizza = models.ForeignKey(
        Pizza, related_name="championed_by", on_delete=models.CASCADE
    )
```

The following are all legal:

```python
>>> Restaurant.objects.prefetch_related("pizzas__toppings")
```

This will prefetch all pizzas belonging to restaurants, and all toppings belonging to those pizzas. This will result in a total of 3 database queries - one for the restaurants, one for the pizzas, and one for the toppings.

```python
>>> Restaurant.objects.prefetch_related("best_pizza__toppings")
```

This will fetch the best pizza and all the toppings for the best pizza for each restaurant. This will be done in 3 database queries - one for the restaurants, one for the ‘best pizzas’, and one for the toppings.

The `best_pizza` relationship could also be fetched using `select_related` to reduce the query count to 2:

```python
>>> Restaurant.objects.select_related("best_pizza").prefetch_related("best_pizza__toppings")
```

Since the prefetch is executed after the main query (which includes the joins needed by `select_related`), it is able to detect that the `best_pizza` objects have already been fetched, and it will skip fetching them again.

Chaining `prefetch_related` calls will accumulate the lookups that are prefetched. To clear any `prefetch_related` behavior, pass `None` as a parameter:

```python
>>> non_prefetched = qs.prefetch_related(None)
```

One difference to note when using `prefetch_related` is that objects created by a query can be shared between the different objects that they are related to i.e. a single Python model instance can appear at more than one point in the tree of objects that are returned. This will normally happen with foreign key relationships. Typically this behavior will not be a problem, and will in fact save both memory and CPU time.

While `prefetch_related` supports prefetching `GenericForeignKey` relationships, the number of queries will depend on the data. Since a `GenericForeignKey` can reference data in multiple tables, one query per table referenced is needed, rather than one query for all the items. There could be additional queries on the `ContentType` table if the relevant rows have not already been fetched.

`prefetch_related` in most cases will be implemented using an SQL query that uses the ‘IN’ operator. This means that for a large `QuerySet` a large ‘IN’ clause could be generated, which, depending on the database, might have performance problems of its own when it comes to parsing or executing the SQL query. Always profile for your use case!

If you use `iterator()` to run the query, `prefetch_related()` calls will only be observed if a value for `chunk_size` is provided.

You can use the [`Prefetch`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.Prefetch) object to further control the prefetch operation.

In its simplest form `Prefetch` is equivalent to the traditional string based lookups:

```python
>>> from django.db.models import Prefetch
>>> Restaurant.objects.prefetch_related(Prefetch("pizzas__toppings"))
```

You can provide a custom queryset with the optional `queryset` argument. This can be used to change the default ordering of the queryset:

```python
>>> Restaurant.objects.prefetch_related(
... Prefetch("pizzas__toppings", queryset=Toppings.objects.order_by("name"))
... )
```

Or to call [`select_related()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.select_related) when applicable to reduce the number of queries even further:

```python
>>> Pizza.objects.prefetch_related(
... Prefetch("restaurants", queryset=Restaurant.objects.select_related("best_pizza"))
... )
```

You can also assign the prefetched result to a custom attribute with the optional `to_attr` argument. The result will be stored directly in a list.

This allows prefetching the same relation multiple times with a different `QuerySet`; for instance:

```python
>>> vegetarian_pizzas = Pizza.objects.filter(vegetarian=True)
>>> Restaurant.objects.prefetch_related(
... Prefetch("pizzas", to_attr="menu"),
... Prefetch("pizzas", queryset=vegetarian_pizzas, to_attr="vegetarian_menu"),
... )
```

Lookups created with custom `to_attr` can still be traversed as usual by other lookups:

```python
>>> vegetarian_pizzas = Pizza.objects.filter(vegetarian=True)
>>> Restaurant.objects.prefetch_related(
... Prefetch("pizzas", queryset=vegetarian_pizzas, to_attr="vegetarian_menu"),
... "vegetarian_menu__toppings",
... )
```

Using `to_attr` is recommended when filtering down the prefetch result as it is less ambiguous than storing a filtered result in the related manager’s cache:

```python
>>> queryset = Pizza.objects.filter(vegetarian=True)
>>> # Recommended:
>>> restaurants = Restaurant.objects.prefetch_related(
... Prefetch("pizzas", queryset=queryset, to_attr="vegetarian_pizzas")
... )
>>> vegetarian_pizzas = restaurants[0].vegetarian_pizzas
>>>
>>> # Not recommended:
>>> restaurants = Restaurant.objects.prefetch_related(
... Prefetch("pizzas", queryset=queryset),
... )
>>> vegetarian_pizzas = restaurants[0].pizzas.all()
```

Custom prefetching also works with single related relations like forward `ForeignKey` or `OneToOneField`. Generally you’ll want to use [`select_related()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.select_related) for these relations, but there are a number of cases where prefetching with a custom `QuerySet` is useful:

- You want to use a `QuerySet` that performs further prefetching on related models.
- You want to prefetch only a subset of the related objects.
- You want to use performance optimization techniques like [deferred fields](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#django.db.models.query.QuerySet.defer):

    ```python
    >>> queryset = Pizza.objects.only("name")
    >>> restaurants = Restaurant.objects.prefetch_related(
    ... Prefetch("best_pizza", queryset=queryset)
    ... )
    ```

When using multiple databases, `Prefetch` will respect your choice of database. If the inner query does not specify a database, it will use the database selected by the outer query. All of the following are valid:

```python
>>> # Both inner and outer queries will use the 'replica' database
>>> Restaurant.objects.prefetch_related("pizzas__toppings").using("replica")
>>> Restaurant.objects.prefetch_related(
... Prefetch("pizzas__toppings"),
... ).using("replica")
>>>
>>> # Inner will use the 'replica' database; outer will use 'default' database
>>> Restaurant.objects.prefetch_related(
... Prefetch("pizzas__toppings", queryset=Toppings.objects.using("replica")),
... )
>>>
>>> # Inner will use 'replica' database; outer will use 'cold-storage' database
>>> Restaurant.objects.prefetch_related(
... Prefetch("pizzas__toppings", queryset=Toppings.objects.using("replica")),
... ).using("cold-storage")
```

Note: The ordering of lookups matters.

Take the following examples:

```python
>>> prefetch_related("pizzas__toppings", "pizzas")
```

This works even though it’s unordered because `'pizzas__toppings'` already contains all the needed information, therefore the second argument `'pizzas'` is actually redundant.

```python
>>> prefetch_related("pizzas__toppings", Prefetch("pizzas", queryset=Pizza.objects.all()))
```

This will raise a `ValueError` because of the attempt to redefine the queryset of a previously seen lookup. Note that an implicit queryset was created to traverse `'pizzas'` as part of the `'pizzas__toppings'` lookup.

```python
>>> prefetch_related("pizza_list__toppings", Prefetch("pizzas", to_attr="pizza_list"))
```

This will trigger an `AttributeError` because `'pizza_list'` doesn’t exist yet when `'pizza_list__toppings'` is being processed.

This consideration is not limited to the use of `Prefetch` objects. Some advanced techniques may require that the lookups be performed in a specific order to avoid creating extra queries; therefore it’s recommended to always carefully order `prefetch_related` arguments.

### `extra()`

```python
extra(select=None, where=None, params=None, tables=None, order_by=None, select_params=None)
```

Sometimes, the Django query

---

# Using `prefetch_related`

When using `prefetch_related`, objects created by a query can be shared between the different objects that they are related to. This means a single Python model instance can appear at more than one point in the tree of objects that are returned. This will normally happen with foreign key relationships. Typically, this behavior will not be a problem and will, in fact, save both memory and CPU time.

While `prefetch_related` supports prefetching `GenericForeignKey` relationships, the number of queries will depend on the data. Since a `GenericForeignKey` can reference data in multiple tables, one query per table referenced is needed, rather than one query for all the items. There could be additional queries on the `ContentType` table if the relevant rows have not already been fetched.

In most cases, `prefetch_related` will be implemented using an SQL query that uses the ‘IN’ operator. This means that for a large `QuerySet`, a large ‘IN’ clause could be generated, which, depending on the database, might have performance problems of its own when it comes to parsing or executing the SQL query. Always profile for your use case!

If you use `iterator()` to run the query, `prefetch_related()` calls will only be observed if a value for `chunk_size` is provided.

You can use the `Prefetch` object to further control the prefetch operation.

In its simplest form, `Prefetch` is equivalent to the traditional string-based lookups:

```python
from django.db.models import Prefetch
Restaurant.objects.prefetch_related(Prefetch("pizzas__toppings"))
```

You can provide a custom queryset with the optional `queryset` argument. This can be used to change the default ordering of the queryset:

```python
Restaurant.objects.prefetch_related(
    ...
    Prefetch("pizzas__toppings", queryset=Toppings.objects.order_by("name"))
    ...
)
```

Or to call `select_related()` when applicable to reduce the number of queries even further:

```python
Pizza.objects.prefetch_related(
    ...
    Prefetch("restaurants", queryset=Restaurant.objects.select_related("best_pizza"))
    ...
)
```

You can also assign the prefetched result to a custom attribute with the optional `to_attr` argument. The result will be stored directly in a list.

This allows prefetching the same relation multiple times with a different `QuerySet`; for instance:

```python
vegetarian_pizzas = Pizza.objects.filter(vegetarian=True)
Restaurant.objects.prefetch_related(
    ...
    Prefetch("pizzas", to_attr="menu"),
    ...
    Prefetch("pizzas", queryset=vegetarian_pizzas, to_attr="vegetarian_menu"),
    ...
)
```

Lookups created with custom `to_attr` can still be traversed as usual by other lookups:

```python
vegetarian_pizzas = Pizza.objects.filter(vegetarian=True)
Restaurant.objects.prefetch_related(
    ...
    Prefetch("pizzas", queryset=vegetarian_pizzas, to_attr="vegetarian_menu"),
    ...
    "vegetarian_menu__toppings",
    ...
)
```

Using `to_attr` is recommended when filtering down the prefetch result as it is less ambiguous than storing a filtered result in the related manager’s cache:

```python
queryset = Pizza.objects.filter(vegetarian=True)
# Recommended:
restaurants = Restaurant.objects.prefetch_related(
    ...
    Prefetch("pizzas", queryset=queryset, to_attr="vegetarian_pizzas")
    ...
)
vegetarian_pizzas = restaurants[0].vegetarian_pizzas
# Not recommended:
restaurants = Restaurant.objects.prefetch_related(
    ...
    Prefetch("pizzas", queryset=queryset),
    ...
)
vegetarian_pizzas = restaurants[0].pizzas.all()
```

Custom prefetching also works with single related relations like forward `ForeignKey` or `OneToOneField`. Generally, you’ll want to use `select_related()` for these relations, but there are a number of cases where prefetching with a custom `QuerySet` is useful:

- You want to use a `QuerySet` that performs further prefetching on related models.
- You want to prefetch only a subset of the related objects.
- You want to use performance optimization techniques like `deferred fields`:

```python
queryset = Pizza.objects.only("name")
restaurants = Restaurant.objects.prefetch_related(
    ...
    Prefetch("best_pizza", queryset=queryset)
    ...
)
```

When using multiple databases, `Prefetch` will respect your choice of database. If the inner query does not specify a database, it will use the database selected by the outer query. All of the following are valid:

```python
# Both inner and outer queries will use the 'replica' database
Restaurant.objects.prefetch_related("pizzas__toppings").using("replica")
Restaurant.objects.prefetch_related(
    ...
    Prefetch("pizzas__toppings"),
    ...
).using("replica")

# Inner will use the 'replica' database; outer will use 'default' database
Restaurant.objects.prefetch_related(
    ...
    Prefetch("pizzas__toppings", queryset=Toppings.objects.using("replica")),
    ...
)

# Inner will use 'replica' database; outer will use 'cold-storage' database
Restaurant.objects.prefetch_related(
    ...
    Prefetch("pizzas__toppings", queryset=Toppings.objects.using("replica")),
    ...
).using("cold-storage")
```

**Note**

The ordering of lookups matters.

Take the following examples:

```python
prefetch_related("pizzas__toppings", "pizzas")
```

This works even though it’s unordered because `'pizzas__toppings'` already contains all the needed information, therefore the second argument `'pizzas'` is actually redundant.

```python
prefetch_related("pizzas__toppings", Prefetch("pizzas", queryset=Pizza.objects.all()))
```

This will raise a `ValueError` because of the attempt to redefine the queryset of a previously seen lookup. Note that an implicit queryset was created to traverse `'pizzas'` as part of the `'pizzas__toppings'` lookup.

```python
prefetch_related("pizza_list__toppings", Prefetch("pizzas", to_attr="pizza_list"))
```

This will trigger an `AttributeError` because `'pizza_list'` doesn’t exist yet when `'pizza_list__toppings'` is being processed.

This consideration is not limited to the use of `Prefetch` objects. Some advanced techniques may require that the lookups be performed in a specific order to avoid creating extra queries; therefore, it’s recommended to always carefully order `prefetch_related` arguments.

# `extra()`

Sometimes, the Django query syntax by itself can’t easily express a complex `WHERE` clause. For these edge cases, Django provides the `extra()` `QuerySet` modifier — a hook for injecting specific clauses into the SQL generated by a `QuerySet`.

**Use this method as a last resort**

This is an old API that we aim to deprecate at some point in the future. Use it only if you cannot express your query using other queryset methods. If you do need to use it, please [file a ticket](https://code.djangoproject.com/newticket) using the [QuerySet.extra keyword](https://code.djangoproject.com/query?status=assigned&status=new&keywords=~QuerySet.extra) with your use case (please check the list of existing tickets first) so that we can enhance the QuerySet API to allow removing `extra()`. We are no longer improving or fixing bugs for this method.

For example, this use of `extra()`:

```python
qs.extra(
    ...
    select={"val": "select col from sometable where othercol = %s"},
    ...
    select_params=(someparam,),
    ...
)
```

is equivalent to:

```python
qs.annotate(val=RawSQL("select col from sometable where othercol = %s", (someparam,)))
```

The main benefit of using `RawSQL` is that you can set `output_field` if needed. The main downside is that if you refer to some table alias of the queryset in the raw SQL, then it is possible that Django might change that alias (for example, when the queryset is used as a subquery in yet another query).

**Warning**

You should be very careful whenever you use `extra()`. Every time you use it, you should escape any parameters that the user can control by using `params` in order to protect against SQL injection attacks.

You also must not quote placeholders in the SQL string. This example is vulnerable to SQL injection because of the quotes around `%s`:

```sql
SELECT col FROM sometable WHERE othercol='%s' # unsafe!
```

You can read more about how Django’s [SQL injection protection](https://docs.djangoproject.com/en/stable/topics/security/#sql-injection-protection) works.

By definition, these extra lookups may not be portable to different database engines (because you’re explicitly writing SQL code) and violate the DRY principle, so you should avoid them if possible.

Specify one or more of `params`, `select`, `where`, or `tables`. None of the arguments is required, but you should use at least one of them.

- **`select`**

  The `select` argument lets you put extra fields in the `SELECT` clause. It should be a dictionary mapping attribute names to SQL clauses to use to calculate that attribute.

  Example:

  ```python
  Entry.objects.extra(select={"is_recent": "pub_date > '2006-01-01'"})
  ```

  As a result, each `Entry` object will have an extra attribute, `is_recent`, a boolean representing whether the entry’s `pub_date` is greater than Jan. 1, 2006.

  Django inserts the given SQL snippet directly into the `SELECT` statement, so the resulting SQL of the above example would be something like:

  ```sql
  SELECT blog_entry.*, (pub_date > '2006-01-01') AS is_recent FROM blog_entry;
  ```

  The next example is more advanced; it does a subquery to give each resulting `Blog` object an `entry_count` attribute, an integer count of associated `Entry` objects:

  ```python
  Blog.objects.extra(
      select={
          "entry_count": "SELECT COUNT(*) FROM blog_entry WHERE blog_entry.blog_id = blog_blog.id"
      },
  )
  ```

  In this particular case, we’re exploiting the fact that the query will already contain the `blog_blog` table in its `FROM` clause.

  The resulting SQL of the above example would be:

  ```sql
  SELECT blog_blog.*, (SELECT COUNT(*) FROM blog_entry WHERE blog_entry.blog_id = blog_blog.id) AS entry_count FROM blog_blog;
  ```

  Note that the parentheses required by most database engines around subqueries are not required in Django’s `select` clauses.

  In some rare cases, you might wish to pass parameters to the SQL fragments in `extra(select=...)`. For this purpose, use the `select_params` parameter.

  This will work, for example:

  ```python
  Blog.objects.extra(
      select={"a": "%s", "b": "%s"},
      select_params=("one", "two"),
  )
  ```

  If you need to use a literal `%s` inside your select string, use the sequence `%%s`.

- **`where` / `tables`**

  You can define explicit SQL `WHERE` clauses — perhaps to perform non-explicit joins — by using `where`. You can manually add tables to the SQL `FROM` clause by using `tables`.

  `where` and `tables` both take a list of strings. All `where` parameters are “AND”ed to any other search criteria.

  Example:

  ```python
  Entry.objects.extra(where=["foo='a' OR bar = 'a'", "baz = 'a'"])
  ```

  …translates (roughly) into the following SQL:

  ```sql
  SELECT * FROM blog_entry WHERE (foo='a' OR bar='a') AND (baz='a')
  ```

  Be careful when using the `tables` parameter if you’re specifying tables that are already used in the query. When you add extra tables via the `tables` parameter, Django assumes you want that table included an extra time, if it is already included. That creates a problem, since the table name will then be given an alias. If a table appears multiple times in an SQL statement, the second and subsequent occurrences must use aliases so the database can tell them apart. If you’re referring to the extra table you added in the extra `where` parameter this is going to cause errors.

  Normally, you’ll only be adding extra tables that don’t already appear in the query. However, if the case outlined above does occur, there are a few solutions. First, see if you can get by without including the extra table and use the one already in the query. If that isn’t possible, put your `extra()` call at the front of the queryset construction so that your table is the first use of that table. Finally, if all else fails, look at the query produced and rewrite your `where` addition to use the alias given to your extra table. The alias will be the same each time you construct the queryset in the same way, so you can rely upon the alias name to not change.

- **`order_by`**

  If you need to order the resulting queryset using some of the new fields or tables you have included via `extra()` use the `order_by` parameter to `extra()` and pass in a sequence of strings. These strings should either be model fields (as in the normal `order_by()` method on querysets), of the form `table_name.column_name` or an alias for a column that you specified in the `select` parameter to `extra()`.

  For example:

  ```python
  q = Entry.objects.extra(select={"is_recent": "pub_date > '2006-01-01'"})
  q = q.extra(order_by=["-is_recent"])
  ```

  This would sort all the items for which `is_recent` is true to the front of the result set (`True` sorts before `False` in a descending ordering).

  This shows, by the way, that you can make multiple calls to `extra()` and it will behave as you expect (adding new constraints each time).

- **`params`**

  The `where` parameter described above may use standard Python database string placeholders — `'%s'` to indicate parameters the database engine should automatically quote. The `params` argument is a list of any extra parameters to be substituted.

  Example:

  ```python
  Entry.objects.extra(where=["headline=%s"], params=["Lennon"])
  ```

  Always use `params` instead of embedding values directly into `where` because `params` will ensure values are quoted correctly according to your particular backend. For example, quotes will be escaped correctly.

  Bad:

  ```python
  Entry.objects.extra(where=["headline='Lennon'"])
  ```

  Good:

  ```python
  Entry.objects.extra(where=["headline=%s"], params=["Lennon"])
  ```

**Warning**

If you are performing queries on MySQL, note that MySQL’s silent type coercion may cause unexpected results when mixing types. If you query on a string type column, but with an integer value, MySQL will coerce the types of all values in the table to an integer before performing the comparison. For example, if your table contains the values `'abc'`, `'def'` and you query for `WHERE mycolumn=0`, both rows will match. To prevent this, perform the correct typecasting before using the value in a query.

# `defer()`

In some complex data-modeling situations, your models might contain a lot of fields, some of which could contain a lot of data (for example, text fields), or require expensive processing to convert them to Python objects. If you are using the results of a queryset in some situation where you don’t know if you need those particular fields when you initially fetch the data, you can tell Django not to retrieve them from the database.

This is done by passing the names of the fields to not load to `defer()`:

```python
Entry.objects.defer("headline", "body")
```

A queryset that has deferred fields will still return model instances. Each deferred field will be retrieved from the database if you access that field (one at a time, not all the deferred fields at once).

**Note**

Deferred fields will not lazy-load like this from asynchronous code. Instead, you will get a `SynchronousOnlyOperation` exception. If you are writing asynchronous code, you should not try to access any fields that you `defer()`.

You can make multiple calls to `defer()`. Each call adds new fields to the deferred set:

```python
# Defers both the body and headline fields.
Entry.objects.defer("body").filter(rating=5).defer("headline")
```

The order in which fields are added to the deferred set does not matter. Calling `defer()` with a field name that has already been deferred is harmless (the field will still be deferred).

You can defer loading of fields in related models (if the related models are loading via `select_related()`) by using the standard double-underscore notation to separate related fields:

```python
Blog.objects.select_related().defer("entry__headline", "entry__body")
```

If you want to clear the set of deferred fields, pass `None` as a parameter to `defer()`:

```python
# Load all fields immediately.
my_queryset.defer(None)
```

Some fields in a model won’t be deferred, even if you ask for them. You can never defer the loading of the primary key. If you are using `select_related()` to retrieve related models, you shouldn’t defer the loading of the field that connects from the primary model to the related one, doing so will result in an error.

Similarly, calling `defer()` (or its counterpart `only()`) including an argument from an aggregation (e.g. using the result of `annotate()`) doesn’t make sense: doing so will raise an exception. The aggregated values will always be fetched into the resulting queryset.

**Note**

The `defer()` method (and its cousin, `only()`, below) are only for advanced use-cases. They provide an optimization for when you have analyzed your queries closely and understand *exactly* what information you need and have measured that the difference between returning the fields you need and the full set of fields for the model will be significant.

Even if you think you are in the advanced use-case situation, **only use** `defer()` **when you cannot, at queryset load time, determine if you will need the extra fields or not**. If you are frequently loading and using a particular subset of your data, the best choice you can make is to normalize your models and put the non-loaded data into a separate model (and database table). If the columns *must* stay in the one table for some reason, create a model with `Meta.managed = False` (see the `managed` attribute documentation) containing just the fields you normally need to load and use that where you might otherwise call `defer()`. This makes your code more explicit to the reader, is slightly faster and consumes a little less memory in the Python process.

For example, both of these models use the same underlying database table:

```python
class CommonlyUsedModel(models.Model):
    f1 = models.CharField(max_length=10)
    class Meta:
        managed = False
        db_table = "app_largetable"

class ManagedModel(models.Model):
    f1 = models.CharField(max_length=10)
    f2 = models.CharField(max_length=10)
    class Meta:
        db_table = "app_largetable"

# Two equivalent QuerySets:
CommonlyUsedModel.objects.all()
ManagedModel.objects.defer("f2")
```

If many fields need to be duplicated in the unmanaged model, it may be best to create an abstract model with the shared fields and then have the unmanaged and managed models inherit from the abstract model.

**Note**

When calling `save()` for instances with deferred fields, only the loaded fields will be saved. See `save()` for more details.

# `only()`

The `only()` method is essentially the opposite of `defer()`. Only the fields passed into this method and that are *not* already specified as deferred are loaded immediately when the queryset is evaluated.

If you have a model where almost all the fields need to be deferred, using `only()` to specify the complementary set of fields can result in simpler code.

Suppose you have a model with fields `name`, `age`, and `biography`. The following two querysets are the same, in terms of deferred fields:

```python
Person.objects.defer("age", "biography")
Person.objects.only("name")
```

Whenever you call `only()` it *replaces* the set of fields to load immediately. The method’s name is mnemonic: **only** those fields are loaded immediately; the remainder are deferred. Thus, successive calls to `only()` result in only the final fields being considered:

```python
# This will defer all fields except the headline.
Entry.objects.only("body", "rating").only("headline")
```

Since `defer()` acts incrementally (adding fields to the deferred list), you can combine calls to `only()` and `defer()` and things will behave logically:

```python
# Final result is that everything except "headline" is deferred.
Entry.objects.only("headline", "body").defer("body")
# Final result loads headline immediately.
Entry.objects.defer("body").only("headline", "body")
```

All of the cautions in the note for the `defer()` documentation apply to `only()` as well. Use it cautiously and only after exhausting your other options.

Using `only()` and omitting a field requested using `select_related()` is an error as well. On the other hand, invoking `only()` without any arguments, will return every field (including annotations) fetched by the queryset.

As with `defer()`, you cannot access the non-loaded fields from asynchronous code and expect them to load. Instead, you will get a `SynchronousOnlyOperation` exception. Ensure that all fields you might access are in your `only()` call.

**Note**

When calling `save()` for instances with deferred fields, only the loaded fields will be saved. See `save()` for more details.

**Note**

When using `defer()` after `only()`, the fields in `defer()` will override `only()` for fields that are listed in both.

# `using()`

This method is for controlling which database the `QuerySet` will be evaluated against if you are using more than one database. The only argument this method takes is the alias of a database, as defined in `DATABASES`.

For example:

```python
# queries the database with the 'default' alias.
>>> Entry.objects.all()
# queries the database with the 'backup' alias
>>> Entry.objects.using("backup")
```

# `select_for_update()`

Returns a queryset that will lock rows until the end of the transaction, generating a `SELECT ... FOR UPDATE` SQL statement on supported databases.

For example:

```python
from django.db import transaction
entries = Entry.objects.select_for_update().filter(author=request.user)
with transaction.atomic():
    for entry in entries:
        ...
```

When the queryset is evaluated (`for entry in entries` in this case), all matched entries will be locked until the end of the transaction block, meaning that other transactions will be prevented from changing or acquiring locks on them.

Usually, if another transaction has already acquired a lock on one of the selected rows, the query will block until the lock is released. If this is not the behavior you want, call `select_for_update(nowait=True)`. This will make the call non-blocking. If a conflicting lock is already acquired by another transaction, `DatabaseError` will be raised when the queryset is evaluated. You can also ignore locked rows by using `select_for_update(skip_locked=True)` instead. The `nowait` and `skip_locked` are mutually exclusive and attempts to call `select_for_update()` with both options enabled will result in a `ValueError`.

By default, `select_for_update()` locks all rows that are selected by the query. For example, rows of related objects specified in `select_related()` are locked in addition to rows of the queryset’s model. If this isn’t desired, specify the related objects you want to lock in `select_for_update(of=(...))` using the same fields syntax as `select_related()`. Use the value `'self'` to refer to the queryset’s model.

**Lock parents models in `select_for_update(of=(...))`**

If you want to lock parents models when using [multi-table inheritance](https://docs.djangoproject.com/en/stable/topics/db/models/#multi-table-inheritance), you must specify parent link fields (by default `<parent_model_name>_ptr`) in the `of` argument. For example:

```python
Restaurant.objects.select_for_update(of=("self", "place_ptr"))
```

**Using `select_for_update(of=(...))` with specified fields**

If you want to lock models and specify selected fields, e.g. using `values()`, you must select at least one field from each model in the `of` argument. Models without selected fields will not be locked.

On PostgreSQL only, you can pass `no_key=True` in order to acquire a weaker lock, that still allows creating rows that merely reference locked rows (through a foreign key, for example) while the lock is in place. The PostgreSQL documentation has more details about [row-level lock modes](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-ROWS).

You can’t use `select_for_update()` on nullable relations:

```python
>>> Person.objects.select_related("hometown").select_for_update()
Traceback (most recent call last):
...
django.db.utils.NotSupportedError: FOR UPDATE cannot be applied to the nullable side of an outer join
```

To avoid that restriction, you can exclude null objects if you don’t care about them:

```python
>>> Person.objects.select_related("hometown").select_for_update().exclude(hometown=None)
<QuerySet [<Person: ...), ...]>
```

The `postgresql`, `oracle`, and `mysql` database backends support `select_for_update()`. However, MariaDB only supports the `nowait` argument, MariaDB 10.6+ also supports the `skip_locked` argument, and MySQL supports the `nowait`, `skip_locked`, and `of` arguments. The `no_key` argument is only supported on PostgreSQL.

Passing `nowait=True`, `skip_locked=True`, `no_key=True`, or `of` to `select_for_update()` using database backends that do not support these options, such as MySQL, raises a `NotSupportedError`. This prevents code from unexpectedly blocking.

Evaluating a queryset with `select_for_update()` in autocommit mode on backends which support `SELECT ... FOR UPDATE` is a `TransactionManagementError` error because the rows are not locked in that case. If allowed, this would facilitate data corruption and could easily be caused by calling code that expects to be run in a transaction outside of one.

Using `select_for_update()` on backends which do not support `SELECT ... FOR UPDATE` (such as SQLite) will have no effect. `SELECT ... FOR UPDATE` will not be added to the query, and an error isn’t raised if `select_for_update()` is used in autocommit mode.

**Warning**

Although `select_for_update()` normally fails in autocommit mode, since `TestCase` automatically wraps each test in a transaction, calling `select_for_update()` in a `TestCase` even outside an `atomic()` block will (perhaps unexpectedly) pass without raising a `TransactionManagementError`. To properly test `select_for_update()` you should use `TransactionTestCase`.

**Certain expressions may not be supported**

PostgreSQL doesn’t support `select_for_update()` with `Window` expressions.

# `raw()`

Takes a raw SQL query, executes it, and returns a `django.db.models.query.RawQuerySet` instance. This `RawQuerySet` instance can be iterated over just like a normal `QuerySet` to provide object instances.

See the [Performing raw SQL queries](https://docs.djangoproject.com/en/stable/topics/db/sql/) for more information.

**Warning**

`raw()` always triggers a new query and doesn’t account for previous filtering. As such, it should generally be called from the `Manager` or from a fresh `QuerySet` instance.

# Operators that return new `QuerySet`s

Combined querysets must use the same model.

## AND (`&`)

Combines two `QuerySet`s using the SQL `AND` operator in a manner similar to chaining filters.

The following are equivalent:

```python
Model.objects.filter(x=1) & Model.objects.filter(y=2)
Model.objects.filter(x=1).filter(y=2)
```

SQL equivalent:

```sql
SELECT ... WHERE x=1 AND y=2
```

## OR (`|`)

Combines two `QuerySet`s using the SQL `OR` operator.

The following are equivalent:

```python
Model.objects.filter(x=1) | Model.objects.filter(y=2)
from django.db.models import Q
Model.objects.filter(Q(x=1) | Q(y=2))
```

SQL equivalent:

```sql
SELECT ... WHERE x=1 OR y=2
```

`|` is not a commutative operation, as different (though equivalent) queries may be generated.

## XOR (`^`)

Combines two `QuerySet`s using the SQL `XOR` operator. A `XOR` expression matches rows that are matched by an odd number of operands.

The following are equivalent:

```python
Model.objects.filter(x=1) ^ Model.objects.filter(y=2)
from django.db.models import Q
Model.objects.filter(Q(x=1) ^ Q(y=2))
```

SQL equivalent:

```sql
SELECT ... WHERE x=1 XOR y=2
```

**Note**

`XOR` is natively supported on MariaDB and MySQL. On other databases, `x ^ y ^ ... ^ z` is converted to an equivalent:

```sql
(x OR y OR ... OR z) AND 1=MOD(
    (CASE WHEN x THEN 1 ELSE 0 END) +
    (CASE WHEN y THEN 1 ELSE 0 END) +
    ...
    (CASE WHEN z THEN 1 ELSE 0 END),
    2
)
```

# Methods that do not return `QuerySet`s

The following `QuerySet` methods evaluate the `QuerySet` and return something *other than* a `QuerySet`.

These methods do not use a cache (see [Caching and QuerySets](https://docs.djangoproject.com/en/stable/topics/db/queries/#caching-and-querysets)). Rather, they query the database each time they’re called.

Because these methods evaluate the QuerySet, they are blocking calls, and so their main (synchronous) versions cannot be called from asynchronous code. For this reason, each has a corresponding asynchronous version with an `a` prefix - for example, rather than `get(...)`, you can `await aget(...)`.

There is usually no difference in behavior apart from their asynchronous nature, but any differences are noted below next to each method.

## `get()`

**Asynchronous version**: `aget()`

Returns the object matching the given lookup parameters, which should be in the format described in [Field lookups](https://docs.djangoproject.com/en/stable/topics/db/queries/#field-lookups). You should use lookups that are guaranteed unique, such as the primary key or fields in a unique constraint. For example:

```python
Entry.objects.get(id=1)
Entry.objects.get(Q(blog=blog) & Q(entry_number=1))
```

If you expect a queryset to already return one row, you can use `get()` without any arguments to return the object for that row:

```python
Entry.objects.filter(pk=1).get()
```

If `get()` doesn’t find any object, it raises a `Model.DoesNotExist` exception:

```python
Entry.objects.get(id=-999) # raises Entry.DoesNotExist
```

If `get()` finds more than one object, it raises a `Model.MultipleObjectsReturned` exception:

```python
Entry.objects.get(name="A Duplicated Name") # raises Entry.MultipleObjectsReturned
```

Both these exception classes are attributes of the model class, and specific to that model. If you want to handle such exceptions from several `get()` calls for different models, you can use their generic base classes. For example, you can use `django.core.exceptions.ObjectDoesNotExist` to handle `DoesNotExist` exceptions from multiple models:

```python
from django.core.exceptions import ObjectDoesNotExist
try:
    blog = Blog.objects.get(id=1)
    entry = Entry.objects.get(blog=blog, entry_number=1)
except ObjectDoesNotExist:
    print("Either the blog or entry doesn't exist.")
```

## `create()`

**Asynchronous version**: `acreate()`

A convenience method for creating an object and saving it all in one step. Thus:

```python
p = Person.objects.create(first_name="Bruce", last_name="Springsteen")
```

and:

```python
p = Person(first_name="Bruce", last_name="Springsteen")
p.save(force_insert=True)
```

are equivalent.

The `force_insert` parameter is documented elsewhere, but all it means is that a new object will always be created. Normally, you won’t need to worry about this. However, if your model contains a manual primary key value that you set and if that value already exists in the database, a call to `create()` will fail with an `IntegrityError` since primary keys must be unique. Be prepared to handle the exception if you are using manual primary keys.

## `get_or_create()`

**Asynchronous version**: `aget_or_create()`

A convenience method for looking up an object with the given `kwargs` (may be empty if your model has defaults for all fields), creating one if necessary.

Returns a tuple of `(object, created)`, where `object` is the retrieved or created object and `created` is a boolean specifying whether a new object was created.

This is meant to prevent duplicate objects from being created when requests are made in parallel, and as a shortcut to boilerplatish code. For example:

```python
try:
    obj = Person.objects.get(first_name="John", last_name="Lennon")
except Person.DoesNotExist:
    obj = Person(first_name="John", last_name="Lennon", birthday=date(1940, 10, 9))
    obj.save()
```

Here, with concurrent requests, multiple attempts to save a `Person` with the same parameters may be made. To avoid this race condition, the above example can be rewritten using `get_or_create()` like so:

```python
obj, created = Person.objects.get_or_create(
    first_name="John",
    last_name="Lennon",
    defaults={"birthday": date(1940, 10, 9)},
)
```

Any keyword arguments passed to `get_or_create()` — *except* an optional one called `defaults` — will be used in a `get()` call. If an object is found, `get_or_create()` returns a tuple of that object and `False`.

**Warning**

This method is atomic assuming that the database enforces uniqueness of the keyword arguments (see `unique` or `unique_together`). If the fields used in the keyword arguments do not have a uniqueness constraint, concurrent calls to this method may result in multiple rows with the same parameters being inserted.

You can specify more complex conditions for the retrieved object by chaining `get_or_create()` with `filter()` and using `Q` objects. For example, to retrieve Robert or Bob Marley if either exists, and create the latter otherwise:

```python
from django.db.models import Q
obj, created = Person.objects.filter(
    Q(first_name="Bob") | Q(first_name="Robert"),
).get_or_create(last_name="Marley", defaults={"first_name": "Bob"})
```

If multiple objects are found, `get_or_create()` raises `MultipleObjectsReturned`. If an object is *not* found, `get_or_create()` will instantiate and save a new object, returning a tuple of the new object and `True`. The new object will be created roughly according to this algorithm:

```python
params = {k: v for k, v in kwargs.items() if "__" not in k}
params.update({k: v() if callable(v) else v for k, v in defaults.items()})
obj = self.model(**params)
obj.save()
```

In English, that means start with any non-`defaults` keyword argument that doesn’t contain a double underscore (which would indicate a non-exact lookup). Then add the contents of `defaults`, overriding any keys if necessary, and use the result as the keyword arguments to the model class. If there are any callables in `defaults`, evaluate them. As hinted at above, this is a simplification of the algorithm that is used, but it contains all the pertinent details. The internal implementation has some more error-checking than this and handles some extra edge-conditions; if you’re interested, read the code.

If you have a field named `defaults` and want to use it as an exact lookup in `get_or_create()`, use `'defaults__exact'`, like so:

```python
Foo.objects.get_or_create(defaults__exact="bar", defaults={"defaults": "baz"})
```

The `get_or_create()` method has similar error behavior to `create()` when you’re using manually specified primary keys. If an object needs to be created and the key already exists in the database, an `IntegrityError` will be raised.

Finally, a word on using `get_or_create()` in Django views. Please make sure to use it only in `POST` requests unless you have a good reason not to. `GET` requests shouldn’t have any effect on data. Instead, use `POST` whenever a request to a page has a side effect on your data. For more, see [Safe methods](https://datatracker.ietf.org/doc/html/rfc9110.html#section-9.2.1) in the HTTP spec.

**Warning**

You can use `get_or_create()` through `ManyToManyField` attributes and reverse relations. In that case, you will restrict the queries inside the context of that relation. That could lead you to some integrity problems if you don’t use it consistently.

Being the following models:

```python
class Chapter(models.Model):
    title = models.CharField(max_length=255, unique=True)

class Book(models.Model):
    title = models.CharField(max_length=256)
    chapters = models.ManyToManyField(Chapter)
```

You can use `get_or_create()` through Book’s chapters field, but it only fetches inside the context of that book:

```python
>>> book = Book.objects.create(title="Ulysses")
>>> book.chapters.get_or_create(title="Telemachus")
(<Chapter: Telemachus>, True)
>>> book.chapters.get_or_create(title="Telemachus")
(<Chapter: Telemachus>, False)
>>> Chapter.objects.create(title="Chapter 1")
<Chapter: Chapter 1>
>>> book.chapters.get_or_create(title="Chapter 1") # Raises IntegrityError
```

This is happening because it’s trying to get or create “Chapter 1” through the book “Ulysses”, but it can’t do either: the relation can’t fetch that chapter because it isn’t related to that book, but it can’t create it either because `title` field should be unique.

## `update_or_create()`

**Asynchronous version**: `aupdate_or_create()`

A convenience method for updating an object with the given `kwargs`, creating a new one if necessary. Both `create_defaults` and `defaults` are dictionaries of (field, value) pairs. The values in both `create_defaults` and `defaults` can be callables. `defaults` is used to update the object while `create_defaults` are used for the create operation. If `create_defaults` is not supplied, `defaults` will be used for the create operation.

Returns a tuple of `(object, created)`, where `object` is the created or updated object and `created` is a boolean specifying whether a new object was created.

The `update_or_create` method tries to fetch an object from the database based on the given `kwargs`. If a match is found, it updates the fields passed in the `defaults` dictionary.

This is meant as a shortcut to boilerplatish code. For example:

```python
defaults = {"first_name": "Bob"}
create_defaults = {"first_name": "Bob", "birthday": date(1940, 10, 9)}
try:
    obj = Person.objects.get(first_name="John", last_name="Lennon")
    for key, value in defaults.items():
        setattr(obj, key, value)
    obj.save()
except Person.DoesNotExist:
    new_values = {"first_name": "John", "last_name": "Lennon"}
    new_values.update(create_defaults)
    obj = Person(**new_values)
    obj.save()
```

This pattern gets quite unwieldy as the number of fields in a model goes up. The above example can be rewritten using `update_or_create()` like so:

```python
obj, created = Person.objects.update_or_create(
    first_name="John",
    last_name="Lennon",
    defaults={"first_name": "Bob"},
    create_defaults={"first_name": "Bob", "birthday": date(1940, 10, 9)},
)
```

For a detailed description of how names passed in `kwargs` are resolved, see `get_or_create()`.

As described above in `get_or_create()`, this method is prone to a race-condition which can result in multiple rows being inserted simultaneously if uniqueness is not enforced at the database level.

Like `get_or_create()` and `create()`, if you’re using manually specified primary keys and an object needs to be created but the key already exists in the database, an `IntegrityError` is raised.

## `bulk_create()`

**Asynchronous version**: `abulk_create()`

This method inserts the provided list of objects into the database in an efficient manner (generally only 1 query, no matter how many objects there are), and returns created objects as a list, in the same order as provided:

```python
>>> objs = Entry.objects.bulk_create(
    ...
    [
        ...
        Entry(headline="This is a test"),
        ...
        Entry(headline="This is only a test"),
        ...
    ]
    ...
)
```

This has a number of caveats though:

- The model’s `save()` method will not be called, and the `pre_save` and `post_save` signals will not be sent.
- It does not work with child models in a multi-table inheritance scenario.
- If the model’s primary key is an `AutoField` and `ignore_conflicts` is False, the primary key attribute can only be retrieved on certain databases (currently PostgreSQL, MariaDB, and SQLite 3.35+). On other databases, it will not be set.
- It does not work with many-to-many relationships.
- It casts `objs` to a list, which fully evaluates `objs` if it’s a generator. The cast allows inspecting all objects so that any objects with a manually set primary key can be inserted first. If you want to insert objects in batches without evaluating the entire generator at once, you can use this technique as long as the objects don’t have any manually set primary keys:

```python
from itertools import islice
batch_size = 100
objs = (Entry(headline="Test %s" % i) for i in range(1000))
while True:
    batch = list(islice(objs, batch_size))
    if not batch:
        break
    Entry.objects.bulk_create(batch, batch_size)
```

The `batch_size` parameter controls how many objects are created in a single query. The default is to create all objects in one batch, except for SQLite where the default is such that at most 999 variables per query are used.

On databases that support it (all but Oracle), setting the `ignore_conflicts` parameter to `True` tells the database to ignore failure to insert any rows that fail constraints such as duplicate unique values.

On databases that support it (all except Oracle), setting the `update_conflicts` parameter to `True`, tells the database to update `update_fields` when a row insertion fails on conflicts. On PostgreSQL and SQLite, in addition to `update_fields`, a list of `unique_fields` that may be in conflict must be provided.

Enabling the `ignore_conflicts` parameter disables setting the primary key on each model instance (if the database normally supports it).

**Warning**

On MySQL and MariaDB, setting the `ignore_conflicts` parameter to `True` turns certain types of errors, other than duplicate key, into warnings. Even with Strict Mode. For example: invalid values or non-nullable violations. See the [MySQL documentation](https://dev.mysql.com/doc/refman/en/sql-mode.html#ignore-strict-comparison) and [MariaDB documentation](https://mariadb.com/kb/en/ignore/) for more details.

## `bulk_update()`

**Asynchronous version**: `abulk_update()`

This method efficiently updates the given fields on the provided model instances, generally with one query, and returns the number of objects updated:

```python
>>> objs = [
    ...
    Entry.objects.create(headline="Entry 1"),
    ...
    Entry.objects.create(headline="Entry 2"),
    ...
]
>>> objs[0].headline = "This is entry 1"
>>> objs[1].headline = "This is entry 2"
>>> Entry.objects.bulk_update(objs, ["headline"])
2
```

`QuerySet.update()` is used to save the changes, so this is more efficient than iterating through the list of models and calling `save()` on each of them, but it has a few caveats:

- You cannot update the model’s primary key.
- Each model’s `save()` method isn’t called, and the `pre_save` and `post_save` signals aren’t sent.
- If updating a large number of columns in a large number of rows, the SQL generated can be very large. Avoid this by specifying a suitable `batch_size`.
- Updating fields defined on multi-table inheritance ancestors will incur an extra query per ancestor.
- When an individual batch contains duplicates, only the first instance in that batch will result in an update.
- The number of objects updated returned by the function may be fewer than the number of objects passed in. This can be due to duplicate objects passed in which are updated in the same batch or race conditions such that objects are no longer present in the database.

The `batch_size` parameter controls how many objects are saved in a single query. The default is to update all objects in one batch, except for SQLite and Oracle which have restrictions on the number of variables used in a query.

## `count()`

**Asynchronous version**: `acount()`

Returns an integer representing the number of objects in the database matching the `QuerySet`.

Example:

```python
# Returns the total number of entries in the database.
Entry.objects.count()
# Returns the number of entries whose headline contains 'Lennon'
Entry.objects.filter(headline__contains="Lennon").count()
```

A `count()` call performs a `SELECT COUNT(*)` behind the scenes, so you should always use `count()` rather than loading all of the record into Python objects and calling `len()` on the result (unless you need to load the objects into memory anyway, in which case `len()` will be faster).

Note that if you want the number of items in a `QuerySet` and are also retrieving model instances from it (for example, by iterating over it), it’s probably more efficient to use `len(queryset)` which won’t cause an extra database query like `count()` would.

If the queryset has already been fully retrieved, `count()` will use that length rather than perform an extra database query.

## `in_bulk()`

**Asynchronous version**: `ain_bulk()`

Takes a list of field values (`id_list`) and the `field_name` for those values, and returns a dictionary mapping each value to an instance of the object with the given field value. No `django.core.exceptions.ObjectDoesNotExist` exceptions will ever be raised by `in_bulk()`; that is, any `id_list` value not matching any instance will simply be ignored. If `id_list` isn’t provided, all objects in the queryset are returned. `field_name` must be a unique field or a distinct field (if there’s only one field specified in `distinct()`). `field_name` defaults to the primary key.

Example:

```python
>>> Blog.objects.in_bulk([1])
{1: <Blog: Beatles Blog>}
>>> Blog.objects.in_bulk([1, 2])
{1: <Blog: Beatles Blog>, 2: <Blog: Cheddar Talk>}
>>> Blog.objects.in_bulk([])
{}
>>> Blog.objects.in_bulk()
{1: <Blog: Beatles Blog>, 2: <Blog: Cheddar Talk>, 3: <Blog: Django Weblog>}
>>> Blog.objects.in_bulk(["beatles_blog"], field_name="slug")
{'beatles_blog': <Blog: Beatles Blog>}
>>> Blog.objects.distinct("name").in_bulk(field_name="name")
{'Beatles Blog': <Blog: Beatles Blog>, 'Cheddar Talk': <Blog: Cheddar Talk>, 'Django Weblog': <Blog: Django Weblog>}
```

If you pass `in_bulk()` an empty list, you’ll get an empty dictionary.

## `iterator()`

**Asynchronous version**: `aiterator()`

Evaluates the `QuerySet` (by performing the query) and returns an iterator (see [PEP 234](https://peps.python.org/pep-0234/)) over the results, or an asynchronous iterator (see [PEP 492](https://peps.python.org/pep-0492/)) if you call its asynchronous version `aiterator()`.

A `QuerySet` typically caches its results internally so that repeated evaluations do not result in additional queries. In contrast, `iterator()` will read results directly, without doing any caching at the `QuerySet` level (internally, the default iterator calls `iterator()` and caches the return value). For a `QuerySet` which returns a large number of objects that you only need to access once, this can result in better performance and a significant reduction in memory.

Note that using `iterator()` on a `QuerySet` which has already been evaluated will force it to evaluate again, repeating the query.

`iterator()` is compatible with previous calls to `prefetch_related()` as long as `chunk_size` is given. Larger values will necessitate fewer queries to accomplish the prefetching at the cost of greater memory usage.

On some databases (e.g. Oracle, [SQLite](https://www.sqlite.org/limits.html#max_variable_number)), the maximum number of terms in an SQL `IN` clause might be limited. Hence values below this limit should be used. (In particular, when prefetching across two or more relations, a `chunk_size` should be small enough that the anticipated number of results for each prefetched relation still falls below the limit.)

So long as the QuerySet does not prefetch any related objects, providing no value for `chunk_size` will result in Django using an implicit default of 2000.

Depending on the database backend, query results will either be loaded all at once or streamed from the database using server-side cursors.

### With server-side cursors

Oracle and [PostgreSQL](https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-server-side-cursors) use server-side cursors to stream results from the database without loading the entire result set into memory.

The Oracle database driver always uses server-side cursors.

With server-side cursors, the `chunk_size` parameter specifies the number of results to cache at the database driver level. Fetching bigger chunks diminishes the number of round trips between the database driver and the database, at the expense of memory.

On PostgreSQL, server-side cursors will only be used when the `DISABLE_SERVER_SIDE_CURSORS` setting is `False`. Read [Transaction pooling and server-side cursors](https://docs.djangoproject.com/en/stable/ref/databases/#transaction-pooling-server-side-cursors) if you’re using a connection pooler configured in transaction pooling mode. When server-side cursors are disabled, the behavior is the same as databases that don’t support server-side cursors.

### Without server-side cursors

MySQL doesn’t support streaming results, hence the Python database driver loads the entire result set into memory. The result set is then transformed into Python row objects by the database adapter using the `fetchmany()` method defined in [PEP 249](https://peps.python.org/pep-0249/).

SQLite can fetch results in batches using `fetchmany()`, but since SQLite doesn’t provide isolation between queries within a connection, be careful when writing to the table being iterated over. See [Isolation when using QuerySet.iterator()](https://docs.djangoproject.com/en/stable/ref/databases/#sqlite-isolation) for more information.

The `chunk_size` parameter controls the size of batches Django retrieves from the database driver. Larger batches decrease the overhead of communicating with the database driver at the expense of a slight increase in memory consumption.

So long as the QuerySet does not prefetch any related objects, providing no value for `chunk_size` will result in Django using an implicit default of 2000, a value derived from [a calculation on the psycopg mailing list](https://www.postgresql.org/message-id/4D2F2C71.8080805%40dndg.it):

> Assuming rows of 10-20 columns with a mix of textual and numeric data, 2000 is going to fetch less than 100KB of data, which seems a good compromise between the number of rows transferred and the data discarded if the loop is exited early.

## `latest()`

**Asynchronous version**: `alatest()`

Returns the latest object in the table based on the given field(s).

This example returns the latest `Entry` in the table, according to the `pub_date` field:

```python
Entry.objects.latest("pub_date")
```

You can also choose the latest based on several fields. For example, to select the `Entry` with the earliest `expire_date` when two entries have the same `pub_date`:

```python
Entry.objects.latest("pub_date", "-expire_date")
```

The negative sign in `'-expire_date'` means to sort `expire_date` in *descending* order. Since `latest()` gets the last result, the `Entry` with the earliest `expire_date` is selected.

If your model’s `Meta` specifies `get_latest_by`, you can omit any arguments to `earliest()` or `latest()`. The fields specified in `get_latest_by` will be used by default.

Like `get()`, `earliest()` and `latest()` raise `DoesNotExist` if there is no object with the given parameters.

Note that `earliest()` and `latest()` exist purely for convenience and readability.

**`earliest()` and `latest()` may return instances with null dates.**

Since ordering is delegated to the database, results on fields that allow null values may be ordered differently if you use different databases. For example, PostgreSQL and MySQL sort null values as if they are higher than non-null values, while SQLite does the opposite.

You may want to filter out null values:

```python
Entry.objects.filter(pub_date__isnull=False).latest("pub_date")
```

## `earliest()`

**Asynchronous version**: `aearliest()`

Works otherwise like `latest()` except the direction is changed.

## `first()`

**Asynchronous version**: `afirst()`

Returns the first object matched by the queryset, or `None` if there is no matching object. If the `QuerySet` has no ordering defined, then the queryset is automatically ordered by the primary key. This can affect aggregation results as described in [Interaction with order_by()](https://docs.djangoproject.com/en/stable/topics/db/aggregation/#aggregation-ordering-interaction).

Example:

```python
p = Article.objects.order_by("title", "pub_date").first()
```

Note that `first()` is a convenience method, the following code sample is equivalent to the above example:

```python
try:
    p = Article.objects.order_by("title", "pub_date")[0]
except IndexError:
    p = None
```

## `last()`

**Asynchronous version**: `alast()`

Works like `first()`, but returns the last object in the queryset.

## `aggregate()`

**Asynchronous version**: `aaggregate()`

Returns a dictionary of aggregate values (averages, sums, etc.) calculated over the `QuerySet`. Each argument to `aggregate()` specifies a value that will be included in the dictionary that is returned.

The aggregation functions that are provided by Django are described in [Aggregation Functions](https://docs.djangoproject.com/en/stable/topics/db/aggregation/#aggregation-functions) below. Since aggregates are also [query expressions](https://docs.djangoproject.com/en/stable/ref/models/expressions/), you may combine aggregates with other aggregates or values to create complex aggregates.

Aggregates specified using keyword arguments will use the keyword as the name for the annotation. Anonymous arguments will have a name generated for them based upon the name of the aggregate function and the model field that is being aggregated. Complex aggregates cannot use anonymous arguments and must specify a keyword argument as an alias.

For example, when you are working with blog entries, you may want to know the number of authors that have contributed blog entries:

```python
>>> from django.db.models import Count
>>> Blog.objects.aggregate(Count("entry__authors"))
{'entry__authors__count': 16}
```

By using a keyword argument to specify the aggregate function, you can control the name of the aggregation value that is returned:

```python
>>> Blog.objects.aggregate(number_of_authors=Count("entry__authors"))
{'number_of_authors': 16}
```

For an in-depth discussion of aggregation, see [the topic guide on Aggregation](https://docs.djangoproject.com/en/stable/topics/db/aggregation/).

## `exists()`

**Asynchronous version**: `aexists()`

Returns `True` if the `QuerySet` contains any results, and `False` if not. This tries to perform the query in the simplest and fastest way possible, but it *does* execute nearly the same query as `count()` would.

---

# QuerySet API Reference

## When QuerySets are evaluated

### Pickling QuerySets

QuerySets are picklable if they are not being used in an asynchronous context. When a QuerySet is pickled, the query is pickled, not the results of the query. Unpickling a QuerySet will yield a new QuerySet that is ready to be evaluated again.

## QuerySet API

### Methods that return new QuerySets

#### `filter()`

Returns a new QuerySet containing objects that match the given lookup parameters.

#### `exclude()`

Returns a new QuerySet containing objects that do not match the given lookup parameters.

#### `annotate()`

Adds the output of the given annotation to each object in the QuerySet.

#### `alias()`

Creates a shortcut for a more complex expression to be used in a QuerySet.

#### `order_by()`

Returns a new QuerySet instance with the ordering changed as specified.

#### `reverse()`

Returns a new QuerySet instance with the ordering reversed.

#### `distinct()`

Returns a new QuerySet that uses SELECT DISTINCT in its SQL query.

#### `values()`

Returns a QuerySet that returns dictionaries, rather than model instances when used.

#### `values_list()`

Returns a QuerySet that returns tuples, rather than model instances when used.

#### `dates()`

Returns a QuerySet that evaluates to a list of datetime.date objects representing all available dates for the field name specified.

#### `datetimes()`

Returns a QuerySet that evaluates to a list of datetime.datetime objects representing all available datetimes for the field name specified.

#### `none()`

Returns an empty QuerySet of the same class as the current QuerySet.

#### `all()`

Returns a copy of the current QuerySet.

#### `union()`

Combines the results of two or more QuerySets.

#### `intersection()`

Returns a new QuerySet containing objects that are present in both QuerySets.

#### `difference()`

Returns a new QuerySet containing objects that are present in the first QuerySet but not in the second QuerySet.

#### `select_related()`

Returns a new QuerySet instance that will select related objects.

#### `prefetch_related()`

Returns a new QuerySet instance that will prefetch the specified many-to-many and one-to-many objects when the QuerySet is evaluated.

#### `extra()`

Adds extra SQL (a dictionary) without escaping to the query.

#### `defer()`

Defers loading of certain fields until they are accessed.

#### `only()`

Specifies the fields that should be included in the SELECT clause.

#### `using()`

Specifies the database to use for this QuerySet.

#### `select_for_update()`

Locks rows until the end of the transaction.

#### `raw()`

Executes a raw SQL query and returns a RawQuerySet.

### Operators that return new QuerySets

#### AND (`&`)

Combines two QuerySets using the SQL AND operator.

#### OR (`|`)

Combines two QuerySets using the SQL OR operator.

#### XOR (`^`)

Combines two QuerySets using the SQL XOR operator.

### Methods that do not return QuerySets

#### `get()`

Returns the object matching the QuerySet, an exception is raised if no results are found.

#### `create()`

Creates a new object with the given keyword arguments.

#### `get_or_create()`

Looks up an object with the given keyword arguments, creating one if necessary.

#### `update_or_create()`

Looks up an object with the given keyword arguments, updating one if it exists, otherwise creating a new one.

#### `bulk_create()`

Creates multiple objects in the database from the provided list of model instances.

#### `bulk_update()`

Updates multiple objects in the database from the provided list of model instances.

#### `count()`

Returns an integer representing the number of objects in the database matching the QuerySet.

#### `in_bulk()`

Returns a dictionary mapping each of the given IDs to the object with that ID.

#### `iterator()`

An iterator over the results from applying this QuerySet to the database.

##### With server-side cursors

When using server-side cursors, the database cursor is kept open for the lifetime of the iterator.

##### Without server-side cursors

Without server-side cursors, the database cursor is closed after each iteration.

#### `latest()`

Returns the latest object in the table based on the given field(s).

#### `earliest()`

Works otherwise like `latest()` except the direction is changed.

#### `first()`

Returns the first object matched by the queryset, or `None` if there is no matching object.

#### `last()`

Works like `first()`, but returns the last object in the queryset.

#### `aggregate()`

Returns a dictionary of aggregate values (averages, sums, etc.) calculated over the QuerySet.

#### `exists()`

Returns `True` if the QuerySet contains any results, and `False` if not.

#### `contains()`

Returns `True` if the QuerySet contains `obj`, and `False` if not.

#### `update()`

Performs an SQL update query for the specified fields, and returns the number of rows matched.

##### Ordered queryset

Chaining `order_by()` with `update()` is supported only on MariaDB and MySQL, and is ignored for different databases.

#### `delete()`

Performs an SQL delete query on all rows in the QuerySet and returns the number of objects deleted and a dictionary with the number of deletions per object type.

#### `as_manager()`

Class method that returns an instance of `Manager` with a copy of the QuerySet’s methods.

#### `explain()`

Returns a string of the QuerySet’s execution plan, which details how the database would execute the query.

### Field lookups

Field lookups are how you specify the meat of an SQL `WHERE` clause. They’re specified as keyword arguments to the QuerySet methods `filter()`, `exclude()` and `get()`.

#### `exact`

Exact match. If the value provided for comparison is `None`, it will be interpreted as an SQL `NULL`.

#### `iexact`

Case-insensitive exact match. If the value provided for comparison is `None`, it will be interpreted as an SQL `NULL`.

#### `contains`

Case-sensitive containment test.

#### `icontains`

Case-insensitive containment test.

#### `in`

In a given iterable; often a list, tuple, or queryset.

#### `gt`

Greater than.

#### `gte`

Greater than or equal to.

#### `lt`

Less than.

#### `lte`

Less than or equal to.

#### `startswith`

Case-sensitive starts-with.

#### `istartswith`

Case-insensitive starts-with.

#### `endswith`

Case-sensitive ends-with.

#### `iendswith`

Case-insensitive ends-with.

#### `range`

Range test (inclusive).

#### `date`

For datetime fields, casts the value as date. Allows chaining additional field lookups.

#### `year`

For date and datetime fields, an exact year match.

#### `iso_year`

For date and datetime fields, an exact ISO 8601 week-numbering year match.

#### `month`

For date and datetime fields, an exact month match.

#### `day`

For date and datetime fields, an exact day match.

#### `week`

For date and datetime fields, return the week number (1-52 or 53) according to ISO-8601.

#### `week_day`

For date and datetime fields, a ‘day of the week’ match.

#### `iso_week_day`

For date and datetime fields, an exact ISO 8601 day of the week match.

#### `quarter`

For date and datetime fields, a ‘quarter of the year’ match.

#### `time`

For datetime fields, casts the value as time. Allows chaining additional field lookups.

#### `hour`

For datetime and time fields, an exact hour match.

#### `minute`

For datetime and time fields, an exact minute match.

#### `second`

For datetime and time fields, an exact second match.

#### `isnull`

Takes either `True` or `False`, which correspond to SQL queries of `IS NULL` and `IS NOT NULL`, respectively.

#### `regex`

Case-sensitive regular expression match.

#### `iregex`

Case-insensitive regular expression match.

### Aggregation functions

Django provides the following aggregation functions in the `django.db.models` module.

#### `expressions`

Strings that reference fields on the model, transforms of the field, or query expressions.

#### `output_field`

An optional argument that represents the model field of the return value.

#### `filter`

An optional `Q` object that’s used to filter the rows that are aggregated.

#### `default`

An optional argument that allows specifying a value to use as a default value when the queryset (or grouping) contains no entries.

#### `**extra`

Keyword arguments that can provide extra context for the SQL generated by the aggregate.

#### `Avg`

Returns the mean value of the given expression.

#### `Count`

Returns the number of objects that are related through the provided expression.

#### `Max`

Returns the maximum value of the given expression.

#### `Min`

Returns the minimum value of the given expression.

#### `StdDev`

Returns the standard deviation of the data in the provided expression.

#### `Sum`

Computes the sum of all values of the given expression.

#### `Variance`

Returns the variance of the data in the provided expression.

## Query-related tools

### `Q()` objects

A `Q()` object represents an SQL condition that can be used in database-related operations.

### `Prefetch()` objects

The `Prefetch()` object can be used to control the operation of `prefetch_related()`.

### `prefetch_related_objects()`

Prefetches the given lookups on an iterable of model instances.

### `FilteredRelation()` objects

`FilteredRelation` is used with `annotate()` to create an `ON` clause when a `JOIN` is performed.