# Design Philosophies

This document explains some of the fundamental philosophies Django’s developers have used in creating the framework. Its goal is to explain the past and guide the future.

## Overall

### Loose Coupling

A fundamental goal of Django’s stack is [loose coupling and tight cohesion](https://wiki.c2.com/?CouplingAndCohesion). The various layers of the framework shouldn’t “know” about each other unless absolutely necessary.

For example, the template system knows nothing about web requests, the database layer knows nothing about data display and the view system doesn’t care which template system a programmer uses.

Although Django comes with a full stack for convenience, the pieces of the stack are independent of another wherever possible.

### Less Code

Django apps should use as little code as possible; they should lack boilerplate. Django should take full advantage of Python’s dynamic capabilities, such as introspection.

### Quick Development

The point of a web framework in the 21st century is to make the tedious aspects of web development fast. Django should allow for incredibly quick web development.

### Don’t Repeat Yourself (DRY)

Every distinct concept and/or piece of data should live in one, and only one, place. Redundancy is bad. Normalization is good.

The framework, within reason, should deduce as much as possible from as little as possible.

See also: The [discussion of DRY on the Portland Pattern Repository](https://wiki.c2.com/?DontRepeatYourself)

### Explicit Is Better Than Implicit

This is a core Python principle listed in [**PEP 20**](https://peps.python.org/pep-0020/), and it means Django shouldn’t do too much “magic.” Magic shouldn’t happen unless there’s a really good reason for it. Magic is worth using only if it creates a huge convenience unattainable in other ways, and it isn’t implemented in a way that confuses developers who are trying to learn how to use the feature.

### Consistency

The framework should be consistent at all levels. Consistency applies to everything from low-level (the Python coding style used) to high-level (the “experience” of using Django).

## Models

### Explicit Is Better Than Implicit

Fields shouldn’t assume certain behaviors based solely on the name of the field. This requires too much knowledge of the system and is prone to errors. Instead, behaviors should be based on keyword arguments and, in some cases, on the type of the field.

### Include All Relevant Domain Logic

Models should encapsulate every aspect of an “object,” following Martin Fowler’s [Active Record](https://www.martinfowler.com/eaaCatalog/activeRecord.html) design pattern.

This is why both the data represented by a model and information about it (its human-readable name, options like default ordering, etc.) are defined in the model class; all the information needed to understand a given model should be stored *in* the model.

## Database API

The core goals of the database API are:

### SQL Efficiency

It should execute SQL statements as few times as possible, and it should optimize statements internally.

This is why developers need to call `save()` explicitly, rather than the framework saving things behind the scenes silently.

This is also why the `select_related()` `QuerySet` method exists. It’s an optional performance booster for the common case of selecting “every related object.”

### Terse, Powerful Syntax

The database API should allow rich, expressive statements in as little syntax as possible. It should not rely on importing other modules or helper objects.

Joins should be performed automatically, behind the scenes, when necessary.

Every object should be able to access every related object, systemwide. This access should work both ways.

### Option To Drop Into Raw SQL Easily, When Needed

The database API should realize it’s a shortcut but not necessarily an end-all-be-all. The framework should make it easy to write custom SQL – entire statements, or just custom `WHERE` clauses as custom parameters to API calls.

## URL Design

### Loose Coupling

URLs in a Django app should not be coupled to the underlying Python code. Tying URLs to Python function names is a Bad And Ugly Thing.

Along these lines, the Django URL system should allow URLs for the same app to be different in different contexts. For example, one site may put stories at `/stories/`, while another may use `/news/`.

### Infinite Flexibility

URLs should be as flexible as possible. Any conceivable URL design should be allowed.

### Encourage Best Practices

The framework should make it just as easy (or even easier) for a developer to design pretty URLs than ugly ones.

File extensions in web-page URLs should be avoided.

Vignette-style commas in URLs deserve severe punishment.

### Definitive URLs

Technically, `foo.com/bar` and `foo.com/bar/` are two different URLs, and search-engine robots (and some web traffic-analyzing tools) would treat them as separate pages. Django should make an effort to “normalize” URLs so that search-engine robots don’t get confused.

This is the reasoning behind the [`APPEND_SLASH`](../../ref/settings/#std-setting-APPEND_SLASH) setting.

## Template System

### Separate Logic From Presentation

We see a template system as a tool that controls presentation and presentation-related logic – and that’s it. The template system shouldn’t support functionality that goes beyond this basic goal.

### Discourage Redundancy

The majority of dynamic websites use some sort of common sitewide design – a common header, footer, navigation bar, etc. The Django template system should make it easy to store those elements in a single place, eliminating duplicate code.

This is the philosophy behind [template inheritance](../../ref/templates/language/#template-inheritance).

### Be Decoupled From HTML

The template system shouldn’t be designed so that it only outputs HTML. It should be equally good at generating other text-based formats, or just plain text.

### XML Should Not Be Used For Template Languages

Using an XML engine to parse templates introduces a whole new world of human error in editing templates – and incurs an unacceptable level of overhead in template processing.

### Assume Designer Competence

The template system shouldn’t be designed so that templates necessarily are displayed nicely in WYSIWYG editors such as Dreamweaver. That is too severe of a limitation and wouldn’t allow the syntax to be as nice as it is. Django expects template authors are comfortable editing HTML directly.

### Treat Whitespace Obviously

The template system shouldn’t do magic things with whitespace. If a template includes whitespace, the system should treat the whitespace as it treats text – just display it. Any whitespace that’s not in a template tag should be displayed.

### Don’t Invent A Programming Language

The goal is not to invent a programming language. The goal is to offer just enough programming-esque functionality, such as branching and looping, that is essential for making presentation-related decisions. The [Django Template Language (DTL)](../../topics/templates/#template-language-intro) aims to avoid advanced logic.

### Safety And Security

The template system, out of the box, should forbid the inclusion of malicious code – such as commands that delete database records.

This is another reason the template system doesn’t allow arbitrary Python code.

### Extensibility

The template system should recognize that advanced template authors may want to extend its technology.

This is the philosophy behind custom template tags and filters.

## Views

### Simplicity

Writing a view should be as simple as writing a Python function. Developers shouldn’t have to instantiate a class when a function will do.

### Use Request Objects

Views should have access to a request object – an object that stores metadata about the current request. The object should be passed directly to a view function, rather than the view function having to access the request data from a global variable. This makes it light, clean and easy to test views by passing in “fake” request objects.

### Loose Coupling

A view shouldn’t care about which template system the developer uses – or even whether a template system is used at all.

### Differentiate Between GET And POST

GET and POST are distinct; developers should explicitly use one or the other. The framework should make it easy to distinguish between GET and POST data.

## Cache Framework

The core goals of Django’s [cache framework](../../topics/cache/) are:

### Less Code

A cache should be as fast as possible. Hence, all framework code surrounding the cache backend should be kept to the absolute minimum, especially for `get()` operations.

### Consistency

The cache API should provide a consistent interface across the different cache backends.

### Extensibility

The cache API should be extensible at the application level based on the developer’s needs (for example, see [Cache key transformation](../../topics/cache/#cache-key-transformation)).