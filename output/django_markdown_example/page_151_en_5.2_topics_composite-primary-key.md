# Composite Primary Keys

New in Django 5.2.

In Django, each model has a primary key. By default, this primary key consists of a single field.

In most cases, a single primary key should suffice. In database design, however, defining a primary key consisting of multiple fields is sometimes necessary.

To use a composite primary key, when defining a model set the `pk` attribute to be a [`CompositePrimaryKey`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.CompositePrimaryKey):

```python
class Product(models.Model):
    name = models.CharField(max_length=100)

class Order(models.Model):
    reference = models.CharField(max_length=20, primary_key=True)

class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()
```

This will instruct Django to create a composite primary key (`PRIMARY KEY (product_id, order_id)`) when creating the table.

A composite primary key is represented by a `tuple`:

```python
>>> product = Product.objects.create(name="apple")
>>> order = Order.objects.create(reference="A755H")
>>> item = OrderLineItem.objects.create(product=product, order=order, quantity=1)
>>> item.pk
(1, "A755H")
```

You can assign a `tuple` to the [`pk`](https://docs.djangoproject.com/en/5.2/ref/models/instances/#django.db.models.Model.pk) attribute. This sets the associated field values:

```python
>>> item = OrderLineItem(pk=(2, "B142C"))
>>> item.pk
(2, "B142C")
>>> item.product_id
2
>>> item.order_id
"B142C"
```

A composite primary key can also be filtered by a `tuple`:

```python
>>> OrderLineItem.objects.filter(pk=(1, "A755H")).count()
1
```

We’re still working on composite primary key support for [relational fields](https://docs.djangoproject.com/en/5.2/topics/composite-primary-key/#cpk-and-relations), including [`GenericForeignKey`](https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey) fields, and the Django admin. Models with composite primary keys cannot be registered in the Django admin at this time. You can expect to see this in future releases.

## Migrating to a Composite Primary Key

Django doesn’t support migrating to, or from, a composite primary key after the table is created. It also doesn’t support adding or removing fields from the composite primary key.

If you would like to migrate an existing table from a single primary key to a composite primary key, follow your database backend’s instructions to do so.

Once the composite primary key is in place, add the `CompositePrimaryKey` field to your model. This allows Django to recognize and handle the composite primary key appropriately.

While migration operations (e.g. `AddField`, `AlterField`) on primary key fields are not supported, `makemigrations` will still detect changes.

In order to avoid errors, it’s recommended to apply such migrations with `--fake`.

Alternatively, [`SeparateDatabaseAndState`](https://docs.djangoproject.com/en/5.2/ref/migration-operations/#django.db.migrations.operations.SeparateDatabaseAndState) may be used to execute the backend-specific migrations and Django-generated migrations in a single operation.

## Composite Primary Keys and Relations

[Relationship fields](https://docs.djangoproject.com/en/5.2/ref/models/fields/#relationship-fields), including [generic relations](https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/#generic-relations) do not support composite primary keys.

For example, given the `OrderLineItem` model, the following is not supported:

```python
class Foo(models.Model):
    item = models.ForeignKey(OrderLineItem, on_delete=models.CASCADE)
```

Because `ForeignKey` currently cannot reference models with composite primary keys.

To work around this limitation, `ForeignObject` can be used as an alternative:

```python
class Foo(models.Model):
    item_order_id = models.IntegerField()
    item_product_id = models.CharField(max_length=20)
    item = models.ForeignObject(
        OrderLineItem,
        on_delete=models.CASCADE,
        from_fields=("item_order_id", "item_product_id"),
        to_fields=("order_id", "product_id"),
    )
```

`ForeignObject` is much like `ForeignKey`, except that it doesn’t create any columns (e.g. `item_id`), foreign key constraints or indexes in the database.

> **Warning**
>
> `ForeignObject` is an internal API. This means it is not covered by our [deprecation policy](https://docs.djangoproject.com/en/5.2/internals/release-process/#internal-release-deprecation-policy).

## Composite Primary Keys and Database Functions

Many database functions only accept a single expression.

```sql
MAX("order_id") -- OK
MAX("product_id","order_id") -- ERROR
```

In these cases, providing a composite primary key reference raises a `ValueError`, since it is composed of multiple column expressions. An exception is made for `Count`.

```python
Max("order_id")  # OK
Max("pk")  # ValueError
Count("pk")  # OK
```

## Composite Primary Keys in Forms

As a composite primary key is a virtual field, a field which doesn’t represent a single database column, this field is excluded from ModelForms.

For example, take the following form:

```python
class OrderLineItemForm(forms.ModelForm):
    class Meta:
        model = OrderLineItem
        fields = "__all__"
```

This form does not have a form field `pk` for the composite primary key:

```python
>>> OrderLineItemForm()
<OrderLineItemForm bound=False, valid=Unknown, fields=(product;order;quantity)>
```

Setting the primary composite field `pk` as a form field raises an unknown field [`FieldError`](https://docs.djangoproject.com/en/5.2/ref/exceptions/#django.core.exceptions.FieldError).

> **Primary key fields are read only**
>
> If you change the value of a primary key on an existing object and then save it, a new object will be created alongside the old one (see [`Field.primary_key`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.Field.primary_key)).
>
> This is also true of composite primary keys. Hence, you may want to set [`Field.editable`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.Field.editable) to `False` on all primary key fields to exclude them from ModelForms.

## Composite Primary Keys in Model Validation

Since `pk` is only a virtual field, including `pk` as a field name in the `exclude` argument of [`Model.clean_fields()`](https://docs.djangoproject.com/en/5.2/ref/models/instances/#django.db.models.Model.clean_fields) has no effect. To exclude the composite primary key fields from [model validation](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects), specify each field individually. [`Model.validate_unique()`](https://docs.djangoproject.com/en/5.2/ref/models/instances/#django.db.models.Model.validate_unique) can still be called with `exclude={"pk"}` to skip uniqueness checks.

## Building Composite Primary Key Ready Applications

Prior to the introduction of composite primary keys, the single field composing the primary key of a model could be retrieved by introspecting the [`primary key`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.Field.primary_key) attribute of its fields:

```python
>>> pk_field = None
>>> for field in Product._meta.get_fields():
...     if field.primary_key:
...         pk_field = field
...     break
>>> pk_field
<django.db.models.fields.AutoField: id>
```

Now that a primary key can be composed of multiple fields the [`primary key`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.Field.primary_key) attribute can no longer be relied upon to identify members of the primary key as it will be set to `False` to maintain the invariant that at most one field per model will have this attribute set to `True`:

```python
>>> pk_fields = []
>>> for field in OrderLineItem._meta.get_fields():
...     if field.primary_key:
...         pk_fields.append(field)
...
>>> pk_fields
[]
```

In order to build application code that properly handles composite primary keys the [`_meta.pk_fields`](https://docs.djangoproject.com/en/5.2/ref/models/meta/#django.db.models.options.Options.pk_fields) attribute should be used instead:

```python
>>> Product._meta.pk_fields
[<django.db.models.fields.AutoField: id>]
>>> OrderLineItem._meta.pk_fields
[
    <django.db.models.fields.ForeignKey: product>,
    <django.db.models.fields.ForeignKey: order>
]
```