# FAQ: The admin

## I can’t log in. When I enter a valid username and password, it just brings up the login page again, with no error messages.

The login cookie isn’t being set correctly, because the domain of the cookie sent out by Django doesn’t match the domain in your browser. Try setting the [`SESSION_COOKIE_DOMAIN` setting](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-SESSION_COOKIE_DOMAIN) to match your domain. For example, if you’re going to “[https://www.example.com/admin/](https://www.example.com/admin/)” in your browser, set `SESSION_COOKIE_DOMAIN = 'www.example.com'`.

## I can’t log in. When I enter a valid username and password, it brings up the login page again, with a “Please enter a correct username and password” error.

If you’re sure your username and password are correct, make sure your user account has [`is_active`](https://docs.djangoproject.com/en/5.2/ref/contrib/auth/#django.contrib.auth.models.User.is_active) and [`is_staff`](https://docs.djangoproject.com/en/5.2/ref/contrib/auth/#django.contrib.auth.models.User.is_staff) set to True. The admin site only allows access to users with those two fields both set to True.

## How do I automatically set a field’s value to the user who last edited the object in the admin?

The [`ModelAdmin`](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin) class provides customization hooks that allow you to transform an object as it saved, using details from the request. By extracting the current user from the request, and customizing the [`save_model()`](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_model) hook, you can update an object to reflect the user that edited it. See [the documentation on ModelAdmin methods](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#model-admin-methods) for an example.

## How do I limit admin access so that objects can only be edited by the users who created them?

The [`ModelAdmin`](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin) class also provides customization hooks that allow you to control the visibility and editability of objects in the admin. Using the same trick of extracting the user from the request, the [`get_queryset()`](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_queryset) and [`has_change_permission()`](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.has_change_permission) can be used to control the visibility and editability of objects in the admin.

## My admin-site CSS and images showed up fine using the development server, but they’re not displaying when using mod_wsgi.

See [serving the admin files](https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/modwsgi/#serving-the-admin-files) in the “How to use Django with mod_wsgi” documentation.

## My “list_filter” contains a ManyToManyField, but the filter doesn’t display.

Django won’t bother displaying the filter for a `ManyToManyField` if there are no related objects.

For example, if your [`list_filter`](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter) includes [sites](https://docs.djangoproject.com/en/5.2/ref/contrib/sites/), and there are no sites in your database, it won’t display a “Site” filter. In that case, filtering by site would be meaningless.

## Some objects aren’t appearing in the admin.

Inconsistent row counts may be caused by missing foreign key values or a foreign key field incorrectly set to [`null=False`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.Field.null). If you have a record with a [`ForeignKey`](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey) pointing to a nonexistent object and that foreign key is included is [`list_display`](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display), the record will not be shown in the admin changelist because the Django model is declaring an integrity constraint that is not implemented at the database level.

## How can I customize the functionality of the admin interface?

You’ve got several options. If you want to piggyback on top of an add/change form that Django automatically generates, you can attach arbitrary JavaScript modules to the page via the model’s class Admin [js parameter](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#modeladmin-asset-definitions). That parameter is a list of URLs, as strings, pointing to JavaScript modules that will be included within the admin form via a `<script>` tag.

If you want more flexibility than is feasible by tweaking the auto-generated forms, feel free to write custom views for the admin. The admin is powered by Django itself, and you can write custom views that hook into the authentication system, check permissions and do whatever else they need to do.

If you want to customize the look-and-feel of the admin interface, read the next question.

## The dynamically-generated admin site is ugly! How can I change it?

We like it, but if you don’t agree, you can modify the admin site’s presentation by editing the CSS stylesheet and/or associated image files. The site is built using semantic HTML and plenty of CSS hooks, so any changes you’d like to make should be possible by editing the stylesheet.

## What browsers are supported for using the admin?

The admin provides a fully-functional experience to the recent versions of modern, web standards compliant browsers. On desktop this means Chrome, Edge, Firefox, Opera, Safari, and others.

On mobile and tablet devices, the admin provides a responsive experience for web standards compliant browsers. This includes the major browsers on both Android and iOS.

Depending on feature support, there *may* be minor stylistic differences between browsers. These are considered acceptable variations in rendering.

## What assistive technologies are supported for using the admin?

The admin is intended to be compatible with a wide range of assistive technologies, but there are currently many blockers. The support target is all latest versions of major assistive technologies, including Dragon, JAWS, NVDA, Orca, TalkBack, Voice Control, VoiceOver iOS, VoiceOver macOS, Windows Contrast Themes, ZoomText, and screen magnifiers.