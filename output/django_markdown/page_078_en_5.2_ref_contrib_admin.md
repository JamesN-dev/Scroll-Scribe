# The Django Admin Site

## Overview

The Django admin interface is a powerful tool for managing the content of your website. Django automatically discovers models and provides a ready-to-use interface for managing your data.

### Other Topics

*   ModelAdmin objects
*   InlineModelAdmin objects
*   Overriding admin templates
*   Theming support
*   AdminSite objects
*   LogEntry objects
*   Reversing admin URLs
*   The `display` decorator
*   The `staff_member_required` decorator

## `ModelAdmin` Objects

`ModelAdmin` classes define how a model should be displayed and managed in the admin interface.

### The `Register` Decorator

The `@admin.register` decorator is a convenient way to register `ModelAdmin` classes.

### Discovery Of Admin Files

Django automatically discovers `admin.py` files in your installed applications and registers the models defined in them.

### `ModelAdmin` Options

`ModelAdmin` classes can be customized using various options.

#### Custom Template Options

You can specify custom templates for various admin views.

### `ModelAdmin` Methods

`ModelAdmin` classes provide several methods that can be overridden to customize the admin interface.

#### Other Methods

Additional methods are available for further customization.

### `ModelAdmin` Asset Definitions

You can define CSS and JavaScript assets to be included in the admin interface.

#### JQuery

The Django admin interface uses jQuery.

### Adding Custom Validation To The Admin

You can add custom validation logic to the admin interface.

## `InlineModelAdmin` Objects

`InlineModelAdmin` classes allow you to edit related models on the same page as the parent model.

### `InlineModelAdmin` Options

`InlineModelAdmin` classes can be customized using various options.

### Working With A Model With Two Or More Foreign Keys To The Same Parent Model

You can use `InlineModelAdmin` to manage models with multiple foreign keys to the same parent model.

### Working With Many-To-Many Models

`InlineModelAdmin` can be used to manage many-to-many relationships.

### Working With Many-To-Many Intermediary Models

You can use `InlineModelAdmin` to manage many-to-many relationships with intermediary models.

### Using Generic Relations As An Inline

`InlineModelAdmin` can be used with generic relations.

## Overriding Admin Templates

You can override the default admin templates to customize the look and feel of the admin interface.

### Set Up Your Projects Admin Template Directories

Create `templates/admin` directories in your project and apps.

### Overriding Vs. Replacing An Admin Template

You can either override or replace an admin template.

### Templates Which May Be Overridden Per App Or Model

Some templates can be overridden on a per-app or per-model basis.

### Root And Login Templates

The root and login templates can be customized.

## Theming Support

The Django admin interface supports theming.

## `Extrabody` Block

The `extrabody` block allows you to add custom content to the `<body>` of admin pages.

## `AdminSite` Objects

The `AdminSite` class represents an admin site instance.

### `AdminSite` Attributes

*   `site_header`: The text to put at the top of each admin page.
*   `site_title`: The text to put at the end of each admin page’s `<title>`.
*   `site_url`: The URL for the “View site” link at the top of each admin page. By default, `site_url` is `/`. Set it to `None` to remove the link.
*   `index_title`: The text to put at the top of the admin index page.
*   `index_template`: Path to a custom template that will be used by the admin site main index view.
*   `app_index_template`: Path to a custom template that will be used by the admin site app index view.
*   `empty_value_display`: The string to use for displaying empty values in the admin site’s change list. Defaults to a dash.
*   `enable_nav_sidebar`: A boolean value that determines whether to show the navigation sidebar on larger screens. By default, it is set to `True`.
*   `final_catch_all_view`: A boolean value that determines whether to add a final catch-all view to the admin that redirects unauthenticated users to the login page. By default, it is set to `True`.

    > **Warning**
    > Setting this to `False` is not recommended as the view protects against a potential model enumeration privacy issue.

*   `login_template`: Path to a custom template that will be used by the admin site login view.
*   `login_form`: Subclass of [`AuthenticationForm`](../../../topics/auth/default/#django.contrib.auth.forms.AuthenticationForm) that will be used by the admin site login view.
*   `logout_template`: Path to a custom template that will be used by the admin site logout view.
*   `password_change_template`: Path to a custom template that will be used by the admin site password change view.
*   `password_change_done_template`: Path to a custom template that will be used by the admin site password change done view.

### `AdminSite` Methods

*   `each_context(request)`

    Returns a dictionary of variables to put in the template context for every page in the admin site.
    Includes the following variables and values by default:

    *   `site_header`: [`AdminSite.site_header`](#django.contrib.admin.AdminSite.site_header)
    *   `site_title`: [`AdminSite.site_title`](#django.contrib.admin.AdminSite.site_title)
    *   `site_url`: [`AdminSite.site_url`](#django.contrib.admin.AdminSite.site_url)
    *   `has_permission`: [`AdminSite.has_permission()`](#django.contrib.admin.AdminSite.has_permission)
    *   `available_apps`: a list of applications from the [application registry](../../applications/) available for the current user. Each entry in the list is a dict representing an application with the following keys:

        *   `app_label`: the application label
        *   `app_url`: the URL of the application index in the admin
        *   `has_module_perms`: a boolean indicating if displaying and accessing of the module’s index page is permitted for the current user
        *   `models`: a list of the models available in the application

        Each model is a dict with the following keys:

        *   `model`: the model class
        *   `object_name`: class name of the model
        *   `name`: plural name of the model
        *   `perms`: a `dict` tracking `add`, `change`, `delete`, and `view` permissions
        *   `admin_url`: admin changelist URL for the model
        *   `add_url`: admin URL to add a new model instance
    *   `is_popup`: whether the current page is displayed in a popup window
    *   `is_nav_sidebar_enabled`: [`AdminSite.enable_nav_sidebar`](#django.contrib.admin.AdminSite.enable_nav_sidebar)
    *   `log_entries`: [`AdminSite.get_log_entries()`](#django.contrib.admin.AdminSite.get_log_entries)
*   `get_app_list(request, app_label=None)`

    Returns a list of applications from the [application registry](../../applications/) available for the current user. You can optionally pass an `app_label` argument to get details for a single app. Each entry in the list is a dictionary representing an application with the following keys:

    *   `app_label`: the application label
    *   `app_url`: the URL of the application index in the admin
    *   `has_module_perms`: a boolean indicating if displaying and accessing of the module’s index page is permitted for the current user
    *   `models`: a list of the models available in the application
    *   `name`: name of the application

    Each model is a dictionary with the following keys:

    *   `model`: the model class
    *   `object_name`: class name of the model
    *   `name`: plural name of the model
    *   `perms`: a `dict` tracking `add`, `change`, `delete`, and `view` permissions
    *   `admin_url`: admin changelist URL for the model
    *   `add_url`: admin URL to add a new model instance

    Lists of applications and models are sorted alphabetically by their names. You can override this method to change the default order on the admin index page.
*   `has_permission(request)`

    Returns `True` if the user for the given `HttpRequest` has permission to view at least one page in the admin site. Defaults to requiring both [`User.is_active`](../auth/#django.contrib.auth.models.User.is_active) and [`User.is_staff`](../auth/#django.contrib.auth.models.User.is_staff) to be `True`.
*   `register(model_or_iterable, admin_class=None, **options)`

    Registers the given model class (or iterable of classes) with the given `admin_class`. `admin_class` defaults to [`ModelAdmin`](#django.contrib.admin.ModelAdmin) (the default admin options). If keyword arguments are given – e.g. `list_display` – they’ll be applied as options to the admin class.

    Raises [`ImproperlyConfigured`](../../exceptions/#django.core.exceptions.ImproperlyConfigured) if a model is abstract. and `django.contrib.admin.exceptions.AlreadyRegistered` if a model is already registered.
*   `unregister(model_or_iterable)`

    Unregisters the given model class (or iterable of classes).

    Raises `django.contrib.admin.exceptions.NotRegistered` if a model isn’t already registered.
*   `get_model_admin(model)`

    Returns an admin class for the given model class. Raises `django.contrib.admin.exceptions.NotRegistered` if a model isn’t registered.
*   `get_log_entries(request)`

    Returns a queryset for the related [`LogEntry`](#django.contrib.admin.models.LogEntry) instances, shown on the site index page. This method can be overridden to filter the log entries by other criteria.

### Hooking `AdminSite` Instances Into Your Urlconf

The last step in setting up the Django admin is to hook your `AdminSite` instance into your URLconf. Do this by pointing a given URL at the `AdminSite.urls` method. It is not necessary to use [`include()`](../../urls/#django.urls.include).

In this example, we register the default `AdminSite` instance `django.contrib.admin.site` at the URL `/admin/`

```python
# urls.py
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

### Customizing The `AdminSite` Class

If you’d like to set up your own admin site with custom behavior, you’re free to subclass `AdminSite` and override or add anything you like. Then, create an instance of your `AdminSite` subclass (the same way you’d instantiate any other Python class) and register your models and `ModelAdmin` subclasses with it instead of with the default site. Finally, update `myproject/urls.py` to reference your [`AdminSite`](#django.contrib.admin.AdminSite) subclass.

```python
# myapp/admin.py
from django.contrib import admin
from .models import MyModel

class MyAdminSite(admin.AdminSite):
    site_header = "Monty Python administration"

admin_site = MyAdminSite(name="myadmin")
admin_site.register(MyModel)
```

```python
# myproject/urls.py
from django.urls import path
from myapp.admin import admin_site

urlpatterns = [
    path("myadmin/", admin_site.urls),
]
```

Note that you may not want autodiscovery of `admin` modules when using your own `AdminSite` instance since you will likely be importing all the per-app `admin` modules in your `myproject.admin` module. This means you need to put `'django.contrib.admin.apps.SimpleAdminConfig'` instead of `'django.contrib.admin'` in your [`INSTALLED_APPS`](../../settings/#std-setting-INSTALLED_APPS) setting.

### Overriding The Default Admin Site

You can override the default `django.contrib.admin.site` by setting the [`default_site`](#django.contrib.admin.apps.SimpleAdminConfig.default_site) attribute of a custom `AppConfig` to the dotted import path of either a `AdminSite` subclass or a callable that returns a site instance.

```python
# myproject/admin.py
from django.contrib import admin

class MyAdminSite(admin.AdminSite):
    ...
```

```python
# myproject/apps.py
from django.contrib.admin.apps import AdminConfig

class MyAdminConfig(AdminConfig):
    default_site = "myproject.admin.MyAdminSite"
```

```python
# myproject/settings.py
INSTALLED_APPS = [
    # ...
    "myproject.apps.MyAdminConfig",  # replaces 'django.contrib.admin'
    # ...
]
```

### Multiple Admin Sites In The Same Urlconf

You can create multiple instances of the admin site on the same Django-powered website. Create multiple instances of `AdminSite` and place each one at a different URL.

In this example, the URLs `/basic-admin/` and `/advanced-admin/` feature separate versions of the admin site – using the `AdminSite` instances `myproject.admin.basic_site` and `myproject.admin.advanced_site`, respectively:

```python
# urls.py
from django.urls import path
from myproject.admin import advanced_site, basic_site

urlpatterns = [
    path("basic-admin/", basic_site.urls),
    path("advanced-admin/", advanced_site.urls),
]
```

`AdminSite` instances take a single argument to their constructor, their name, which can be anything you like. This argument becomes the prefix to the URL names for the purposes of [reversing them](#admin-reverse-urls). This is only necessary if you are using more than one `AdminSite`.

### Adding Views To Admin Sites

Just like [`ModelAdmin`](#django.contrib.admin.ModelAdmin), [`AdminSite`](#django.contrib.admin.AdminSite) provides a [`get_urls()`](#django.contrib.admin.ModelAdmin.get_urls) method that can be overridden to define additional views for the site. To add a new view to your admin site, extend the base [`get_urls()`](#django.contrib.admin.ModelAdmin.get_urls) method to include a pattern for your new view.

> **Note**
> Any view you render that uses the admin templates, or extends the base admin template, should set `request.current_app` before rendering the template. It should be set to either `self.name` if your view is on an `AdminSite` or `self.admin_site.name` if your view is on a `ModelAdmin`.

### Adding A Password Reset Feature

You can add a password reset feature to the admin site by adding a few lines to your URLconf. Specifically, add these four patterns:

```python
from django.contrib import admin
from django.contrib.auth import views as auth_views

path(
    "admin/password_reset/",
    auth_views.PasswordResetView.as_view(
        extra_context={"site_header": admin.site.site_header}
    ),
    name="admin_password_reset",
),
path(
    "admin/password_reset/done/",
    auth_views.PasswordResetDoneView.as_view(
        extra_context={"site_header": admin.site.site_header}
    ),
    name="password_reset_done",
),
path(
    "reset/<uidb64>/<token>/",
    auth_views.PasswordResetConfirmView.as_view(
        extra_context={"site_header": admin.site.site_header}
    ),
    name="password_reset_confirm",
),
path(
    "reset/done/",
    auth_views.PasswordResetCompleteView.as_view(
        extra_context={"site_header": admin.site.site_header}
    ),
    name="password_reset_complete",
),
```

(This assumes you’ve added the admin at `admin/` and requires that you put the URLs starting with `^admin/` before the line that includes the admin app itself).

The presence of the `admin_password_reset` named URL will cause a “forgotten your password?” link to appear on the default admin log-in page under the password box.

## `LogEntry` Objects

The `LogEntry` class tracks additions, changes, and deletions of objects done through the admin interface.

### `LogEntry` Attributes

*   `action_time`: The date and time of the action.
*   `user`: The user (an [`AUTH_USER_MODEL`](../../settings/#std-setting-AUTH_USER_MODEL) instance) who performed the action.
*   `content_type`: The [`ContentType`](../contenttypes/#django.contrib.contenttypes.models.ContentType) of the modified object.
*   `object_id`: The textual representation of the modified object’s primary key.
*   `object_repr`: The object`s `repr()` after the modification.
*   `action_flag`: The type of action logged: `ADDITION`, `CHANGE`, `DELETION`.

    For example, to get a list of all additions done through the admin:

    ```python
    from django.contrib.admin.models import ADDITION, LogEntry

    LogEntry.objects.filter(action_flag=ADDITION)
    ```
*   `change_message`: The detailed description of the modification. In the case of an edit, for example, the message contains a list of the edited fields. The Django admin site formats this content as a JSON structure, so that [`get_change_message()`](#django.contrib.admin.models.LogEntry.get_change_message) can recompose a message translated in the current user language. Custom code might set this as a plain string though. You are advised to use the [`get_change_message()`](#django.contrib.admin.models.LogEntry.get_change_message) method to retrieve this value instead of accessing it directly.

### `LogEntry` Methods

*   `get_edited_object()`

    A shortcut that returns the referenced object.
*   `get_change_message()`

    Formats and translates [`change_message`](#django.contrib.admin.models.LogEntry.change_message) into the current user language. Messages created before Django 1.10 will always be displayed in the language in which they were logged.

## Reversing Admin Urls

When an [`AdminSite`](#django.contrib.admin.AdminSite) is deployed, the views provided by that site are accessible using Django’s [URL reversing system](../../../topics/http/urls/#naming-url-patterns).

The [`AdminSite`](#django.contrib.admin.AdminSite) provides the following named URL patterns:

| Page                    | URL name              | Parameters                               |
| :---------------------- | :-------------------- | :--------------------------------------- |
| Index                   | `index`               |                                          |
| Login                   | `login`               |                                          |
| Logout                  | `logout`              |                                          |
| Password change         | `password_change`     |                                          |
| Password change done    | `password_change_done`|                                          |
| i18n JavaScript         | `jsi18n`              |                                          |
| Application index page  | `app_list`            | `app_label`                              |
| Redirect to object’s page | `view_on_site`        | `content_type_id`, `object_id`           |

Each [`ModelAdmin`](#django.contrib.admin.ModelAdmin) instance provides an additional set of named URLs:

| Page        | URL name                                  | Parameters  |
| :---------- | :---------------------------------------- | :---------- |
| Changelist  | `{{ app_label }}_{{ model_name }}_changelist` |             |
| Add         | `{{ app_label }}_{{ model_name }}_add`        |             |
| History     | `{{ app_label }}_{{ model_name }}_history`    | `object_id` |
| Delete      | `{{ app_label }}_{{ model_name }}_delete`     | `object_id` |
| Change      | `{{ app_label }}_{{ model_name }}_change`     | `object_id` |

The `UserAdmin` provides a named URL:

| Page            | URL name                      | Parameters |
| :-------------- | :---------------------------- | :--------- |
| Password change | `auth_user_password_change` | `user_id`  |

These named URLs are registered with the application namespace `admin`, and with an instance namespace corresponding to the name of the Site instance.

So - if you wanted to get a reference to the Change view for a particular `Choice` object (from the polls application) in the default admin, you would call:

```python
>>> from django.urls import reverse
>>> c = Choice.objects.get(...)
>>> change_url = reverse("admin:polls_choice_change", args=(c.id,))
```

This will find the first registered instance of the admin application (whatever the instance name), and resolve to the view for changing `poll.Choice` instances in that instance.

If you want to find a URL in a specific admin instance, provide the name of that instance as a `current_app` hint to the reverse call. For example, if you specifically wanted the admin view from the admin instance named `custom`, you would need to call:

```python
>>> change_url = reverse("admin:polls_choice_change", args=(c.id,), current_app="custom")
```

For more details, see the documentation on [reversing namespaced URLs](../../../topics/http/urls/#topics-http-reversing-url-namespaces).

To allow easier reversing of the admin urls in templates, Django provides an `admin_urlname` filter which takes an action as argument:

```html
{% load admin_urls %}
<a href="{% url opts|admin_urlname:'add' %}">Add user</a>
<a href="{% url opts|admin_urlname:'delete' user.pk %}">Delete this user</a>
```

The action in the examples above match the last part of the URL names for [`ModelAdmin`](#django.contrib.admin.ModelAdmin) instances described above. The `opts` variable can be any object which has an `app_label` and `model_name` attributes and is usually supplied by the admin views for the current model.

## The `Display` Decorator

```
display(*, boolean=None, ordering=None, description=None, empty_value=None)
```

This decorator can be used for setting specific attributes on custom display functions that can be used with [`list_display`](#django.contrib.admin.ModelAdmin.list_display) or [`readonly_fields`](#django.contrib.admin.ModelAdmin.readonly_fields):

```python
@admin.display(
    boolean=True,
    ordering="-publish_date",
    description="Is Published?",
)
def is_published(self, obj):
    return obj.publish_date is not None
```

This is equivalent to setting some attributes (with the original, longer names) on the function directly:

```python
def is_published(self, obj):
    return obj.publish_date is not None

is_published.boolean = True
is_published.admin_order_field = "-publish_date"
is_published.short_description = "Is Published?"
```

Also note that the ` empty_value` decorator parameter maps to the `empty_value_display` attribute assigned directly to the function. It cannot be used in conjunction with `boolean` – they are mutually exclusive.

Use of this decorator is not compulsory to make a display function, but it can be useful to use it without arguments as a marker in your source to identify the purpose of the function:

```python
@admin.display
def published_year(self, obj):
    return obj.publish_date.year
```

In this case it will add no attributes to the function.

## The `Staff_Member_Required` Decorator

```
staff_member_required(redirect_field_name='next', login_url='admin:login')
```

This decorator is used on the admin views that require authorization. A view decorated with this function will have the following behavior:

*   If the user is logged in, is a staff member (`User.is_staff=True`), and is active (`User.is_active=True`), execute the view normally.
*   Otherwise, the request will be redirected to the URL specified by the `login_url` parameter, with the originally requested path in a query string variable specified by `redirect_field_name`. For example: `/admin/login/?next=/admin/polls/question/3/`.

Example usage:

```python
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def my_view(request):
    ...
```