# Model Index Reference

Index classes ease creating database indexes. They can be added using the [`Meta.indexes` option](../options/#django.db.models.Options.indexes). This document explains the API references of [`Index`](#django.db.models.Index) which includes the [index options](#index-options).

## Referencing Built-in Indexes

Indexes are defined in `django.db.models.indexes`, but for convenience they’re imported into [`django.db.models`](../../../topics/db/models/#module-django.db.models). The standard convention is to use `from django.db import models` and refer to the indexes as `models.<IndexClass>`.

## `Index` Options

### `Index`(*expressions, fields=(), name=None, db_tablespace=None, opclasses=(), condition=None, include=None)

Creates an index (B-Tree) in the database.

### `expressions`

Positional argument `*expressions` allows creating functional indexes on expressions and database functions.

For example:

```python
Index(Lower("title").desc(), "pub_date", name="lower_title_date_idx")
```

creates an index on the lowercased value of the `title` field in descending order and the `pub_date` field in the default ascending order.

Another example:

```python
Index(F("height") * F("weight"), Round("weight"), name="calc_idx")
```

creates an index on the result of multiplying fields `height` and `weight` and the `weight` rounded to the nearest integer.

[`Index.name`](#django.db.models.Index.name) is required when using `*expressions`.

#### Restrictions on Oracle

Oracle requires functions referenced in an index to be marked as `DETERMINISTIC`. Django doesn’t validate this but Oracle will error. This means that functions such as [`Random()`](../database-functions/#django.db.models.functions.Random) aren’t accepted.

#### Restrictions on PostgreSQL

PostgreSQL requires functions and operators referenced in an index to be marked as `IMMUTABLE`. Django doesn’t validate this but PostgreSQL will error. This means that functions such as [`Concat()`](../database-functions/#django.db.models.functions.Concat) aren’t accepted.

#### MySQL and MariaDB

Functional indexes are ignored with MySQL < 8.0.13 and MariaDB as neither supports them.

### `fields`

A list or tuple of the name of the fields on which the index is desired.

By default, indexes are created with an ascending order for each column. To define an index with a descending order for a column, add a hyphen before the field’s name.

For example `Index(fields=['headline', '-pub_date'])` would create SQL with `(headline, pub_date DESC)`.

#### MariaDB

Index ordering isn’t supported on MariaDB < 10.8. In that case, a descending index is created as a normal index.

### `name`

The name of the index. If `name` isn’t provided Django will auto-generate a name. For compatibility with different databases, index names cannot be longer than 30 characters and shouldn’t start with a number (0-9) or underscore (_).

#### Partial Indexes in Abstract Base Classes

You must always specify a unique name for an index. As such, you cannot normally specify a partial index on an abstract base class, since the [`Meta.indexes`](../options/#django.db.models.Options.indexes) option is inherited by subclasses, with exactly the same values for the attributes (including `name`) each time. To work around name collisions, part of the name may contain `'%(app_label)s'` and `'%(class)s'`, which are replaced, respectively, by the lowercased app label and class name of the concrete model. For example `Index(fields=['title'], name='%(app_label)s_%(class)s_title_index')`.

### `db_tablespace`

The name of the [database tablespace](../../../topics/db/tablespaces/) to use for this index. For single field indexes, if `db_tablespace` isn’t provided, the index is created in the `db_tablespace` of the field.

If [`Field.db_tablespace`](../fields/#django.db.models.Field.db_tablespace) isn’t specified (or if the index uses multiple fields), the index is created in tablespace specified in the [`db_tablespace`](../options/#django.db.models.Options.db_tablespace) option inside the model’s `class Meta`. If neither of those tablespaces are set, the index is created in the same tablespace as the table.

#### See Also

For a list of PostgreSQL-specific indexes, see [`django.contrib.postgres.indexes`](../../contrib/postgres/indexes/#module-django.contrib.postgres.indexes).

### `opclasses`

The names of the [PostgreSQL operator classes](https://www.postgresql.org/docs/current/indexes-opclass.html) to use for this index. If you require a custom operator class, you must provide one for each field in the index.

For example, `GinIndex(name='json_index', fields=['jsonfield'], opclasses=['jsonb_path_ops'])` creates a gin index on `jsonfield` using `jsonb_path_ops`.

`opclasses` are ignored for databases besides PostgreSQL.

[`Index.name`](#django.db.models.Index.name) is required when using `opclasses`.

### `condition`

If the table is very large and your queries mostly target a subset of rows, it may be useful to restrict an index to that subset. Specify a condition as a [`Q`](../querysets/#django.db.models.Q). For example, `condition=Q(pages__gt=400)` indexes records with more than 400 pages.

[`Index.name`](#django.db.models.Index.name) is required when using `condition`.

#### Restrictions on PostgreSQL

PostgreSQL requires functions referenced in the condition to be marked as IMMUTABLE. Django doesn’t validate this but PostgreSQL will error. This means that functions such as [Date functions](../database-functions/#date-functions) and [`Concat`](../database-functions/#django.db.models.functions.Concat) aren’t accepted. If you store dates in [`DateTimeField`](../fields/#django.db.models.DateTimeField), comparison to [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) objects may require the `tzinfo` argument to be provided because otherwise the comparison could result in a mutable function due to the casting Django does for [lookups](../querysets/#field-lookups).

#### Restrictions on SQLite

SQLite [imposes restrictions](https://www.sqlite.org/partialindex.html) on how a partial index can be constructed.

#### Oracle

Oracle does not support partial indexes. Instead, partial indexes can be emulated by using functional indexes together with [`Case`](../conditional-expressions/#django.db.models.expressions.Case) expressions.

#### MySQL and MariaDB

The `condition` argument is ignored with MySQL and MariaDB as neither supports conditional indexes.

### `include`

A list or tuple of the names of the fields to be included in the covering index as non-key columns. This allows index-only scans to be used for queries that select only included fields ([`include`](#django.db.models.Index.include)) and filter only by indexed fields ([`fields`](#django.db.models.Index.fields)).

For example:

```python
Index(name="covering_index", fields=["headline"], include=["pub_date"])
```

will allow filtering on `headline`, also selecting `pub_date`, while fetching data only from the index.

Using `include` will produce a smaller index than using a multiple column index but with the drawback that non-key columns can not be used for sorting or filtering.

`include` is ignored for databases besides PostgreSQL.

[`Index.name`](#django.db.models.Index.name) is required when using `include`.

See the PostgreSQL documentation for more details about [covering indexes](https://www.postgresql.org/docs/current/indexes-index-only-scans.html).

#### Restrictions on PostgreSQL

PostgreSQL supports covering B-Tree and [`GiST` indexes](../../contrib/postgres/indexes/#django.contrib.postgres.indexes.GistIndex). PostgreSQL 14+ also supports covering [`SP-GiST` indexes](../../contrib/postgres/indexes/#django.contrib.postgres.indexes.SpGistIndex).