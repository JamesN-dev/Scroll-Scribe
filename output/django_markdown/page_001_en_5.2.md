# Django documentation

Everything you need to know about Django.

## First steps

Are you new to Django or to programming? This is the place to start!

- **From scratch:** [Overview](intro/overview/) | [Installation](intro/install/)

- **Tutorial:** 
  - [Part 1: Requests and responses](intro/tutorial01/)
  - [Part 2: Models and the admin site](intro/tutorial02/)
  - [Part 3: Views and templates](intro/tutorial03/)
  - [Part 4: Forms and generic views](intro/tutorial04/)
  - [Part 5: Testing](intro/tutorial05/)
  - [Part 6: Static files](intro/tutorial06/)
  - [Part 7: Customizing the admin site](intro/tutorial07/)
  - [Part 8: Adding third-party packages](intro/tutorial08/)

- **Advanced Tutorials:** 
  - [How to write reusable apps](intro/reusable-apps/)
  - [Writing your first contribution to Django](intro/contributing/)

## Getting help

Having trouble? We'd like to help!

- Try the [FAQ](faq/) – it's got answers to many common questions.
- Looking for specific information? Try the [Index](genindex/), [Module Index](py-modindex/), or the [detailed table of contents](contents/).
- Not found anything? See [FAQ: Getting Help](faq/help/) for information on getting support and asking questions to the community.
- Report bugs with Django in our [ticket tracker](https://code.djangoproject.com/).

## How the documentation is organized

Django has a lot of documentation. A high-level overview of how it's organized will help you know where to look for certain things:

- [Tutorials](intro/) take you by the hand through a series of steps to create a web application. Start here if you're new to Django or web application development.
- [Topic guides](topics/) discuss key topics and concepts at a fairly high level and provide useful background information and explanation.
- [Reference guides](ref/) contain technical reference for APIs and other aspects of Django's machinery.
- [How-to guides](howto/) are recipes. They guide you through the steps involved in addressing key problems and use-cases.

## The model layer

Django provides an abstraction layer (the "models") for structuring and manipulating the data of your web application:

### Models
- [Introduction to models](topics/db/models/)
- [Field types](ref/models/fields/)
- [Indexes](ref/models/indexes/)
- [Meta options](ref/models/options/)
- [Model class](ref/models/class/)

### QuerySets
- [Making queries](topics/db/queries/)
- [QuerySet method reference](ref/models/querysets/)
- [Lookup expressions](ref/models/lookups/)

### Model Instances
- [Instance methods](ref/models/instances/)
- [Accessing related objects](ref/models/relations/)

### Migrations
- [Introduction to Migrations](topics/migrations/)
- [Operations reference](ref/migration-operations/)
- [SchemaEditor](ref/schema-editor/)
- [Writing migrations](howto/writing-migrations/)

### Advanced Database Topics
- [Managers](topics/db/managers/)
- [Raw SQL](topics/db/sql/)
- [Transactions](topics/db/transactions/)
- [Aggregation](topics/db/aggregation/)
- [Search](topics/db/search/)
- [Custom fields](howto/custom-model-fields/)
- [Multiple databases](topics/db/multi-db/)
- [Custom lookups](howto/custom-lookups/)

## The view layer

Django has the concept of "views" to encapsulate the logic responsible for processing a user's request and for returning the response:

### Basics
- [URLconfs](topics/http/urls/)
- [View functions](topics/http/views/)
- [Shortcuts](topics/http/shortcuts/)
- [Decorators](topics/http/decorators/)
- [Asynchronous Support](topics/async/)

### Class-based Views
- [Overview](topics/class-based-views/)
- [Built-in display views](topics/class-based-views/generic-display/)
- [Built-in editing views](topics/class-based-views/generic-editing/)
- [Using mixins](topics/class-based-views/mixins/)
- [API reference](ref/class-based-views/)

## And Much More!

The documentation continues with detailed sections on:
- The template layer
- Forms
- Authentication
- Security
- Internationalization
- Performance optimization
- Deployment
- Admin interface
- And many more core functionalities

For the full, detailed documentation, please visit the [Django documentation website](https://docs.djangoproject.com/).