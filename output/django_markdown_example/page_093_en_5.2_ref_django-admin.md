# Django-admin and manage.py

`django-admin` is Django’s command-line utility for administrative tasks. This document outlines all it can do.

In addition, `manage.py` is automatically created in each Django project. It does the same thing as `django-admin` but also sets the `DJANGO_SETTINGS_MODULE` environment variable so that it points to your project’s `settings.py` file.

The `django-admin` script should be on your system path if you installed Django via `pip`. If it’s not in your path, ensure you have your virtual environment activated.

Generally, when working on a single Django project, it’s easier to use `manage.py` than `django-admin`. If you need to switch between multiple Django settings files, use `django-admin` with `DJANGO_SETTINGS_MODULE` or the `--settings` command line option.

The command-line examples throughout this document use `django-admin` to be consistent, but any example can use `manage.py` or `python -m django` just as well.

## Usage

```bash
$ django-admin <command> [options]
$ manage.py <command> [options]
$ python -m django <command> [options]
```

```powershell
...> django-admin <command> [options]
...> manage.py <command> [options]
...> py -m django <command> [options]
```

`command` should be one of the commands listed in this document. `options`, which is optional, should be zero or more of the options available for the given command.

### Getting runtime help

- `django-admin help`

  Run `django-admin help` to display usage information and a list of the commands provided by each application.

- `django-admin help --commands`

  Run `django-admin help --commands` to display a list of all available commands.

- `django-admin help <command>`

  Run `django-admin help <command>` to display a description of the given command and a list of its available options.

### App names

Many commands take a list of “app names.” An “app name” is the basename of the package containing your models. For example, if your `INSTALLED_APPS` contains the string `'mysite.blog'`, the app name is `blog`.

### Determining the version

- `django-admin version`

  Run `django-admin version` to display the current Django version.

  The output follows the schema described in [PEP 440](https://peps.python.org/pep-0440/):

  ```plaintext
  1.4.dev17026 1.4a1 1.4
  ```

### Displaying debug output

Use `--verbosity`, where it is supported, to specify the amount of notification and debug information that `django-admin` prints to the console.

## Available commands

### `check`

- `django-admin check [app_label [app_label ...]]`

  Uses the [system check framework](../../topics/checks/) to inspect the entire Django project for common problems.

  By default, all apps will be checked. You can check a subset of apps by providing a list of app labels as arguments:

  ```bash
  django-admin check auth admin myapp
  ```

- `--tag TAGS, -t TAGS`

  The system check framework performs many different types of checks that are [categorized with tags](../../topics/checks/#system-check-builtin-tags). You can use these tags to restrict the checks performed to just those in a particular category. For example, to perform only models and compatibility checks, run:

  ```bash
  django-admin check --tag models --tag compatibility
  ```

- `--database DATABASE`

  Specifies the database to run checks requiring database access:

  ```bash
  django-admin check --database default --database other
  ```

  By default, these checks will not be run.

- `--list-tags`

  Lists all available tags.

- `--deploy`

  Activates some additional checks that are only relevant in a deployment setting.

  You can use this option in your local development environment, but since your local development settings module may not have many of your production settings, you will probably want to point the `check` command at a different settings module, either by setting the `DJANGO_SETTINGS_MODULE` environment variable, or by passing the `--settings` option:

  ```bash
  django-admin check --deploy --settings=production_settings
  ```

  Or you could run it directly on a production or staging deployment to verify that the correct settings are in use (omitting `--settings`). You could even make it part of your integration test suite.

- `--fail-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}`

  Specifies the message level that will cause the command to exit with a non-zero status. Default is `ERROR`.

### `compilemessages`

- `django-admin compilemessages`

  Compiles `.po` files created by `makemessages` to `.mo` files for use with the built-in gettext support. See [Internationalization and localization](../../topics/i18n/).

- `--locale LOCALE, -l LOCALE`

  Specifies the locale(s) to process. If not provided, all locales are processed.

- `--exclude EXCLUDE, -x EXCLUDE`

  Specifies the locale(s) to exclude from processing. If not provided, no locales are excluded.

- `--use-fuzzy, -f`

  Includes [fuzzy translations](https://www.gnu.org/software/gettext/manual/html_node/Fuzzy-Entries.html) into compiled files.

  Example usage:

  ```bash
  django-admin compilemessages --locale=pt_BR
  django-admin compilemessages --locale=pt_BR --locale=fr -f
  django-admin compilemessages -l pt_BR
  django-admin compilemessages -l pt_BR -l fr --use-fuzzy
  django-admin compilemessages --exclude=pt_BR
  django-admin compilemessages --exclude=pt_BR --exclude=fr
  django-admin compilemessages -x pt_BR
  django-admin compilemessages -x pt_BR -x fr
  ```

- `--ignore PATTERN, -i PATTERN`

  Ignores directories matching the given [glob](https://docs.python.org/3/library/glob.html#module-glob)-style pattern. Use multiple times to ignore more.

  Example usage:

  ```bash
  django-admin compilemessages --ignore=cache --ignore=outdated/*/locale
  ```

### `createcachetable`

- `django-admin createcachetable`

  Creates the cache tables for use with the database cache backend using the information from your settings file. See [Django’s cache framework](../../topics/cache/) for more information.

- `--database DATABASE`

  Specifies the database in which the cache table(s) will be created. Defaults to `default`.

- `--dry-run`

  Prints the SQL that would be run without actually running it, so you can customize it or use the migrations framework.

### `dbshell`

- `django-admin dbshell`

  Runs the command-line client for the database engine specified in your `ENGINE` setting, with the connection parameters specified in your `USER`, `PASSWORD`, etc., settings.

  - For PostgreSQL, this runs the `psql` command-line client.
  - For MySQL, this runs the `mysql` command-line client.
  - For SQLite, this runs the `sqlite3` command-line client.
  - For Oracle, this runs the `sqlplus` command-line client.

  This command assumes the programs are on your `PATH` so that a call to the program name (`psql`, `mysql`, `sqlite3`, `sqlplus`) will find the program in the right place. There’s no way to specify the location of the program manually.

- `--database DATABASE`

  Specifies the database onto which to open a shell. Defaults to `default`.

- `-- ARGUMENTS`

  Any arguments following a `--` divider will be passed on to the underlying command-line client. For example, with PostgreSQL you can use the `psql` command’s `-c` flag to execute a raw SQL query directly:

  ```bash
  $ django-admin dbshell -- -c 'select current_user'
  current_user
  --------------
  postgres
  (1 row)
  ```

  ```powershell
  ...> django-admin dbshell -- -c 'select current_user'
  current_user
  --------------
  postgres
  (1 row)
  ```

  On MySQL/MariaDB, you can do this with the `mysql` command’s `-e` flag:

  ```bash
  $ django-admin dbshell -- -e "select user()"
  +----------------------+
  | user()               |
  +----------------------+
  | djangonaut@localhost |
  +----------------------+
  ```

  ```powershell
  ...> django-admin dbshell -- -e "select user()"
  +----------------------+
  | user()               |
  +----------------------+
  | djangonaut@localhost |
  +----------------------+
  ```

  **Note**

  Be aware that not all options set in the `OPTIONS` part of your database configuration in `DATABASES` are passed to the command-line client, e.g. `'isolation_level'`.

### `diffsettings`

- `django-admin diffsettings`

  Displays differences between the current settings file and Django’s default settings (or another settings file specified by `--default`).

  Settings that don’t appear in the defaults are followed by `"###"`. For example, the default settings don’t define `ROOT_URLCONF`, so `ROOT_URLCONF` is followed by `"###"` in the output of `diffsettings`.

- `--all`

  Displays all settings, even if they have Django’s default value. Such settings are prefixed by `"###"`.

- `--default MODULE`

  The settings module to compare the current settings against. Leave empty to compare against Django’s default settings.

- `--output {hash,unified}`

  Specifies the output format. Available values are `hash` and `unified`. `hash` is the default mode that displays the output that’s described above. `unified` displays the output similar to `diff -u`. Default settings are prefixed with a minus sign, followed by the changed setting prefixed with a plus sign.

### `dumpdata`

- `django-admin dumpdata [app_label[.ModelName] [app_label[.ModelName] ...]]`

  Outputs to standard output all data in the database associated with the named application(s).

  If no application name is provided, all installed applications will be dumped.

  The output of `dumpdata` can be used as input for `loaddata`.

  When result of `dumpdata` is saved as a file, it can serve as a [fixture](../../topics/db/fixtures/#fixtures-explanation) for [tests](../../topics/testing/tools/#topics-testing-fixtures) or as an [initial data](../../howto/initial-data/#initial-data-via-fixtures).

  Note that `dumpdata` uses the default manager on the model for selecting the records to dump. If you’re using a [custom manager](../../topics/db/managers/#custom-managers) as the default manager and it filters some of the available records, not all of the objects will be dumped.

- `--all, -a`

  Uses Django’s base manager, dumping records which might otherwise be filtered or modified by a custom manager.

- `--format FORMAT`

  Specifies the serialization format of the output. Defaults to JSON. Supported formats are listed in [Serialization formats](../../topics/serialization/#serialization-formats).

- `--indent INDENT`

  Specifies the number of indentation spaces to use in the output. Defaults to `None` which displays all data on single line.

- `--exclude EXCLUDE, -e EXCLUDE`

  Prevents specific applications or models (specified in the form of `app_label.ModelName`) from being dumped. If you specify a model name, then only that model will be excluded, rather than the entire application. You can also mix application names and model names.

  If you want to exclude multiple applications, pass `--exclude` more than once:

  ```bash
  django-admin dumpdata --exclude=auth --exclude=contenttypes
  ```

- `--database DATABASE`

  Specifies the database from which data will be dumped. Defaults to `default`.

- `--natural-foreign`

  Uses the `natural_key()` model method to serialize any foreign key and many-to-many relationship to objects of the type that defines the method. If you’re dumping `contrib.auth` `Permission` objects or `contrib.contenttypes` `ContentType` objects, you should probably use this flag. See the [natural keys](../../topics/serialization/#topics-serialization-natural-keys) documentation for more details on this and the next option.

- `--natural-primary`

  Omits the primary key in the serialized data of this object since it can be calculated during deserialization.

- `--pks PRIMARY_KEYS`

  Outputs only the objects specified by a comma separated list of primary keys. This is only available when dumping one model. By default, all the records of the model are output.

- `--output OUTPUT, -o OUTPUT`

  Specifies a file to write the serialized data to. By default, the data goes to standard output.

  When this option is set and `--verbosity` is greater than 0 (the default), a progress bar is shown in the terminal.

  #### Fixtures compression

  The output file can be compressed with one of the `bz2`, `gz`, `lzma`, or `xz` formats by ending the filename with the corresponding extension. For example, to output the data as a compressed JSON file:

  ```bash
  django-admin dumpdata -o mydata.json.gz
  ```

### `flush`

- `django-admin flush`

  Removes all data from the database and re-executes any post-synchronization handlers. The table of which migrations have been applied is not cleared.

  If you would rather start from an empty database and rerun all migrations, you should drop and recreate the database and then run `migrate` instead.

- `--noinput, --no-input`

  Suppresses all user prompts.

- `--database DATABASE`

  Specifies the database to flush. Defaults to `default`.

### `inspectdb`

- `django-admin inspectdb [table [table ...]]`

  Introspects the database tables in the database pointed-to by the `NAME` setting and outputs a Django model module (a `models.py` file) to standard output.

  You may choose what tables or views to inspect by passing their names as arguments. If no arguments are provided, models are created for views only if the `--include-views` option is used. Models for partition tables are created on PostgreSQL if the `--include-partitions` option is used.

  Use this if you have a legacy database with which you’d like to use Django. The script will inspect the database and create a model for each table within it.

  As you might expect, the created models will have an attribute for every field in the table. Note that `inspectdb` has a few special cases in its field-name output:

  - If `inspectdb` cannot map a column’s type to a model field type, it’ll use `TextField` and will insert the Python comment `'This field type is a guess.'` next to the field in the generated model. The recognized fields may depend on apps listed in `INSTALLED_APPS`. For example, `django.contrib.postgres` adds recognition for several PostgreSQL-specific field types.
  - If the database column name is a Python reserved word (such as `'pass'`, `'class'` or `'for'`), `inspectdb` will append `'_field'` to the attribute name. For example, if a table has a column `'for'`, the generated model will have a field `'for_field'`, with the `db_column` attribute set to `'for'`. `inspectdb` will insert the Python comment `'Field renamed because it was a Python reserved word.'` next to the field.

  This feature is meant as a shortcut, not as definitive model generation. After you run it, you’ll want to look over the generated models yourself to make customizations. In particular, you’ll need to rearrange models’ order, so that models that refer to other models are ordered properly.

  Django doesn’t create database defaults when a `default` is specified on a model field. Similarly, database defaults aren’t translated to model field defaults or detected in any fashion by `inspectdb`.

  By default, `inspectdb` creates unmanaged models. That is, `managed = False` in the model’s `Meta` class tells Django not to manage each table’s creation, modification, and deletion. If you do want to allow Django to manage the table’s lifecycle, you’ll need to change the `managed` option to `True` (or remove it because `True` is its default value).

  #### Database-specific notes

  ##### Oracle

  - Models are created for materialized views if `--include-views` is used.

  ##### PostgreSQL

  - Models are created for foreign tables.
  - Models are created for materialized views if `--include-views` is used.
  - Models are created for partition tables if `--include-partitions` is used.

- `--database DATABASE`

  Specifies the database to introspect. Defaults to `default`.

- `--include-partitions`

  If this option is provided, models are also created for partitions.

  Only support for PostgreSQL is implemented.

- `--include-views`

  If this option is provided, models are also created for database views.

### `loaddata`

- `django-admin loaddata fixture [fixture ...]`

  Searches for and loads the contents of the named [fixture](../../topics/db/fixtures/#fixtures-explanation) into the database.

- `--database DATABASE`

  Specifies the database into which the data will be loaded. Defaults to `default`.

- `--ignorenonexistent, -i`

  Ignores fields and models that may have been removed since the fixture was originally generated.

- `--app APP_LABEL`

  Specifies a single app to look for fixtures in rather than looking in all apps.

- `--format FORMAT`

  Specifies the [serialization format](../../topics/serialization/#serialization-formats) (e.g., `json` or `xml`) for fixtures [read from stdin](#loading-fixtures-stdin).

- `--exclude EXCLUDE, -e EXCLUDE`

  Excludes loading the fixtures from the given applications and/or models (in the form of `app_label` or `app_label.ModelName`). Use the option multiple times to exclude more than one app or model.

  #### Loading fixtures from `stdin`

  You can use a dash as the fixture name to load input from `sys.stdin`. For example:

  ```bash
  django-admin loaddata --format=json -
  ```

  When reading from `stdin`, the `--format` option is required to specify the [serialization format](../../topics/serialization/#serialization-formats) of the input (e.g., `json` or `xml`).

  Loading from `stdin` is useful with standard input and output redirections. For example:

  ```bash
  django-admin dumpdata --format=json --database=test app_label.ModelName | django-admin loaddata --format=json --database=prod -
  ```

  The `dumpdata` command can be used to generate input for `loaddata`.

  **See also**

  For more detail about fixtures see the [Fixtures](../../topics/db/fixtures/#fixtures-explanation) topic.

### `makemessages`

- `django-admin makemessages`

  Runs over the entire source tree of the current directory and pulls out all strings marked for translation. It creates (or updates) a message file in the conf/locale (in the Django tree) or locale (for project and application) directory. After making changes to the messages files you need to compile them with `compilemessages` for use with the builtin gettext support. See the [i18n documentation](../../topics/i18n/translation/#how-to-create-language-files) for details.

  This command doesn’t require configured settings. However, when settings aren’t configured, the command can’t ignore the `MEDIA_ROOT` and `STATIC_ROOT` directories or include `LOCALE_PATHS`.

- `--all, -a`

  Updates the message files for all available languages.

- `--extension EXTENSIONS, -e EXTENSIONS`

  Specifies a list of file extensions to examine (default: `html`, `txt`, `py` or `js` if `--domain` is `djangojs`).

  Example usage:

  ```bash
  django-admin makemessages --locale=de --extension xhtml
  ```

  Separate multiple extensions with commas or use `-e` or `--extension` multiple times:

  ```bash
  django-admin makemessages --locale=de --extension=html,txt --extension xml
  ```

- `--locale LOCALE, -l LOCALE`

  Specifies the locale(s) to process.

- `--exclude EXCLUDE, -x EXCLUDE`

  Specifies the locale(s) to exclude from processing. If not provided, no locales are excluded.

  Example usage:

  ```bash
  django-admin makemessages --locale=pt_BR
  django-admin makemessages --locale=pt_BR --locale=fr
  django-admin makemessages -l pt_BR
  django-admin makemessages -l pt_BR -l fr
  django-admin makemessages --exclude=pt_BR
  django-admin makemessages --exclude=pt_BR --exclude=fr
  django-admin makemessages -x pt_BR
  django-admin makemessages -x pt_BR -x fr
  ```

- `--domain DOMAIN, -d DOMAIN`

  Specifies the domain of the messages files. Supported options are:

  - `django` for all `*.py`, `*.html` and `*.txt` files (default)
  - `djangojs` for `*.js` files

- `--symlinks, -s`

  Follows symlinks to directories when looking for new translation strings.

  Example usage:

  ```bash
  django-admin makemessages --locale=de --symlinks
  ```

- `--ignore PATTERN, -i PATTERN`

  Ignores files or directories matching the given [glob](https://docs.python.org/3/library/glob.html#module-glob)-style pattern. Use multiple times to ignore more.

  These patterns are used by default: `'CVS'`, `'.*'`, `'*~'`, `'*.pyc'`.

  Example usage:

  ```bash
  django-admin makemessages --locale=en_US --ignore=apps/* --ignore=secret/*.html
  ```

- `--no-default-ignore`

  Disables the default values of `--ignore`.

- `--no-wrap`

  Disables breaking long message lines into several lines in language files.

- `--no-location`

  Suppresses writing `'#: filename:line'` comment lines in language files. Using this option makes it harder for technically skilled translators to understand each message’s context.

- `--add-location [{full,file,never}]`

  Controls `#: filename:line` comment lines in language files. If the option is:

  - `full` (the default if not given): the lines include both file name and line number.
  - `file`: the line number is omitted.
  - `never`: the lines are suppressed (same as `--no-location`).

  Requires `gettext` 0.19 or newer.

- `--no-obsolete`

  Removes obsolete message strings from the `.po` files.

- `--keep-pot`

  Prevents deleting the temporary `.pot` files generated before creating the `.po` file. This is useful for debugging errors which may prevent the final language files from being created.

  **See also**

  See [Customizing the makemessages command](../../topics/i18n/translation/#customizing-makemessages) for instructions on how to customize the keywords that `makemessages` passes to `xgettext`.

### `makemigrations`

- `django-admin makemigrations [app_label [app_label ...]]`

  Creates new migrations based on the changes detected to your models. Migrations, their relationship with apps and more are covered in depth in [the migrations documentation](../../topics/migrations/).

  Providing one or more app names as arguments will limit the migrations created to the app(s) specified and any dependencies needed (the table at the other end of a `ForeignKey`, for example).

  To add migrations to an app that doesn’t have a `migrations` directory, run `makemigrations` with the app’s `app_label`.

- `--noinput, --no-input`

  Suppresses all user prompts. If a suppressed prompt cannot be resolved automatically, the command will exit with error code 3.

- `--empty`

  Outputs an empty migration for the specified apps, for manual editing. This is for advanced users and should not be used unless you are familiar with the migration format, migration operations, and the dependencies between your migrations.

- `--dry-run`

  Shows what migrations would be made without actually writing any migrations files to disk. Using this option along with `--verbosity 3` will also show the complete migrations files that would be written.

- `--merge`

  Enables fixing of migration conflicts.

- `--name NAME, -n NAME`

  Allows naming the generated migration(s) instead of using a generated name. The name must be a valid Python [identifier](https://docs.python.org/3/reference/lexical_analysis.html#identifiers).

- `--no-header`

  Generate migration files without Django version and timestamp header.

- `--check`

  Makes `makemigrations` exit with a non-zero status when model changes without migrations are detected. Implies `--dry-run`.

- `--scriptable`

  Diverts log output and input prompts to `stderr`, writing only paths of generated migration files to `stdout`.

- `--update`

  Merges model changes into the latest migration and optimize the resulting operations.

  The updated migration will have a generated name. In order to preserve the previous name, set it using `--name`.

### `migrate`

- `django-admin migrate [app_label] [migration_name]`

  Synchronizes the database state with the current set of models and migrations. Migrations, their relationship with apps and more are covered in depth in [the migrations documentation](../../topics/migrations/).

  The behavior of this command changes depending on the arguments provided:

  - No arguments: All apps have all of their migrations run.
  - `<app_label>`: The specified app has its migrations run, up to the most recent migration. This may involve running other apps’ migrations too, due to dependencies.
  - `<app_label> <migrationname>`: Brings the database schema to a state where the named migration is applied, but no later migrations in the same app are applied. This may involve unapplying migrations if you have previously migrated past the named migration. You can use a prefix of the migration name, e.g. `0001`, as long as it’s unique for the given app name. Use the name `zero` to migrate all the way back i.e. to revert all applied migrations for an app.

  **Warning**

  When unapplying migrations, all dependent migrations will also be unapplied, regardless of `<app_label>`. You can use `--plan` to check which migrations will be unapplied.

- `--database DATABASE`

  Specifies the database to migrate. Defaults to `default`.

- `--fake`

  Marks the migrations up to the target one (following the rules above) as applied, but without actually running the SQL to change your database schema.

  This is intended for advanced users to manipulate the current migration state directly if they’re manually applying changes; be warned that using `--fake` runs the risk of putting the migration state table into a state where manual recovery will be needed to make migrations run correctly.

- `--fake-initial`

  Allows Django to skip an app’s initial migration if all database tables with the names of all models created by all `CreateModel` operations in that migration already exist. This option is intended for use when first running migrations against a database that preexisted the use of migrations. This option does not, however, check for matching database schema beyond matching table names and so is only safe to use if you are confident that your existing schema matches what is recorded in your initial migration.

- `--plan`

  Shows the migration operations that will be performed for the given `migrate` command.

- `--run-syncdb`

  Allows creating tables for apps without migrations. While this isn’t recommended, the migrations framework is sometimes too slow on large projects with hundreds of models.

- `--noinput, --no-input`

  Suppresses all user prompts. An example prompt is asking about removing stale content types.

- `--check`

  Makes `migrate` exit with a non-zero status when unapplied migrations are detected.

- `--prune`

  Deletes nonexistent migrations from the `django_migrations` table. This is useful when migration files replaced by a squashed migration have been removed. See [Squashing migrations](../../topics/migrations/#migration-squashing) for more details.

### `optimizemigration`

- `django-admin optimizemigration app_label migration_name`

  Optimizes the operations for the named migration and overrides the existing file. If the migration contains functions that must be manually copied, the command creates a new migration file suffixed with `_optimized` that is meant to replace the named migration.

- `--check`

  Makes `optimizemigration` exit with a non-zero status when a migration can be optimized.

### `runserver`

- `django-admin runserver [addrport]`

  Starts a lightweight development web server on the local machine. By default, the server runs on port 8000 on the IP address `127.0.0.1`. You can pass in an IP address and port number explicitly.

  If you run this script as a user with normal privileges (recommended), you might not have access to start a port on a low port number. Low port numbers are reserved for the superuser (root).

  This server uses the WSGI application object specified by the `WSGI_APPLICATION` setting.

  **Warning**

  DO NOT USE THIS SERVER IN A PRODUCTION SETTING.

  This lightweight development server has not gone through security audits or performance tests, hence is unsuitable for production. Making this server able to handle a production environment is outside the scope of Django.

  The development server automatically reloads Python code for each request, as needed. You don’t need to restart the server for code changes to take effect. However, some actions like adding files don’t trigger a restart, so you’ll have to restart the server in these cases.

  If you’re using Linux or MacOS and install both [pywatchman](https://pypi.org/project/pywatchman/) and the [Watchman](https://facebook.github.io/watchman/) service, kernel signals will be used to autoreload the server (rather than polling file modification timestamps each second). This offers better performance on large projects, reduced response time after code changes, more robust change detection, and a reduction in power usage. Django supports `pywatchman` 1.2.0 and higher.

  **Large directories with many files may cause performance issues**

  When using Watchman with a project that includes large non-Python directories like `node_modules`, it’s advisable to ignore this directory for optimal performance. See the [watchman documentation](https://facebook.github.io/watchman/docs/config#ignore_dirs) for information on how to do this.

  **Watchman timeout**

  The default timeout of `Watchman` client is 5 seconds. You can change it by setting the `DJANGO_WATCHMAN_TIMEOUT` environment variable.

  When you start the server, and each time you change Python code while the server is running, the system check framework will check your entire Django project for some common errors (see the `check` command). If any errors are found, they will be printed to standard output. You can use the `--skip-checks` option to skip running system checks.

  You can run as many concurrent servers as you want, as long as they’re on separate ports by executing `django-admin runserver` more than once.

  Note that the default IP address, `127.0.0.1`, is not accessible from other machines on your network. To make your development server viewable to other machines on the network, use its own IP address (e.g. `192.168.2.1`), `0` (shortcut for `0.0.0.0`), `0.0.0.0`, or `::` (with IPv6 enabled).

  You can provide an IPv6 address surrounded by brackets (e.g. `[200a::1]:8000`). This will automatically enable IPv6 support.

  A hostname containing ASCII-only characters can also be used.

  If the `staticfiles` contrib app is enabled (default in new projects) the `runserver` command will be overridden with its own [runserver](../../contrib/staticfiles/#staticfiles-runserver) command.

  Logging of each request and response of the server is sent to the [django.server](../../logging/#django-server-logger) logger.

- `--noreload`

  Disables the auto-reloader. This means any Python code changes you make while the server is running will *not* take effect if the particular Python modules have already been loaded into memory.

- `--nothreading`

  Disables use of threading in the development server. The server is multithreaded by default.

- `--ipv6, -6`

  Uses IPv6 for the development server. This changes the default IP address from `127.0.0.1` to `::1`.

- `DJANGO_RUNSERVER_HIDE_WARNING`

  By default, a warning is printed to the console that `runserver` is not suitable for production:

  ```plaintext
  WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead. For more information on production servers see: https://docs.djangoproject.com/en/|version|/howto/deployment/
  ```

  Set this environment variable to `"true"` to hide this warning.

  #### Examples of using different ports and addresses

  - Port 8000 on IP address `127.0.0.1`:

    ```bash
    django-admin runserver
    ```

  - Port 8000 on IP address `1.2.3.4`:

    ```bash
    django-admin runserver 1.2.3.4:8000
    ```

  - Port 7000 on IP address `127.0.0.1`:

    ```bash
    django-admin runserver 7000
    ```

  - Port 7000 on IP address `1.2.3.4`:

    ```bash
    django-admin runserver 1.2.3.4:7000
    ```

  - Port 8000 on IPv6 address `::1`:

    ```bash
    django-admin runserver -6
    ```

  - Port 7000 on IPv6 address `::1`:

    ```bash
    django-admin runserver -6 7000
    ```

  - Port 7000 on IPv6 address `2001:0db8:1234:5678::9`:

    ```bash
    django-admin runserver [2001:0db8:1234:5678::9]:7000
    ```

  - Port 8000 on IPv4 address of host `localhost`:

    ```bash
    django-admin runserver localhost:8000
    ```

  - Port 8000 on IPv6 address of host `localhost`:

    ```bash
    django-admin runserver -6 localhost:8000
    ```

  #### Serving static files with the development server

  By default, the development server doesn’t serve any static files for your site (such as CSS files, images, things under `MEDIA_URL` and so forth). If you want to configure Django to serve static media, read [How to manage static files (e.g. images, JavaScript, CSS)](../../howto/static-files/).

  #### Serving with ASGI in development

  Django’s `runserver` command provides a WSGI server. In order to run under ASGI you will need to use an [ASGI server](../../howto/deployment/asgi/). The Django Daphne project provides [Integration with runserver](../../howto/deployment/asgi/daphne/#daphne-runserver) that you can use.

### `sendtestemail`

- `django-admin sendtestemail [email [email ...]]`

  Sends a test email (to confirm email sending through Django is working) to the recipient(s) specified. For example:

  ```bash
  django-admin sendtestemail foo@example.com bar@example.com
  ```

  There are a couple of options, and you may use any combination of them together:

- `--managers`

  Mails the email addresses specified in `MANAGERS` using `mail_managers()`.

- `--admins`

  Mails the email addresses specified in `ADMINS` using `mail_admins()`.

### `shell`

- `django-admin shell`

  Starts the Python interactive interpreter.

  All models from installed apps are automatically imported into the shell environment. Models from apps listed earlier in `INSTALLED_APPS` take precedence. For a `--verbosity` of 2 or higher, the automatically imported objects will be listed. To disable automatic importing entirely, use the `--no-imports` flag.

  See the guide on [customizing this behaviour](../../howto/custom-shell/#customizing-shell-auto-imports) to add or remove automatic imports.

  **Changed in Django 5.2:**

  Automatic models import was added.

- `--interface {ipython,bpython,python}, -i {ipython,bpython,python}`

  Specifies the shell to use. By default, Django will use [IPython](https://ipython.org/) or [bpython](https://bpython-interpreter.org/) if either is installed. If both are installed, specify which one you want like so:

  IPython:

  ```bash
  django-admin shell -i ipython
  ```

  bpython:

  ```bash
  django-admin shell -i bpython
  ```

  If you have a “rich” shell installed but want to force use of the “plain” Python interpreter, use `python` as the interface name, like so:

  ```bash
  django-admin shell -i python
  ```

- `--no-startup`

  Disables reading the startup script for the “plain” Python interpreter. By default, the script pointed to by the [PYTHONSTARTUP](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONSTARTUP) environment variable or the `~/.pythonrc.py` script is read.

- `--no-imports`

  Disables the automatic import of models from `INSTALLED_APPS`.

- `--command COMMAND, -c COMMAND`

  Lets you pass a command as a string to execute it as Django, like so:

  ```bash
  django-admin shell --command="import django; print(django.__version__)"
  ```

  You can also pass code in on standard input to execute it. For example:

  ```bash
  $ django-admin shell <<EOF
  > import django
  > print(django.__version__)
  > EOF
  ```

  On Windows, the REPL is output due to implementation limits of `select.select()` on that platform.

### `showmigrations`

- `django-admin showmigrations [app_label [app_label ...]]`

  Shows all migrations in a project. You can choose from one of two formats:

- `--list, -l`

  Lists all of the apps Django knows about, the migrations available for each app, and whether or not each migration is applied (marked by an `[X]` next to the migration name). For a `--verbosity` of 2 and above, the applied datetimes are also shown.

  Apps without migrations are also listed, but have `(no migrations)` printed under them.

  This is the default output format.

- `--plan, -p`

  Shows the migration plan Django will follow to apply migrations. Like `--list`, applied migrations are marked by an `[X]`. For a `--verbosity` of 2 and above, all dependencies of a migration will also be shown.

  `<app_label>`s arguments limit the output, however, dependencies of provided apps may also be included.

- `--database DATABASE`

  Specifies the database to examine. Defaults to `default`.

### `sqlflush`

- `django-admin sqlflush`

  Prints the SQL statements that would be executed for the `flush` command.

- `--database DATABASE`

  Specifies the database for which to print the SQL. Defaults to `default`.

### `sqlmigrate`

- `django-admin sqlmigrate app_label migration_name`

  Prints the SQL for the named migration. This requires an active database connection, which it will use to resolve constraint names; this means you must generate the SQL against a copy of the database you wish to later apply it on.

  Note that `sqlmigrate` doesn’t colorize its output.

- `--backwards`

  Generates the SQL for unapplying the migration. By default, the SQL created is for running the migration in the forwards direction.

- `--database DATABASE`

  Specifies the database for which to generate the SQL. Defaults to `default`.

### `sqlsequencereset`

- `django-admin sqlsequencereset app_label [app_label ...]`

  Prints the SQL statements for resetting sequences for the given app name(s).

  Sequences are indexes used by some database engines to track the next available number for automatically incremented fields.

  Use this command to generate SQL which will fix cases where a sequence is out of sync with its automatically incremented field data.

- `--database DATABASE`

  Specifies the database for which to print the SQL. Defaults to `default`.

### `squashmigrations`

- `django-admin squashmigrations app_label [start_migration_name] migration_name`

  Squashes the migrations for `app_label` up to and including `migration_name` down into fewer migrations, if possible. The resulting squashed migrations can live alongside the unsquashed ones safely. For more information, please read [Squashing migrations](../../topics/migrations/#migration-squashing).

  When `start_migration_name` is given, Django will only include migrations starting from and including this migration. This helps to mitigate the squashing limitation of `RunPython` and `django.db.migrations.operations.RunSQL` migration operations.

- `--no-optimize`

  Disables the optimizer when generating a squashed migration. By default, Django will try to optimize the operations in your migrations to reduce the size of the resulting file. Use this option if this process is failing or creating incorrect migrations, though please also file a Django bug report about the behavior, as optimization is meant to be safe.

- `--noinput, --no-input`

  Suppresses all user prompts.

- `--squashed-name SQUASHED_NAME`

  Sets the name of the squashed migration. When omitted, the name is based on the first and last migration, with `_squashed_` in between.

- `--no-header`

  Generate squashed migration file without Django version and timestamp header.

### `startapp`

- `django-admin startapp name [directory]`

  Creates a Django app directory structure for the given app name in the current directory or the given destination.

  By default, [the new directory](https://github.com/django/django/blob/main/django/conf/app_template) contains a `models.py` file and other app template files. If only the app name is given, the app directory will be created in the current working directory.

  If the optional destination is provided, Django will use that existing directory rather than creating a new one. You can use ‘.’ to denote the current working directory.

  For example:

  ```bash
  django-admin startapp myapp /Users/jezdez/Code/myapp
  ```

- `--template TEMPLATE`

  Provides the path to a directory with a custom app template file, or a path to an uncompressed archive (`.tar`) or a compressed archive (`.tar.gz`, `.tar.bz2`, `.tar.xz`, `.tar.lzma`, `.tgz`, `.tbz2`, `.txz`, `.tlz`, `.zip`) containing the app template files.

  For example, this would look for an app template in the given directory when creating the `myapp` app:

  ```bash
  django-admin startapp --template=/Users/jezdez/Code/my_app_template myapp
  ```

  Django will also accept URLs (`http`, `https`, `ftp`) to compressed archives with the app template files, downloading and extracting them on the fly.

  For example, taking advantage of GitHub’s feature to expose repositories as zip files, you can use a URL like:

  ```bash
  django-admin startapp --template=https://github.com/githubuser/django-app-template/archive/main.zip myapp
  ```

- `--extension EXTENSIONS, -e EXTENSIONS`

  Specifies which file extensions in the app template should be rendered with the template engine. Defaults to `py`.

- `--name FILES, -n FILES`

  Specifies which files in the app template (in addition to those matching `--extension`) should be rendered with the template engine. Defaults to an empty list.

- `--exclude DIRECTORIES, -x DIRECTORIES`

  Specifies which directories in the app template should be excluded, in addition to `.git` and `__pycache__`. If this option is not provided, directories named `__pycache__` or starting with `.` will be excluded.

  The [template context](../../templates/api/#django.template.Context) used for all matching files is:

  - Any option passed to the `startapp` command (among the command’s supported options)
  - `app_name` – the app name as passed to the command
  - `app_directory` – the full path of the newly created app
  - `camel_case_app_name` – the app name in camel case format
  - `docs_version` – the version of the documentation: `'dev'` or `'1.x'`
  - `django_version` – the version of Django, e.g. `'2.0.3'`

  **Warning**

  When the app template files are rendered with the Django template engine (by default all `*.py` files), Django will also replace all stray template variables contained. For example, if one of the Python files contains a docstring explaining a particular feature related to template rendering, it might result in an incorrect example.

  To work around this problem, you can use the [templatetag](../../templates/builtins/#std-templatetag-templatetag) template tag to “escape” the various parts of the template syntax.

  In addition, to allow Python template files that contain Django template language syntax while also preventing packaging systems from trying to byte-compile invalid `*.py` files, template files ending with `.py-tpl` will be renamed to `.py`.

  **Warning**

  The contents of custom app (or project) templates should always be audited before use: Such templates define code that will become part of your project, and this means that such code will be trusted as much as any app you install, or code you write yourself. Further, even rendering the templates is, effectively, executing code that was provided as input to the management command. The Django template language may provide wide access into the system, so make sure any custom template you use is worthy of your trust.

### `startproject`

- `django-admin startproject name [directory]`

  Creates a Django project directory structure for the given project name in the current directory or the given destination.

  By default, [the new directory](https://github.com/django/django/blob/main/django/conf/project_template) contains `manage.py` and a project package (containing a `settings.py` and other files).

  If only the project name is given, both the project directory and project package will be named `<projectname>` and the project directory will be created in the current working directory.

  If the optional destination is provided, Django will use that existing directory as the project directory, and create `manage.py` and the project package within it. Use ‘.’ to denote the current working directory.

  For example:

  ```bash
  django-admin startproject myproject /Users/jezdez/Code/myproject_repo
  ```

- `--template TEMPLATE`

  Specifies a directory, file path, or URL of a custom project template. See the [startapp --template](#cmdoption-startapp-template) documentation for examples and usage.

- `--extension EXTENSIONS, -e EXTENSIONS`

  Specifies which file extensions in the project template should be rendered with the template engine. Defaults to `py`.

- `--name FILES, -n FILES`

  Specifies which files in the project template (in addition to those matching `--extension`) should be rendered with the template engine. Defaults to an empty list.

- `--exclude DIRECTORIES, -x DIRECTORIES`

  Specifies which directories in the project template should be excluded, in addition to `.git` and `__pycache__`. If this option is not provided, directories named `__pycache__` or starting with `.` will be excluded.

  The [template context](../../templates/api/#django.template.Context) used is:

  - Any option passed to the `startproject` command (among the command’s supported options)
  - `project_name` – the project name as passed to the command
  - `project_directory` – the full path of the newly created project
  - `secret_key` – a random key for the `SECRET_KEY` setting
  - `docs_version` – the version of the documentation: `'dev'` or `'1.x'`
  - `django_version` – the version of Django, e.g. `'2.0.3'`

  Please also see the [rendering warning](#render-warning) and [trusted code warning](#trusted-code-warning) as mentioned for `startapp`.

### `test`

- `django-admin test [test_label [test_label ...]]`

  Runs tests for all installed apps. See [Testing in Django](../../topics/testing/) for more information.

- `--failfast`

  Stops running tests and reports the failure immediately after a test fails.

- `--testrunner TESTRUNNER`

  Controls the test runner class that is used to execute tests. This value overrides the value provided by the `TEST_RUNNER` setting.

- `--noinput, --no-input`

  Suppresses all user prompts. A typical prompt is a warning about deleting an existing test database.

  #### Test runner options

  The `test` command receives options on behalf of the specified `--testrunner`. These are the options of the default test runner: `DiscoverRunner`.

- `--keepdb`

  Preserves the test database between test runs. This has the advantage of skipping both the create and destroy actions which can greatly decrease the time to run tests, especially those in a large test suite. If the test database does not exist, it will be created on the first run and then preserved for each subsequent run. Unless the `MIGRATE` test setting is `False`, any unapplied migrations will also be applied to the test database before running the test suite.

- `--shuffle [SEED]`

  Randomizes the order of tests before running them. This can help detect tests that aren’t properly isolated. The test order generated by this option is a deterministic function of the integer seed given. When no seed is passed, a seed is chosen randomly and printed to the console. To repeat a particular test order, pass a seed. The test orders generated by this option preserve Django’s [guarantees on test order](../../topics/testing/overview/#order-of-tests). They also keep tests grouped by test case class.

  The shuffled orderings also have a special consistency property useful when narrowing down isolation issues. Namely, for a given seed and when running a subset of tests, the new order will be the original shuffling restricted to the smaller set. Similarly, when adding tests

---

# Django-admin and manage.py

## Usage

### Getting runtime help

To get help on any command, use the `help` command:

```bash
django-admin help <command>
```

For example:

```bash
django-admin help testserver
```

### App names

Some commands take one or more app labels as arguments. An app label is a short name for an application. App labels must be unique across a project.

### Determining the version

To determine which version of Django you’re using, run:

```bash
django-admin --version
```

### Displaying debug output

To display debug output, use the `--verbosity` option:

```bash
django-admin <command> --verbosity <level>
```

The verbosity level can be 0, 1, 2, or 3:

- `0` means no output.
- `1` means normal output (default).
- `2` means verbose output.
- `3` means very verbose output.

## Available commands

### check

Checks for any problems in your project without making migrations or touching the database.

### compilemessages

Compiles .po files to .mo files for use with built-in gettext support.

### createcachetable

Creates the table needed to use database caching.

### dbshell

Runs the command-line client for your database.

### diffsettings

Displays differences between the current settings file and Django’s default settings.

### dumpdata

Outputs all data in your database as JSON or XML.

#### Fixtures compression

You can compress the output of `dumpdata` using gzip or bzip2.

### flush

Returns the database to the state it was in immediately after `syncdb` was executed.

### inspectdb

Introspects the database tables in the given database and outputs a Django model module.

#### Database-specific notes

##### Oracle

Oracle databases require the `cx_Oracle` module.

##### PostgreSQL

PostgreSQL databases require the `psycopg2` module.

### loaddata

Loads the contents of fixtures into the database.

#### Loading fixtures from stdin

You can load fixtures from standard input by using a hyphen (`-`) as the fixture name.

### makemessages

Runs over the source tree and creates (or updates) a message file for each language.

### makemigrations

Creates new migration(s) for changes you have made to your models.

### migrate

Synchronizes the database state with the current set of models and migrations.

### optimizemigration

Optimizes the migration files for the given app.

### runserver

Runs a lightweight development server.

#### Examples of using different ports and addresses

```bash
django-admin runserver 8080
django-admin runserver 127.0.0.1:8080
```

#### Serving static files with the development server

The development server automatically serves static files from the `STATIC_URL` path.

#### Serving with ASGI in development

You can run the development server with ASGI by using the `--asgi` option.

### sendtestemail

Sends a test email to the email addresses specified in the `EMAILS` setting.

### shell

Runs a Python interactive interpreter.

### showmigrations

Shows a list of migrations and their status.

### sqlflush

Returns the SQL statements that would be executed for the `flush` management command.

### sqlmigrate

Prints the SQL statements for a migration.

### sqlsequencereset

Prints the SQL statements for resetting sequences.

### squashmigrations

Combines multiple migrations into a single migration.

### startapp

Creates a Django app directory structure for the given app name in the current directory or the given destination.

### startproject

Creates a Django project directory structure for the given project name in the current directory or the given destination.

By default, the new directory contains `manage.py` and a project package (containing a `settings.py` and other files).

If only the project name is given, both the project directory and project package will be named `<projectname>` and the project directory will be created in the current working directory.

If the optional destination is provided, Django will use that existing directory as the project directory, and create `manage.py` and the project package within it. Use ‘.’ to denote the current working directory.

For example:

```bash
django-admin startproject myproject /Users/jezdez/Code/myproject_repo
```

#### --template

Specifies a directory, file path, or URL of a custom project template. See the `startapp --template` documentation for examples and usage.

#### --extension

Specifies which file extensions in the project template should be rendered with the template engine. Defaults to `py`.

#### --name

Specifies which files in the project template (in addition to those matching `--extension`) should be rendered with the template engine. Defaults to an empty list.

#### --exclude

Specifies which directories in the project template should be excluded, in addition to `.git` and `__pycache__`. If this option is not provided, directories named `__pycache__` or starting with `.` will be excluded.

The template context used is:

- Any option passed to the `startproject` command (among the command’s supported options)
- `project_name` – the project name as passed to the command
- `project_directory` – the full path of the newly created project
- `secret_key` – a random key for the `SECRET_KEY` setting
- `docs_version` – the version of the documentation: `'dev'` or `'1.x'`
- `django_version` – the version of Django, e.g. `'2.0.3'`

Please also see the rendering warning and trusted code warning as mentioned for `startapp`.

### test

Runs tests for all installed apps. See [Testing in Django](https://docs.djangoproject.com/en/5.2/topics/testing/) for more information.

#### --failfast

Stops running tests and reports the failure immediately after a test fails.

#### --testrunner

Controls the test runner class that is used to execute tests. This value overrides the value provided by the `TEST_RUNNER` setting.

#### --noinput

Suppresses all user prompts. A typical prompt is a warning about deleting an existing test database.

#### Test runner options

The `test` command receives options on behalf of the specified `--testrunner`. These are the options of the default test runner: `DiscoverRunner`.

##### --keepdb

Preserves the test database between test runs. This has the advantage of skipping both the create and destroy actions which can greatly decrease the time to run tests, especially those in a large test suite. If the test database does not exist, it will be created on the first run and then preserved for each subsequent run. Unless the `MIGRATE` test setting is `False`, any unapplied migrations will also be applied to the test database before running the test suite.

##### --shuffle

Randomizes the order of tests before running them. This can help detect tests that aren’t properly isolated. The test order generated by this option is a deterministic function of the integer seed given. When no seed is passed, a seed is chosen randomly and printed to the console. To repeat a particular test order, pass a seed. The test orders generated by this option preserve Django’s guarantees on test order. They also keep tests grouped by test case class.

The shuffled orderings also have a special consistency property useful when narrowing down isolation issues. Namely, for a given seed and when running a subset of tests, the new order will be the original shuffling restricted to the smaller set. Similarly, when adding tests while keeping the seed the same, the order of the original tests will be the same in the new order.

##### --reverse

Sorts test cases in the opposite execution order. This may help in debugging the side effects of tests that aren’t properly isolated. Grouping by test class is preserved when using this option. This can be used in conjunction with `--shuffle` to reverse the order for a particular seed.

##### --debug-mode

Sets the `DEBUG` setting to `True` prior to running tests. This may help troubleshoot test failures.

##### --debug-sql

Enables SQL logging for failing tests. If `--verbosity` is `2`, then queries in passing tests are also output.

##### --parallel

Runs tests in separate parallel processes. Since modern processors have multiple cores, this allows running tests significantly faster.

Using `--parallel` without a value, or with the value `auto`, runs one test process per core according to `multiprocessing.cpu_count()`. You can override this by passing the desired number of processes, e.g. `--parallel 4`, or by setting the `DJANGO_TEST_PROCESSES` environment variable.

Django distributes test cases — `unittest.TestCase` subclasses — to subprocesses. If there are fewer test case classes than configured processes, Django will reduce the number of processes accordingly.

Each process gets its own database. You must ensure that different test case classes don’t access the same resources. For instance, test case classes that touch the filesystem should create a temporary directory for their own use.

Note: If you have test classes that cannot be run in parallel, you can use `SerializeMixin` to run them sequentially. See [Enforce running test classes sequentially](https://docs.djangoproject.com/en/5.2/topics/testing/advanced/#topics-testing-enforce-run-sequentially).

This option requires the third-party `tblib` package to display tracebacks correctly:

```bash
$ python -mpip install tblib
```

This feature isn’t available on Windows. It doesn’t work with the Oracle database backend either.

If you want to use `pdb` while debugging tests, you must disable parallel execution (`--parallel=1`). You’ll see something like `bdb.BdbQuit` if you don’t.

Warning: When test parallelization is enabled and a test fails, Django may be unable to display the exception traceback. This can make debugging difficult. If you encounter this problem, run the affected test without parallelization to see the traceback of the failure.

This is a known limitation. It arises from the need to serialize objects in order to exchange them between processes. See [What can be pickled and unpickled?](https://docs.python.org/3/library/pickle.html#pickle-picklable) for details.

##### --tag

Runs only tests marked with the specified tags. May be specified multiple times and combined with `test --exclude-tag`.

Tests that fail to load are always considered matching.

##### --exclude-tag

Excludes tests marked with the specified tags. May be specified multiple times and combined with `test --tag`.

##### -k

Runs test methods and classes matching test name patterns, in the same way as `unittest's -k option`. Can be specified multiple times.

##### --pdb

Spawns a `pdb` debugger at each test error or failure. If you have it installed, `ipdb` is used instead.

##### --buffer

Discards output (`stdout` and `stderr`) for passing tests, in the same way as `unittest's --buffer option`.

##### --no-faulthandler

Django automatically calls `faulthandler.enable()` when starting the tests, which allows it to print a traceback if the interpreter crashes. Pass `--no-faulthandler` to disable this behavior.

##### --timing

Outputs timings, including database setup and total run time.

##### --durations

Shows the N slowest test cases (N=0 for all).

Python 3.12 and later: This feature is only available for Python 3.12 and later.

### testserver

Runs a Django development server (as in `runserver`) using data from the given fixture(s).

For example, this command:

```bash
django-admin testserver mydata.json
```

…would perform the following steps:

1. Create a test database, as described in [The test database](https://docs.djangoproject.com/en/5.2/topics/testing/overview/#the-test-database).
2. Populate the test database with fixture data from the given fixtures. (For more on fixtures, see the documentation for `loaddata` above.)
3. Runs the Django development server (as in `runserver`), pointed at this newly created test database instead of your production database.

This is useful in a number of ways:

- When you’re writing [unit tests](https://docs.djangoproject.com/en/5.2/topics/testing/overview/) of how your views act with certain fixture data, you can use `testserver` to interact with the views in a web browser, manually.
- Let’s say you’re developing your Django application and have a “pristine” copy of a database that you’d like to interact with. You can dump your database to a [fixture](https://docs.djangoproject.com/en/5.2/topics/db/fixtures/#fixtures-explanation) (using the `dumpdata` command, explained above), then use `testserver` to run your web application with that data. With this arrangement, you have the flexibility of messing up your data in any way, knowing that whatever data changes you’re making are only being made to a test database.

Note that this server does *not* automatically detect changes to your Python source code (as `runserver` does). It does, however, detect changes to templates.

#### --addrport

Specifies a different port, or IP address and port, from the default of `127.0.0.1:8000`. This value follows exactly the same format and serves exactly the same function as the argument to the `runserver` command.

Examples:

To run the test server on port 7000 with `fixture1` and `fixture2`:

```bash
django-admin testserver --addrport 7000 fixture1 fixture2
django-admin testserver fixture1 fixture2 --addrport 7000
```

(The above statements are equivalent. We include both of them to demonstrate that it doesn’t matter whether the options come before or after the fixture arguments.)

To run on 1.2.3.4:7000 with a `test` fixture:

```bash
django-admin testserver --addrport 1.2.3.4:7000 test
```

#### --noinput

Suppresses all user prompts. A typical prompt is a warning about deleting an existing test database.

## Commands provided by applications

Some commands are only available when the `django.contrib` application that [implements](https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/) them has been [`enabled`](https://docs.djangoproject.com/en/5.2/settings/#std-setting-INSTALLED_APPS). This section describes them grouped by their application.

### django.contrib.auth

#### changepassword

This command is only available if Django’s [authentication system](https://docs.djangoproject.com/en/5.2/topics/auth/) (`django.contrib.auth`) is installed.

Allows changing a user’s password. It prompts you to enter a new password twice for the given user. If the entries are identical, this immediately becomes the new password. If you do not supply a user, the command will attempt to change the password whose username matches the current user.

##### --database

Specifies the database to query for the user. Defaults to `default`.

Example usage:

```bash
django-admin changepassword ringo
```

#### createsuperuser

This command is only available if Django’s [authentication system](https://docs.djangoproject.com/en/5.2/topics/auth/) (`django.contrib.auth`) is installed.

Creates a superuser account (a user who has all permissions). This is useful if you need to create an initial superuser account or if you need to programmatically generate superuser accounts for your site(s).

When run interactively, this command will prompt for a password for the new superuser account. When run non-interactively, you can provide a password by setting the `DJANGO_SUPERUSER_PASSWORD` environment variable. Otherwise, no password will be set, and the superuser account will not be able to log in until a password has been manually set for it.

In non-interactive mode, the [`USERNAME_FIELD`](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#django.contrib.auth.models.CustomUser.USERNAME_FIELD) and required fields (listed in [`REQUIRED_FIELDS`](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS)) fall back to `DJANGO_SUPERUSER_<uppercase_field_name>` environment variables, unless they are overridden by a command line argument. For example, to provide an `email` field, you can use `DJANGO_SUPERUSER_EMAIL` environment variable.

##### --noinput

Suppresses all user prompts. If a suppressed prompt cannot be resolved automatically, the command will exit with error code 1.

##### --username

The username and email address for the new account can be supplied by using the `--username` and `--email` arguments on the command line. If either of those is not supplied, `createsuperuser` will prompt for it when running interactively.

##### --database

Specifies the database into which the superuser object will be saved.

You can subclass the management command and override `get_input_data()` if you want to customize data input and validation. Consult the source code for details on the existing implementation and the method’s parameters. For example, it could be useful if you have a `ForeignKey` in [`REQUIRED_FIELDS`](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS) and want to allow creating an instance instead of entering the primary key of an existing instance.

### django.contrib.contenttypes

#### remove_stale_contenttypes

This command is only available if Django’s [contenttypes app](https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/) ([`django.contrib.contenttypes`](https://docs.djangoproject.com/en/5.2/ref/contrib/contenttypes/#module-django.contrib.contenttypes)) is installed.

Deletes stale content types (from deleted models) in your database. Any objects that depend on the deleted content types will also be deleted. A list of deleted objects will be displayed before you confirm it’s okay to proceed with the deletion.

##### --database

Specifies the database to use. Defaults to `default`.

##### --include-stale-apps

Deletes stale content types including ones from previously installed apps that have been removed from [`INSTALLED_APPS`](https://docs.djangoproject.com/en/5.2/settings/#std-setting-INSTALLED_APPS). Defaults to `False`.

### django.contrib.gis

#### ogrinspect

This command is only available if [GeoDjango](https://docs.djangoproject.com/en/5.2/ref/contrib/gis/) (`django.contrib.gis`) is installed.

Please refer to its [description](https://docs.djangoproject.com/en/5.2/ref/contrib/gis/commands/#django-admin-ogrinspect) in the GeoDjango documentation.

### django.contrib.sessions

#### clearsessions

Can be run as a cron job or directly to clean out expired sessions.

### django.contrib.staticfiles

#### collectstatic

This command is only available if the [static files application](https://docs.djangoproject.com/en/5.2/howto/static-files/) (`django.contrib.staticfiles`) is installed.

Please refer to its [description](https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#django-admin-collectstatic) in the [staticfiles](https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/) documentation.

#### findstatic

This command is only available if the [static files application](https://docs.djangoproject.com/en/5.2/howto/static-files/) (`django.contrib.staticfiles`) is installed.

Please refer to its [description](https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#django-admin-findstatic) in the [staticfiles](https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/) documentation.

## Default options

Although some commands may allow their own custom options, every command allows for the following options by default:

### --pythonpath

Adds the given filesystem path to the Python [`sys.path`](https://docs.python.org/3/library/sys.html#sys.path) module attribute. If this isn’t provided, `django-admin` will use the [`PYTHONPATH`](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH) environment variable.

This option is unnecessary in `manage.py`, because it takes care of setting the Python path for you.

Example usage:

```bash
django-admin migrate --pythonpath='/home/djangoprojects/myproject'
```

### --settings

Specifies the settings module to use. The settings module should be in Python package syntax, e.g. `mysite.settings`. If this isn’t provided, `django-admin` will use the [`DJANGO_SETTINGS_MODULE`](https://docs.djangoproject.com/en/5.2/topics/settings/#envvar-DJANGO_SETTINGS_MODULE) environment variable.

This option is unnecessary in `manage.py`, because it uses `settings.py` from the current project by default.

Example usage:

```bash
django-admin migrate --settings=mysite.settings
```

### --traceback

Displays a full stack trace when a [`CommandError`](https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/#django.core.management.CommandError) is raised. By default, `django-admin` will show an error message when a `CommandError` occurs and a full stack trace for any other exception.

This option is ignored by [`runserver`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-runserver).

Example usage:

```bash
django-admin migrate --traceback
```

### --verbosity

Specifies the amount of notification and debug information that a command should print to the console.

- `0` means no output.
- `1` means normal output (default).
- `2` means verbose output.
- `3` means *very* verbose output.

This option is ignored by [`runserver`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-runserver).

Example usage:

```bash
django-admin migrate --verbosity 2
```

### --no-color

Disables colorized command output. Some commands format their output to be colorized. For example, errors will be printed to the console in red and SQL statements will be syntax highlighted.

Example usage:

```bash
django-admin runserver --no-color
```

### --force-color

Forces colorization of the command output if it would otherwise be disabled as discussed in [Syntax coloring](https://docs.djangoproject.com/en/5.2/ref/django-admin/#syntax-coloring). For example, you may want to pipe colored output to another command.

### --skip-checks

Skips running system checks prior to running the command. This option is only available if the [`requires_system_checks`](https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/#django.core.management.BaseCommand.requires_system_checks) command attribute is not an empty list or tuple.

Example usage:

```bash
django-admin migrate --skip-checks
```

## Extra niceties

### Syntax coloring

The `django-admin` / `manage.py` commands will use pretty color-coded output if your terminal supports ANSI-colored output. It won’t use the color codes if you’re piping the command’s output to another program unless the [`--force-color`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#cmdoption-force-color) option is used.

#### Windows support

On Windows 10, the [Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal-preview/9n0dx20hk701) application, [VS Code](https://code.visualstudio.com), and PowerShell (where virtual terminal processing is enabled) allow colored output, and are supported by default.

Under Windows, the legacy `cmd.exe` native console doesn’t support ANSI escape sequences so by default there is no color output. In this case either of two third-party libraries are needed:

- Install [colorama](https://pypi.org/project/colorama/), a Python package that translates ANSI color codes into Windows API calls. Django commands will detect its presence and will make use of its services to color output just like on Unix-based platforms. `colorama` can be installed via pip:

```bash
...> py -m pip install "colorama >= 0.4.6"
```

- Install [ANSICON](http://adoxa.altervista.org/ansicon/), a third-party tool that allows `cmd.exe` to process ANSI color codes. Django commands will detect its presence and will make use of its services to color output just like on Unix-based platforms.

Other modern terminal environments on Windows, that support terminal colors, but which are not automatically detected as supported by Django, may “fake” the installation of `ANSICON` by setting the appropriate environmental variable, `ANSICON="on"`.

#### Custom colors

The colors used for syntax highlighting can be customized. Django ships with three color palettes:

- `dark`, suited to terminals that show white text on a black background. This is the default palette.
- `light`, suited to terminals that show black text on a white background.
- `nocolor`, which disables syntax highlighting.

You select a palette by setting a [`DJANGO_COLORS`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#envvar-DJANGO_COLORS) environment variable to specify the palette you want to use. For example, to specify the `light` palette under a Unix or OS/X BASH shell, you would run the following at a command prompt:

```bash
export DJANGO_COLORS="light"
```

You can also customize the colors that are used. Django specifies a number of roles in which color is used:

- `error` - A major error.
- `notice` - A minor error.
- `success` - A success.
- `warning` - A warning.
- `sql_field` - The name of a model field in SQL.
- `sql_coltype` - The type of a model field in SQL.
- `sql_keyword` - An SQL keyword.
- `sql_table` - The name of a model in SQL.
- `http_info` - A 1XX HTTP Informational server response.
- `http_success` - A 2XX HTTP Success server response.
- `http_not_modified` - A 304 HTTP Not Modified server response.
- `http_redirect` - A 3XX HTTP Redirect server response other than 304.
- `http_not_found` - A 404 HTTP Not Found server response.
- `http_bad_request` - A 4XX HTTP Bad Request server response other than 404.
- `http_server_error` - A 5XX HTTP Server Error response.
- `migrate_heading` - A heading in a migrations management command.
- `migrate_label` - A migration name.

Each of these roles can be assigned a specific foreground and background color, from the following list:

- `black`
- `red`
- `green`
- `yellow`
- `blue`
- `magenta`
- `cyan`
- `white`

Each of these colors can then be modified by using the following display options:

- `bold`
- `underscore`
- `blink`
- `reverse`
- `conceal`

A color specification follows one of the following patterns:

- `role=fg`
- `role=fg/bg`
- `role=fg,option,option`
- `role=fg/bg,option,option`

where `role` is the name of a valid color role, `fg` is the foreground color, `bg` is the background color and each `option` is one of the color modifying options. Multiple color specifications are then separated by a semicolon. For example:

```bash
export DJANGO_COLORS="error=yellow/blue,blink;notice=magenta"
```

would specify that errors be displayed using blinking yellow on blue, and notices displayed using magenta. All other color roles would be left uncolored.

Colors can also be specified by extending a base palette. If you put a palette name in a color specification, all the colors implied by that palette will be loaded. So:

```bash
export DJANGO_COLORS="light;error=yellow/blue,blink;notice=magenta"
```

would specify the use of all the colors in the light color palette, *except* for the colors for errors and notices which would be overridden as specified.

### Bash completion

If you use the Bash shell, consider installing the Django bash completion script, which lives in [extras/django_bash_completion](https://github.com/django/django/blob/main/extras/django_bash_completion) in the Django source distribution. It enables tab-completion of `django-admin` and `manage.py` commands, so you can, for instance…

- Type `django-admin`.
- Press [TAB] to see all available options.
- Type `sql`, then [TAB], to see all available options whose names start with `sql`.

See [How to create custom django-admin commands](https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/) for how to add customized actions.

### Black formatting

The Python files created by [`startproject`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-startproject), [`startapp`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-startapp), [`optimizemigration`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-optimizemigration), [`makemigrations`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-makemigrations), and [`squashmigrations`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-squashmigrations) are formatted using the `black` command if it is present on your `PATH`.

If you have `black` globally installed, but do not wish it used for the current project, you can set the `PATH` explicitly:

```bash
PATH=path/to/venv/bin django-admin makemigrations
```

For commands using `stdout` you can pipe the output to `black` if needed:

```bash
django-admin inspectdb | black -
```

# Running management commands from your code

```python
django.core.management.call_command(name, *args, **options)
```

To call a management command from code use `call_command()`.

- `name`: the name of the command to call or a command object. Passing the name is preferred unless the object is required for testing.
- `*args`: a list of arguments accepted by the command. Arguments are passed to the argument parser, so you can use the same style as you would on the command line. For example, `call_command('flush', '--verbosity=0')`.
- `**options`: named options accepted on the command-line. Options are passed to the command without triggering the argument parser, which means you’ll need to pass the correct type. For example, `call_command('flush', verbosity=0)` (zero must be an integer rather than a string).

Examples:

```python
from django.core import management
from django.core.management.commands import loaddata

management.call_command('flush', verbosity=0, interactive=False)
management.call_command('loaddata', 'test_data', verbosity=0)
management.call_command(loaddata.Command(), 'test_data', verbosity=0)
```

Note that command options that take no arguments are passed as keywords with `True` or `False`, as you can see with the `interactive` option above.

Named arguments can be passed by using either one of the following syntaxes:

```python
# Similar to the command line
management.call_command('dumpdata', '--natural-foreign')
# Named argument similar to the command line minus the initial dashes and
# with internal dashes replaced by underscores
management.call_command('dumpdata', natural_foreign=True)
# `use_natural_foreign_keys` is the option destination variable
management.call_command('dumpdata', use_natural_foreign_keys=True)
```

Some command options have different names when using `call_command()` instead of `django-admin` or `manage.py`. For example, `django-admin createsuperuser --no-input` translates to `call_command('createsuperuser', interactive=False)`. To find what keyword argument name to use for `call_command()`, check the command’s source code for the `dest` argument passed to `parser.add_argument()`.

Command options which take multiple options are passed a list:

```python
management.call_command('dumpdata', exclude=['contenttypes', 'auth'])
```

The return value of the `call_command()` function is the same as the return value of the `handle()` method of the command.

## Output redirection

Note that you can redirect standard output and error streams as all commands support the `stdout` and `stderr` options. For example, you could write:

```python
with open("/path/to/command_output", "w") as f:
    management.call_command('dumpdata', stdout=f)
```