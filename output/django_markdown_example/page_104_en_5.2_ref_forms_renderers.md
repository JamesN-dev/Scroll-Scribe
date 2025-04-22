# The Form Rendering API

Django’s form widgets are rendered using Django’s [template engines system](../../../topics/templates/).

The form rendering process can be customized at several levels:

- Widgets can specify custom template names.
- Forms and widgets can specify custom renderer classes.
- A widget’s template can be overridden by a project. (Reusable applications typically shouldn’t override built-in templates because they might conflict with a project’s custom templates.)

## The Low-Level Render API

The rendering of form templates is controlled by a customizable renderer class. A custom renderer can be specified by updating the [`FORM_RENDERER` setting](../../settings/#std-setting-FORM_RENDERER). It defaults to `'django.forms.renderers.DjangoTemplates'`.

By specifying a custom form renderer and overriding `form_template_name` you can adjust the default form markup across your project from a single place.

You can also provide a custom renderer per-form or per-widget by setting the `Form.default_renderer` attribute or by using the `renderer` argument of `Form.render()`, or `Widget.render()`.

Matching points apply to formset rendering. See [Using a formset in views and templates](../../../topics/forms/formsets/#formset-rendering) for discussion.

Use one of the [built-in template form renderers](#built-in-template-form-renderers) or implement your own. Custom renderers must implement a `render(template_name, context, request=None)` method. It should return a rendered template (as a string) or raise `TemplateDoesNotExist`.

### `BaseRenderer`

The base class for the built-in form renderers.

#### `form_template_name`

The default name of the template to use to render a form.

Defaults to `"django/forms/div.html"` template.

#### `formset_template_name`

The default name of the template to use to render a formset.

Defaults to `"django/forms/formsets/div.html"` template.

#### `field_template_name`

The default name of the template used to render a `BoundField`.

Defaults to `"django/forms/field.html"`

#### `bound_field_class`

New in Django 5.2.

The default class used to represent form fields across the project.

Defaults to `BoundField` class.

This can be customized further using `Form.bound_field_class` for per-form overrides, or `Field.bound_field_class` for per-field overrides.

#### `get_template(template_name)`

Subclasses must implement this method with the appropriate template finding logic.

#### `render(template_name, context, request=None)`

Renders the given template, or raises `TemplateDoesNotExist`.

## Built-In-Template Form Renderers

### `DjangoTemplates`

#### `DjangoTemplates`

This renderer uses a standalone `DjangoTemplates` engine (unconnected to what you might have configured in the `TEMPLATES` setting). It loads templates first from the built-in form templates directory in [django/forms/templates](https://github.com/django/django/blob/main/django/forms/templates) and then from the installed apps’ templates directories using the `app_directories` loader.

If you want to render templates with customizations from your `TEMPLATES` setting, such as context processors for example, use the `TemplatesSetting` renderer.

#### `DjangoDivFormRenderer`

**Deprecated since version 5.0.**

The alias of `DjangoTemplates`.

### `Jinja2`

#### `Jinja2`

This renderer is the same as the `DjangoTemplates` renderer except that it uses a `Jinja2` backend. Templates for the built-in widgets are located in [django/forms/jinja2](https://github.com/django/django/blob/main/django/forms/jinja2) and installed apps can provide templates in a `jinja2` directory.

To use this backend, all the forms and widgets in your project and its third-party apps must have Jinja2 templates. Unless you provide your own Jinja2 templates for widgets that don’t have any, you can’t use this renderer. For example, `django.contrib.admin` doesn’t include Jinja2 templates for its widgets due to their usage of Django template tags.

#### `Jinja2DivFormRenderer`

**Deprecated since version 5.0.**

The alias of `Jinja2`.

### `TemplatesSetting`

#### `TemplatesSetting`

This renderer gives you complete control of how form and widget templates are sourced. It uses `get_template()` to find templates based on what’s configured in the `TEMPLATES` setting.

Using this renderer along with the built-in templates requires either:

- `'django.forms'` in `INSTALLED_APPS` and at least one engine with `APP_DIRS=True`.
- Adding the built-in templates directory in `DIRS` of one of your template engines. To generate that path:

```python
import django
django.__path__[0] + "/forms/templates"  # or '/forms/jinja2'
```

Using this renderer requires you to make sure the form templates your project needs can be located.

## Context Available in Formset Templates

Formset templates receive a context from `BaseFormSet.get_context()`. By default, formsets receive a dictionary with the following values:

- `formset`: The formset instance.

## Context Available in Form Templates

Form templates receive a context from `Form.get_context()`. By default, forms receive a dictionary with the following values:

- `form`: The bound form.
- `fields`: All bound fields, except the hidden fields.
- `hidden_fields`: All hidden bound fields.
- `errors`: All non-field-related or hidden field-related form errors.

## Context Available in Field Templates

Field templates receive a context from `BoundField.get_context()`. By default, fields receive a dictionary with the following values:

- `field`: The `BoundField`.

## Context Available in Widget Templates

Widget templates receive a context from `Widget.get_context()`. By default, widgets receive a single value in the context, `widget`. This is a dictionary that contains values like:

- `name`
- `value`
- `attrs`
- `is_hidden`
- `template_name`

Some widgets add further information to the context. For instance, all widgets that subclass `Input` define `widget['type']` and `MultiWidget` defines `widget['subwidgets']` for looping purposes.

## Overriding Built-In Formset Templates

`BaseFormSet.template_name`

To override formset templates, you must use the `TemplatesSetting` renderer. Then overriding formset templates works [the same as](../../../howto/overriding-templates/) overriding any other template in your project.

## Overriding Built-In Form Templates

`Form.template_name`

To override form templates, you must use the `TemplatesSetting` renderer. Then overriding form templates works [the same as](../../../howto/overriding-templates/) overriding any other template in your project.

## Overriding Built-In Field Templates

`Field.template_name`

To override field templates, you must use the `TemplatesSetting` renderer. Then overriding field templates works [the same as](../../../howto/overriding-templates/) overriding any other template in your project.

## Overriding Built-In Widget Templates

Each widget has a `template_name` attribute with a value such as `input.html`. Built-in widget templates are stored in the `django/forms/widgets` path. You can provide a custom template for `input.html` by defining `django/forms/widgets/input.html`, for example. See [Built-in widgets](../widgets/#built-in-widgets) for the name of each widget’s template.

To override widget templates, you must use the `TemplatesSetting` renderer. Then overriding widget templates works [the same as](../../../howto/overriding-templates/) overriding any other template in your project.