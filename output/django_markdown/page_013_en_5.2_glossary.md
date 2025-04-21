# Glossary

## concrete model
A non-abstract (`abstract=False`) model.

## field
An attribute on a model; a given field usually maps directly to a single database column.

See [Models](../topics/db/models/).

## generic view
A higher-order view function that provides an abstract/generic implementation of a common idiom or pattern found in view development.

See [Class-based views](../topics/class-based-views/).

## model
Models store your application's data.

See [Models](../topics/db/models/).

## MTV
"Model-template-view"; a software pattern, similar in style to MVC, but a better description of the way Django does things.

See [the FAQ entry](../faq/general/#faq-mtv).

## MVC
[Model-view-controller](https://en.wikipedia.org/wiki/Model-view-controller); a software pattern. Django [follows MVC to some extent](../faq/general/#faq-mtv).

## project
A Python package – i.e. a directory of code – that contains all the settings for an instance of Django. This would include database configuration, Django-specific options and application-specific settings.

## property
Also known as "managed attributes", and a feature of Python since version 2.2. This is a neat way to implement attributes whose usage resembles attribute access, but whose implementation uses method calls.

See [`property`](https://docs.python.org/3/library/functions.html#property).

## queryset
An object representing some set of rows to be fetched from the database.

See [Making queries](../topics/db/queries/).

## slug
A short label for something, containing only letters, numbers, underscores or hyphens. They're generally used in URLs. For example, in a typical blog entry URL:

```
https://www.djangoproject.com/weblog/2008/apr/12/spring/
```

the last bit (`spring`) is the slug.

## template
A chunk of text that acts as formatting for representing data. A template helps to abstract the presentation of data from the data itself.

See [Templates](../topics/templates/).

## view
A function responsible for rendering a page.