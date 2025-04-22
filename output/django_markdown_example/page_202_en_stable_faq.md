# Django FAQ

## FAQ: General

- [Why does this project exist?](general/#why-does-this-project-exist)
- [What does “Django” mean, and how do you pronounce it?](general/#what-does-django-mean-and-how-do-you-pronounce-it)
- [Is Django stable?](general/#is-django-stable)
- [Does Django scale?](general/#does-django-scale)
- [Who’s behind this?](general/#who-s-behind-this)
- [How is Django licensed?](general/#how-is-django-licensed)
- [Why does Django include Python’s license file?](general/#why-does-django-include-python-s-license-file)
- [Which sites use Django?](general/#which-sites-use-django)
- [Django appears to be a MVC framework, but you call the Controller the “view”, and the View the “template”. How come you don’t use the standard names?](general/#django-appears-to-be-a-mvc-framework-but-you-call-the-controller-the-view-and-the-view-the-template-how-come-you-don-t-use-the-standard-names)
- [<Framework X> does <feature Y> – why doesn’t Django?](general/#framework-x-does-feature-y-why-doesn-t-django)
- [Why did you write all of Django from scratch, instead of using other Python libraries?](general/#why-did-you-write-all-of-django-from-scratch-instead-of-using-other-python-libraries)
- [Is Django a content-management-system (CMS)?](general/#is-django-a-content-management-system-cms)
- [How can I download the Django documentation to read it offline?](general/#how-can-i-download-the-django-documentation-to-read-it-offline)
- [How do I cite Django?](general/#how-do-i-cite-django)

## FAQ: Installation

- [How do I get started?](install/#how-do-i-get-started)
- [What are Django’s prerequisites?](install/#what-are-django-s-prerequisites)
- [What Python version can I use with Django?](install/#what-python-version-can-i-use-with-django)
- [What Python version should I use with Django?](install/#what-python-version-should-i-use-with-django)
- [Should I use the stable version or development version?](install/#should-i-use-the-stable-version-or-development-version)

## FAQ: Using Django

- [Why do I get an error about importing `DJANGO_SETTINGS_MODULE`?](usage/#why-do-i-get-an-error-about-importing-django-settings-module)
- [I can’t stand your template language. Do I have to use it?](usage/#i-can-t-stand-your-template-language-do-i-have-to-use-it)
- [Do I have to use your model/database layer?](usage/#do-i-have-to-use-your-model-database-layer)
- [How do I use image and file fields?](usage/#how-do-i-use-image-and-file-fields)
- [How do I make a variable available to all my templates?](usage/#how-do-i-make-a-variable-available-to-all-my-templates)

## FAQ: Getting Help

- [How do I do X? Why doesn’t Y work? Where can I go to get help?](help/#how-do-i-do-x-why-doesn-t-y-work-where-can-i-go-to-get-help)
- [Nobody answered my question! What should I do?](help/#nobody-answered-my-question-what-should-i-do)
- [I think I’ve found a bug! What should I do?](help/#i-think-i-ve-found-a-bug-what-should-i-do)
- [I think I’ve found a security problem! What should I do?](help/#i-think-i-ve-found-a-security-problem-what-should-i-do)

## FAQ: Databases and Models

- [How can I see the raw SQL queries Django is running?](models/#how-can-i-see-the-raw-sql-queries-django-is-running)
- [Can I use Django with a preexisting database?](models/#can-i-use-django-with-a-preexisting-database)
- [If I make changes to a model, how do I update the database?](models/#if-i-make-changes-to-a-model-how-do-i-update-the-database)
- [Do Django models support multiple-column primary keys?](models/#do-django-models-support-multiple-column-primary-keys)
- [Does Django support NoSQL databases?](models/#does-django-support-nosql-databases)
- [How do I add database-specific options to my CREATE TABLE statements, such as specifying MyISAM as the table type?](models/#how-do-i-add-database-specific-options-to-my-create-table-statements-such-as-specifying-myisam-as-the-table-type)

## FAQ: The Admin

- [I can’t log in. When I enter a valid username and password, it just brings up the login page again, with no error messages.](admin/#i-can-t-log-in-when-i-enter-a-valid-username-and-password-it-just-brings-up-the-login-page-again-with-no-error-messages)
- [I can’t log in. When I enter a valid username and password, it brings up the login page again, with a “Please enter a correct username and password” error.](admin/#i-can-t-log-in-when-i-enter-a-valid-username-and-password-it-brings-up-the-login-page-again-with-a-please-enter-a-correct-username-and-password-error)
- [How do I automatically set a field’s value to the user who last edited the object in the admin?](admin/#how-do-i-automatically-set-a-field-s-value-to-the-user-who-last-edited-the-object-in-the-admin)
- [How do I limit admin access so that objects can only be edited by the users who created them?](admin/#how-do-i-limit-admin-access-so-that-objects-can-only-be-edited-by-the-users-who-created-them)
- [My admin-site CSS and images showed up fine using the development server, but they’re not displaying when using mod_wsgi.](admin/#my-admin-site-css-and-images-showed-up-fine-using-the-development-server-but-they-re-not-displaying-when-using-mod-wsgi)
- [My “list_filter” contains a ManyToManyField, but the filter doesn’t display.](admin/#my-list-filter-contains-a-manytomanyfield-but-the-filter-doesn-t-display)
- [Some objects aren’t appearing in the admin.](admin/#some-objects-aren-t-appearing-in-the-admin)
- [How can I customize the functionality of the admin interface?](admin/#how-can-i-customize-the-functionality-of-the-admin-interface)
- [The dynamically-generated admin site is ugly! How can I change it?](admin/#the-dynamically-generated-admin-site-is-ugly-how-can-i-change-it)
- [What browsers are supported for using the admin?](admin/#what-browsers-are-supported-for-using-the-admin)
- [What assistive technologies are supported for using the admin?](admin/#what-assistive-technologies-are-supported-for-using-the-admin)

## FAQ: Contributing Code

- [How can I get started contributing code to Django?](contributing/#how-can-i-get-started-contributing-code-to-django)
- [I submitted a bug fix several weeks ago. Why are you ignoring my contribution?](contributing/#i-submitted-a-bug-fix-several-weeks-ago-why-are-you-ignoring-my-contribution)
- [When and how might I remind the team of a change I care about?](contributing/#when-and-how-might-i-remind-the-team-of-a-change-i-care-about)
- [But I’ve reminded you several times and you keep ignoring my contribution!](contributing/#but-i-ve-reminded-you-several-times-and-you-keep-ignoring-my-contribution)
- [I’m sure my ticket is absolutely 100% perfect, can I mark it as “Ready For Checkin” myself?](contributing/#i-m-sure-my-ticket-is-absolutely-100-perfect-can-i-mark-it-as-ready-for-checkin-myself)

## Troubleshooting

- [Problems running `django-admin`](troubleshooting/#problems-running-django-admin)
- [Miscellaneous](troubleshooting/#miscellaneous)