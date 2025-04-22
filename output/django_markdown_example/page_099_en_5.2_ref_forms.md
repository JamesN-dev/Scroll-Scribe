# Forms

Detailed form API reference. For introductory material, see the [Working with forms](https://docs.djangoproject.com/en/5.2/topics/forms/) topic guide.

## The Forms API

- [Bound and unbound forms](https://docs.djangoproject.com/en/5.2/ref/forms/api/#bound-and-unbound-forms)
- [Using forms to validate data](https://docs.djangoproject.com/en/5.2/ref/forms/api/#using-forms-to-validate-data)
- [Initial form values](https://docs.djangoproject.com/en/5.2/ref/forms/api/#initial-form-values)
- [Checking which form data has changed](https://docs.djangoproject.com/en/5.2/ref/forms/api/#checking-which-form-data-has-changed)
- [Accessing the fields from the form](https://docs.djangoproject.com/en/5.2/ref/forms/api/#accessing-the-fields-from-the-form)
- [Accessing “clean” data](https://docs.djangoproject.com/en/5.2/ref/forms/api/#accessing-clean-data)
- [Outputting forms as HTML](https://docs.djangoproject.com/en/5.2/ref/forms/api/#outputting-forms-as-html)
- [More granular output](https://docs.djangoproject.com/en/5.2/ref/forms/api/#more-granular-output)
- [Customizing `BoundField`](https://docs.djangoproject.com/en/5.2/ref/forms/api/#customizing-boundfield)
- [Binding uploaded files to a form](https://docs.djangoproject.com/en/5.2/ref/forms/api/#binding-uploaded-files-to-a-form)
- [Subclassing forms](https://docs.djangoproject.com/en/5.2/ref/forms/api/#subclassing-forms)
- [Prefixes for forms](https://docs.djangoproject.com/en/5.2/ref/forms/api/#prefixes-for-forms)

## Form fields

- [Core field arguments](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#core-field-arguments)
- [Checking if the field data has changed](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#checking-if-the-field-data-has-changed)
- [Built-in `Field` classes](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#built-in-field-classes)
- [Slightly complex built-in `Field` classes](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#slightly-complex-built-in-field-classes)
- [Fields which handle relationships](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#fields-which-handle-relationships)
- [Creating custom fields](https://docs.djangoproject.com/en/5.2/ref/forms/fields/#creating-custom-fields)

## Model Form Functions

- [`modelform_factory`](https://docs.djangoproject.com/en/5.2/ref/forms/models/#modelform-factory)
- [`modelformset_factory`](https://docs.djangoproject.com/en/5.2/ref/forms/models/#modelformset-factory)
- [`inlineformset_factory`](https://docs.djangoproject.com/en/5.2/ref/forms/models/#inlineformset-factory)

## Formset Functions

- [`formset_factory`](https://docs.djangoproject.com/en/5.2/ref/forms/formsets/#formset-factory)

## The form rendering API

- [The low-level render API](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#the-low-level-render-api)
- [Built-in-template form renderers](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#built-in-template-form-renderers)
- [Context available in formset templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#context-available-in-formset-templates)
- [Context available in form templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#context-available-in-form-templates)
- [Context available in field templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#context-available-in-field-templates)
- [Context available in widget templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#context-available-in-widget-templates)
- [Overriding built-in formset templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#overriding-built-in-formset-templates)
- [Overriding built-in form templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#overriding-built-in-form-templates)
- [Overriding built-in field templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#overriding-built-in-field-templates)
- [Overriding built-in widget templates](https://docs.djangoproject.com/en/5.2/ref/forms/renderers/#overriding-built-in-widget-templates)

## Widgets

- [Specifying widgets](https://docs.djangoproject.com/en/5.2/ref/forms/widgets/#specifying-widgets)
- [Setting arguments for widgets](https://docs.djangoproject.com/en/5.2/ref/forms/widgets/#setting-arguments-for-widgets)
- [Widgets inheriting from the `Select` widget](https://docs.djangoproject.com/en/5.2/ref/forms/widgets/#widgets-inheriting-from-the-select-widget)
- [Customizing widget instances](https://docs.djangoproject.com/en/5.2/ref/forms/widgets/#customizing-widget-instances)
- [Base widget classes](https://docs.djangoproject.com/en/5.2/ref/forms/widgets/#base-widget-classes)
- [Built-in widgets](https://docs.djangoproject.com/en/5.2/ref/forms/widgets/#built-in-widgets)

## Form and field validation

- [Raising `ValidationError`](https://docs.djangoproject.com/en/5.2/ref/forms/validation/#raising-validationerror)
- [Using validation in practice](https://docs.djangoproject.com/en/5.2/ref/forms/validation/#using-validation-in-practice)