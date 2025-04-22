# Model Class Reference

This document covers features of the `Model` class. For more information about models, see [the complete list of Model reference guides](../).

## Attributes

### `DoesNotExist`

#### exception Model.DoesNotExist

This exception is raised by the ORM when an expected object is not found. For example, `QuerySet.get()` will raise it when no object is found for the given lookups.

Django provides a `DoesNotExist` exception as an attribute of each model class to identify the class of object that could not be found, allowing you to catch exceptions for a particular model class. The exception is a subclass of `django.core.exceptions.ObjectDoesNotExist`.

### `MultipleObjectsReturned`

#### exception Model.MultipleObjectsReturned

This exception is raised by `QuerySet.get()` when multiple objects are found for the given lookups.

Django provides a `MultipleObjectsReturned` exception as an attribute of each model class to identify the class of object for which multiple objects were found, allowing you to catch exceptions for a particular model class. The exception is a subclass of `django.core.exceptions.MultipleObjectsReturned`.

### `objects`

#### Model.objects

Each non-abstract `Model` class must have a `Manager` instance added to it. Django ensures that in your model class you have at least a default `Manager` specified. If you don’t add your own `Manager`, Django will add an attribute `objects` containing default `Manager` instance. If you add your own `Manager` instance attribute, the default one does not appear. Consider the following example:

```python
from django.db import models

class Person(models.Model):
    # Add manager with another name
    people = models.Manager()
```

For more details on model managers see [Managers](../../../topics/db/managers/) and [Retrieving objects](../../../topics/db/queries/#retrieving-objects).