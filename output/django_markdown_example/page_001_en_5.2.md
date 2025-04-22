# Django Documentation

Everything you need to know about Django.

## First Steps

Are you new to Django or to programming? This is the place to start!

- **From scratch:** [Overview](https://docs.djangoproject.com/en/5.2/intro/overview/) | [Installation](https://docs.djangoproject.com/en/5.2/intro/install/)
- **Tutorial:**
  - [Part 1: Requests and responses](https://docs.djangoproject.com/en/5.2/intro/tutorial01/)
  - [Part 2: Models and the admin site](https://docs.djangoproject.com/en/5.2/intro/tutorial02/)
  - [Part 3: Views and templates](https://docs.djangoproject.com/en/5.2/intro/tutorial03/)
  - [Part 4: Forms and generic views](https://docs.djangoproject.com/en/5.2/intro/tutorial04/)
  - [Part 5: Testing](https://docs.djangoproject.com/en/5.2/intro/tutorial05/)
  - [Part 6: Static files](https://docs.djangoproject.com/en/5.2/intro/tutorial06/)
  - [Part 7: Customizing the admin site](https://docs.djangoproject.com/en/5.2/intro/tutorial07/)
  - [Part 8: Adding third-party packages](https://docs.djangoproject.com/en/5.2/intro/tutorial08/)
- **Advanced Tutorials:**
  - [How to write reusable apps](https://docs.djangoproject.com/en/5.2/intro/reusable-apps/)
  - [Writing your first contribution to Django](https://docs.djangoproject.com/en/5.2/intro/contributing/)

## Getting Help

Having trouble? We’d like to help!

- Try the [FAQ](https://docs.djangoproject.com/en/5.2/faq/) – it’s got answers to many common questions.
- Looking for specific information? Try the [Index](https://docs.djangoproject.com/en/5.2/genindex/), [Module Index](https://docs.djangoproject.com/en/5.2/py-modindex/) or the [detailed table of contents](https://docs.djangoproject.com/en/5.2/contents/).
- Not found anything? See [FAQ: Getting Help](https://docs.djangoproject.com/en/5.2/faq/help/) for information on getting support and asking questions to the community.
- Report bugs with Django in our [ticket tracker](https://code.djangoproject.com/).

## How the Documentation is Organized

Django has a lot of documentation. A high-level overview of how it’s organized will help you know where to look for certain things:

- [Tutorials](https://docs.djangoproject.com/en/5.2/intro/) take you by the hand through a series of steps to create a web application. Start here if you’re new to Django or web application development. Also look at the “[First steps](#first-steps)”.
- [Topic guides](https://docs.djangoproject.com/en/5.2/topics/) discuss key topics and concepts at a fairly high level and provide useful background information and explanation.
- [Reference guides](https://docs.djangoproject.com/en/5.2/ref/) contain technical reference for APIs and other aspects of Django’s machinery. They describe how it works and how to use it but assume that you have a basic understanding of key concepts.
- [How-to guides](https://docs.djangoproject.com/en/5.2/howto/) are recipes. They guide you through the steps involved in addressing key problems and use-cases. They are more advanced than tutorials and assume some knowledge of how Django works.

## The Model Layer

Django provides an abstraction layer (the “models”) for structuring and manipulating the data of your web application. Learn more about it below:

- **Models:**
  - [Introduction to models](https://docs.djangoproject.com/en/5.2/topics/db/models/)
  - [Field types](https://docs.djangoproject.com/en/5.2/ref/models/fields/)
  - [Indexes](https://docs.djangoproject.com/en/5.2/ref/models/indexes/)
  - [Meta options](https://docs.djangoproject.com/en/5.2/ref/models/options/)
  - [Model class](https://docs.djangoproject.com/en/5.2/ref/models/class/)
- **QuerySets:**
  - [Making queries](https://docs.djangoproject.com/en/5.2/topics/db/queries/)
  - [QuerySet method reference](https://docs.djangoproject.com/en/5.2/ref/models/querysets/)
  - [Lookup expressions](https://docs.djangoproject.com/en/5.2/ref/models/lookups/)
- **Model instances:**
  - [Instance methods](https://docs.djangoproject.com/en/5.2/ref/models/instances/)
  - [Accessing related objects](https://docs.djangoproject.com/en/5.2/ref/models/relations/)
- **Migrations:**
  - [Introduction to Migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/)
  - [Operations reference](https://docs.djangoproject.com/en/5.2/ref/migration-operations/)
  - [SchemaEditor](https://docs.djangoproject.com/en/5.2/ref/schema-editor/)
  - [Writing migrations](https://docs.djangoproject.com/en/5.2/howto/writing-migrations/)
- **Advanced:**
  - [Managers](https://docs.djangoproject.com/en/5.2/topics/db/managers/)
  - [Raw SQL](https://docs.djangoproject.com/en/5.2/topics/db/sql/)
  - [Transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/)
  - [Aggregation](https://docs.djangoproject.com/en/5.2/topics/db/aggregation/)
  - [Search](https://docs.djangoproject.com/en/5.2/topics/db/search/)
  - [Custom fields](https://docs.djangoproject.com/en/5.2/howto/custom-model-fields/)
  - [Multiple databases](https://docs.djangoproject.com/en/5.2/topics/db/multi-db/)
  - [Custom lookups](https://docs.djangoproject.com/en/5.2/howto/custom-lookups/)
  - [Query Expressions](https://docs.djangoproject.com/en/5.2/ref/models/expressions/)
  - [Conditional Expressions](https://docs.djangoproject.com/en/5.2/ref/models/conditional-expressions/)
  - [Database Functions](https://docs.djangoproject.com/en/5.2/ref/models/database-functions/)
- **Other:**
  - [Supported databases](https://docs.djangoproject.com/en/5.2/ref/databases/)
  - [Legacy databases](https://docs.djangoproject.com/en/5.2/howto/legacy-databases/)
  - [Providing initial data](https://docs.djangoproject.com/en/5.2/howto/initial-data/)
  - [Optimize database access](https://docs.djangoproject.com/en/5.2/topics/db/optimization/)
  - [PostgreSQL specific features](https://docs.djangoproject.com/en/5.2/ref/contrib/postgres/)

## The View Layer

Django has the concept of “views” to encapsulate the logic responsible for processing a user’s request and for returning the response. Find all you need to know about views via the links below:

- **The basics:**
  - [URLconfs](https://docs.djangoproject.com/en/5.2/topics/http/urls/)
  - [View functions](https://docs.djangoproject.com/en/5.2/topics/http/views/)
  - [Shortcuts](https://docs.djangoproject.com/en/5.2/topics/http/shortcuts/)
  - [Decorators](https://docs.djangoproject.com/en/5.2/topics/http/decorators/)
  - [Asynchronous Support](https://docs.djangoproject.com/en/5.2/topics/async/)
- **Reference:**
  - [Built-in Views](https://docs.djangoproject.com/en/5.2/ref/views/)
  - [Request/response objects](https://docs.djangoproject.com/en/5.2/ref/request-response/)
  - [TemplateResponse objects](https://docs.djangoproject.com/en/5.2/ref/template-response/)
- **File uploads:**
  - [Overview](https://docs.djangoproject.com/en/5.2/topics/http/file-uploads/)
  - [File objects](https://docs.djangoproject.com/en/5.2/ref/files/file/)
  - [Storage API](https://docs.djangoproject.com/en/5.2/ref/files/storage/)
  - [Managing files](https://docs.djangoproject.com/en/5.2/topics/files/)
  - [Custom storage](https://docs.djangoproject.com/en/5.2/howto/custom-file-storage/)
- **Class-based views:**
  - [Overview](https://docs.djangoproject.com/en/5.2/topics/class-based-views/)
  - [Built-in display views](https://docs.djangoproject.com/en/5.2/topics/class-based-views/generic-display/)
  - [Built-in editing views](https://docs.djangoproject.com/en/5.2/topics/class-based-views/generic-editing/)
  - [Using mixins](https://docs.djangoproject.com/en/5.2/topics/class-based-views/mixins/)
  - [API reference](https://docs.djangoproject.com/en/5.2/ref/class-based-views/)
  - [Flattened index](https://docs.djangoproject.com/en/5.2/ref/class-based-views/flattened-index/)
- **Advanced:**
  - [Generating CSV](https://docs.djangoproject.com/en/5.2/howto/outputting-csv/)
  - [Generating PDF](https://docs.djangoproject.com/en/5.2/howto/outputting-pdf/)
- **Middleware:**
  - [Overview](https://docs.djangoproject.com/en/5.2/topics/http/middleware/)
  - [Built-in middleware classes](https://docs.djangoproject.com/en/5.2/ref/middleware/)

## The Template Layer

The template layer provides a designer-friendly syntax for rendering the information to be presented to the user. Learn how this syntax can be used by designers and how it can be extended by programmers:

- **The basics:**
  - [Overview](https://docs.djangoproject.com/en/5.2/topics/templates/)
- **For designers:**
  - [Language overview](https://docs.djangoproject.com/en/5.2/ref/templates/language/)
  - [Built-in tags and filters](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/)
  - [Humanization](https://docs.djangoproject.com/en/5.2/ref/contrib/humanize/)
- **For programmers:**
  - [Template API](https://docs.djangoproject.com/en/5.2/ref/templates/api/)
  - [Custom tags and filters](https://docs.djangoproject.com/en/5.2/howto/custom-template-tags/)
  - [Custom template backend](https://docs.djangoproject.com/en/5.2/howto/custom-template-backend/)

## Forms

Django provides a rich framework to facilitate the creation of forms and the manipulation of form data.

- **The basics:**
  - [Overview](https://docs.djangoproject.com/en/5.2/topics/forms/)
  - [Form API](https://docs.djangoproject.com/en/5.2/ref/forms/api/)
  - [Built-in fields](https://docs.djangoproject.com/en/5.2/ref/forms/fields/)
  - [Built-in widgets](https://docs.djangoproject.com/en/5.2/ref/forms/widgets/)
- **Advanced:**
  - [Forms for models](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/)
  - [Integrating media](https://docs.djangoproject.com/en/5.2/topics/forms/media/)
  - [Formsets](https://docs.djangoproject.com/en/5.2/topics/forms/formsets/)
  - [Customizing validation](https://docs.djangoproject.com/en/5.2/ref/forms/validation/)

## The Development Process

Learn about the various components and tools to help you in the development and testing of Django applications:

- **Settings:**
  - [Overview](https://docs.djangoproject.com/en/5.2/topics/settings/)
  - [Full list of settings](https://docs.djangoproject.com/en/5.2/ref/settings/)
- **Applications:**
  - [Overview](https://docs.djangoproject.com/en/5.2/ref/applications/)
- **Exceptions:**
  - [Overview](https://docs.djangoproject.com/en/5.2/ref/exceptions/)
- **django-admin and manage.py:**
  - [Overview](https://docs.djangoproject.com/en/5.2/ref/django-admin/)
  - [Adding custom commands](https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/)
- **Testing:**
  - [Introduction](https://docs.djangoproject.com/en/5.2/topics/testing/)
  - [Writing and running tests](https://docs.djangoproject.com/en/5.2/topics/testing/overview/)
  - [Included testing tools](https://docs.djangoproject.com/en/5.2/topics/testing/tools/)
  - [Advanced topics](https://docs.djangoproject.com/en/5.2/topics/testing/advanced/)
- **Deployment:**
  - [Overview](https://docs.djangoproject.com/en/5.2/howto/deployment/)
  - [WSGI servers](https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/)
  - [ASGI servers](https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/)
  - [Deploying static files](https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/)
  - [Tracking code errors by email](https://docs.djangoproject.com/en/5.2/howto/error-reporting/)
  - [Deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

## The Admin

Find all you need to know about the automated admin interface, one of Django’s most popular features:

- [Admin site](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/)
- [Admin actions](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/actions/)
- [Admin documentation generator](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/admindocs/)

## Security

Security is a topic of paramount importance in the development of web applications and Django provides multiple protection tools and mechanisms:

- [Security overview](https://docs.djangoproject.com/en/5.2/topics/security/)
- [Disclosed security issues in Django](https://docs.djangoproject.com/en/5.2/releases/security/)
- [Clickjacking protection](https://docs.djangoproject.com/en/5.2/ref/clickjacking/)
- [Cross Site Request Forgery protection](https://docs.djangoproject.com/en/5.2/ref/csrf/)
- [Cryptographic signing](https://docs.djangoproject.com/en/5.2/topics/signing/)
- [Security Middleware](https://docs.djangoproject.com/en/5.2/ref/middleware/#security-middleware)

## Internationalization and Localization

Django offers a robust internationalization and localization framework to assist you in the development of applications for multiple languages and world regions:

- [Overview](https://docs.djangoproject.com/en/5.2/topics/i18n/)
- [Internationalization](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/)
- [Localization](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/#how-to-create-language-files)
- [Localized web UI formatting and form input](https://docs.djangoproject.com/en/5.2/topics/i18n/formatting/)
- [Time zones](https://docs.djangoproject.com/en/5.2/topics/i18n/timezones/)

## Performance and Optimization

There are a variety of techniques and tools that can help get your code running more efficiently - faster, and using fewer system resources.

- [Performance and optimization overview](https://docs.djangoproject.com/en/5.2/topics/performance/)

## Geographic Framework

[GeoDjango](https://docs.djangoproject.com/en/5.2/ref/contrib/gis/) intends to be a world-class geographic web framework. Its goal is to make it as easy as possible to build GIS web applications and harness the power of spatially enabled data.

## Common Web Application Tools

Django offers multiple tools commonly needed in the development of web applications:

- **Authentication:**
  - [Overview](https://docs.djangoproject.com/en/5.2/topics/auth/)
  - [Using the authentication system](https://docs.djangoproject.com/en/5.2/topics/auth/default/)
  - [Password management](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/)
  - [Customizing authentication](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/)
  - [API Reference](https://docs.djangoproject.com/en/5.2/ref/contrib/auth/)
- [Caching](https://docs.djangoproject.com/en/5.2/topics/cache/)
- [Logging](https://docs.djangoproject.com/en/5.2/topics/logging/)
- [Sending emails](https://docs.djangoproject.com/en/5.2/topics/email/)
- [Syndication feeds (RSS/Atom)](https://docs.djangoproject.com/en/5.2/ref/contrib/syndication/)
- [Pagination](https://docs.djangoproject.com/en/5.2/topics/pagination/)
- [Messages framework](https://docs.djangoproject.com/en/5.2/ref/contrib/messages/)
- [Serialization](https://docs.djangoproject.com/en/5.2/topics/serialization/)
- [Sessions](https://docs.djangoproject.com/en/5.2/topics/http/sessions/)
- [Sitemaps](https://docs.djangoproject.com/en/5.2/ref/contrib/sitemaps/)
- [Static files management](https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/)
- [Data validation](https://docs.djangoproject.com/en/5.2/ref/validators/)

## Other Core Functionalities

Learn about some other core functionalities of the Django framework:

- [Conditional content processing](https://docs.djangoproject.com/en/5.2/topics/conditional-view-processing/)
- [Content types and generic relations](https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/)
- [Flatpages](https://docs.djangoproject.com/en/5.2/ref/contrib/flatpages/)
- [Redirects](https://docs.djangoproject.com/en/5.2/ref/contrib/redirects/)
- [Signals](https://docs.djangoproject.com/en/5.2/topics/signals/)
- [System check framework](https://docs.djangoproject.com/en/5.2/topics/checks/)
- [The sites framework](https://docs.djangoproject.com/en/5.2/ref/contrib/sites/)
- [Unicode in Django](https://docs.djangoproject.com/en/5.2/ref/unicode/)

## The Django Open-Source Project

Learn about the development process for the Django project itself and about how you can contribute:

- **Community:**
  - [Contributing to Django](https://docs.djangoproject.com/en/5.2/internals/contributing/)
  - [The release process](https://docs.djangoproject.com/en/5.2/internals/release-process/)
  - [Team organization](https://docs.djangoproject.com/en/5.2/internals/organization/)
  - [The Django source code repository](https://docs.djangoproject.com/en/5.2/internals/git/)
  - [Security policies](https://docs.djangoproject.com/en/5.2/internals/security/)
  - [Mailing lists and Forum](https://docs.djangoproject.com/en/5.2/internals/mailing-lists/)
- **Design philosophies:**
  - [Overview](https://docs.djangoproject.com/en/5.2/misc/design-philosophies/)
- **Documentation:**
  - [About this documentation](https://docs.djangoproject.com/en/5.2/internals/contributing/writing-documentation/)
- **Third-party distributions:**
  - [Overview](https://docs.djangoproject.com/en/5.2/misc/distributions/)
- **Django over time:**
  - [API stability](https://docs.djangoproject.com/en/5.2/misc/api-stability/)
  - [Release notes and upgrading instructions](https://docs.djangoproject.com/en/5.2/releases/)
  - [Deprecation Timeline](https://docs.djangoproject.com/en/5.2/internals/deprecation/)