# Writing and Running Tests

See also

- The [testing tutorial](../../../intro/tutorial05/), the [testing tools reference](../tools/), and the [advanced testing topics](../advanced/).

This document is split into two primary sections. First, we explain how to write tests with Django. Then, we explain how to run them.

## Writing Tests

Django’s unit tests use a Python standard library module: [`unittest`](https://docs.python.org/3/library/unittest.html#module-unittest). This module defines tests using a class-based approach.

Here is an example which subclasses from [`django.test.TestCase`](../tools/#django.test.TestCase), which is a subclass of [`unittest.TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase) that runs each test inside a transaction to provide isolation:

```python
from django.test import TestCase
from myapp.models import Animal

class AnimalTestCase(TestCase):
    def setUp(self):
        Animal.objects.create(name="lion", sound="roar")
        Animal.objects.create(name="cat", sound="meow")

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        lion = Animal.objects.get(name="lion")
        cat = Animal.objects.get(name="cat")
        self.assertEqual(lion.speak(), 'The lion says "roar"')
        self.assertEqual(cat.speak(), 'The cat says "meow"')
```

When you [run your tests](#running-tests), the default behavior of the test utility is to find all the test case classes (that is, subclasses of [`unittest.TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase)) in any file whose name begins with `test`, automatically build a test suite out of those test case classes, and run that suite.

For more details about [`unittest`](https://docs.python.org/3/library/unittest.html#module-unittest), see the Python documentation.

### Where Should the Tests Live?

The default [`startapp`](../../../ref/django-admin/#django-admin-startapp) template creates a `tests.py` file in the new application. This might be fine if you only have a few tests, but as your test suite grows you’ll likely want to restructure it into a tests package so you can split your tests into different submodules such as `test_models.py`, `test_views.py`, `test_forms.py`, etc. Feel free to pick whatever organizational scheme you like.

See also [Using the Django test runner to test reusable applications](../advanced/#testing-reusable-applications).

**Warning**

If your tests rely on database access such as creating or querying models, be sure to create your test classes as subclasses of [`django.test.TestCase`](../tools/#django.test.TestCase) rather than [`unittest.TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase).

Using [`unittest.TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase) avoids the cost of running each test in a transaction and flushing the database, but if your tests interact with the database their behavior will vary based on the order that the test runner executes them. This can lead to unit tests that pass when run in isolation but fail when run in a suite.

## Running Tests

Once you’ve written tests, run them using the [`test`](../../../ref/django-admin/#django-admin-test) command of your project’s `manage.py` utility:

```bash
$ ./manage.py test
```

Test discovery is based on the unittest module’s [built-in test discovery](https://docs.python.org/3/library/unittest.html#unittest-test-discovery). By default, this will discover tests in any file named `test*.py` under the current working directory.

You can specify particular tests to run by supplying any number of “test labels” to `./manage.py test`. Each test label can be a full Python dotted path to a package, module, `TestCase` subclass, or test method. For instance:

```bash
# Run all the tests in the animals.tests module
$ ./manage.py test animals.tests

# Run all the tests found within the 'animals' package
$ ./manage.py test animals

# Run just one test case class
$ ./manage.py test animals.tests.AnimalTestCase

# Run just one test method
$ ./manage.py test animals.tests.AnimalTestCase.test_animals_can_speak
```

You can also provide a path to a directory to discover tests below that directory:

```bash
$ ./manage.py test animals/
```

You can specify a custom filename pattern match using the `-p` (or `--pattern`) option, if your test files are named differently from the `test*.py` pattern:

```bash
$ ./manage.py test --pattern="tests_*.py"
```

If you press `Ctrl-C` while the tests are running, the test runner will wait for the currently running test to complete and then exit gracefully. During a graceful exit the test runner will output details of any test failures, report on how many tests were run and how many errors and failures were encountered, and destroy any test databases as usual. Thus pressing `Ctrl-C` can be very useful if you forget to pass the [`--failfast`](../../../ref/django-admin/#cmdoption-test-failfast) option, notice that some tests are unexpectedly failing and want to get details on the failures without waiting for the full test run to complete.

If you do not want to wait for the currently running test to finish, you can press `Ctrl-C` a second time and the test run will halt immediately, but not gracefully. No details of the tests run before the interruption will be reported, and any test databases created by the run will not be destroyed.

### Test with Warnings Enabled

It’s a good idea to run your tests with Python warnings enabled: `python -Wa manage.py test`. The `-Wa` flag tells Python to display deprecation warnings. Django, like many other Python libraries, uses these warnings to flag when features are going away. It also might flag areas in your code that aren’t strictly wrong but could benefit from a better implementation.

### The Test Database

Tests that require a database (namely, model tests) will not use your “real” (production) database. Separate, blank databases are created for the tests.

Regardless of whether the tests pass or fail, the test databases are destroyed when all the tests have been executed.

You can prevent the test databases from being destroyed by using the [`test --keepdb`](../../../ref/django-admin/#cmdoption-test-keepdb) option. This will preserve the test database between runs. If the database does not exist, it will first be created. Any migrations will also be applied in order to keep it up to date.

As described in the previous section, if a test run is forcefully interrupted, the test database may not be destroyed. On the next run, you’ll be asked whether you want to reuse or destroy the database. Use the [`test --noinput`](../../../ref/django-admin/#cmdoption-test-noinput) option to suppress that prompt and automatically destroy the database. This can be useful when running tests on a continuous integration server where tests may be interrupted by a timeout, for example.

The default test database names are created by prepending `test_` to the value of each [`NAME`](../../../ref/settings/#std-setting-NAME) in [`DATABASES`](../../../ref/settings/#std-setting-DATABASES). When using SQLite, the tests will use an in-memory database by default (i.e., the database will be created in memory, bypassing the filesystem entirely!). The [`TEST`](../../../ref/settings/#std-setting-DATABASE-TEST) dictionary in [`DATABASES`](../../../ref/settings/#std-setting-DATABASES) offers a number of settings to configure your test database. For example, if you want to use a different database name, specify [`NAME`](../../../ref/settings/#std-setting-TEST_NAME) in the [`TEST`](../../../ref/settings/#std-setting-DATABASE-TEST) dictionary for any given database in [`DATABASES`](../../../ref/settings/#std-setting-DATABASES).

On PostgreSQL, [`USER`](../../../ref/settings/#std-setting-USER) will also need read access to the built-in `postgres` database.

Aside from using a separate database, the test runner will otherwise use all of the same database settings you have in your settings file: [`ENGINE`](../../../ref/settings/#std-setting-DATABASE-ENGINE), [`USER`](../../../ref/settings/#std-setting-USER), [`HOST`](../../../ref/settings/#std-setting-HOST), etc. The test database is created by the user specified by [`USER`](../../../ref/settings/#std-setting-USER), so you’ll need to make sure that the given user account has sufficient privileges to create a new database on the system.

For fine-grained control over the character encoding of your test database, use the [`CHARSET`](../../../ref/settings/#std-setting-TEST_CHARSET) TEST option. If you’re using MySQL, you can also use the [`COLLATION`](../../../ref/settings/#std-setting-TEST_COLLATION) option to control the particular collation used by the test database. See the [settings documentation](../../../ref/settings/) for details of these and other advanced settings.

If using an SQLite in-memory database with SQLite, [shared cache](https://www.sqlite.org/sharedcache.html) is enabled, so you can write tests with ability to share the database between threads.

**Finding data from your production database when running tests?**

If your code attempts to access the database when its modules are compiled, this will occur *before* the test database is set up, with potentially unexpected results. For example, if you have a database query in module-level code and a real database exists, production data could pollute your tests. *It is a bad idea to have such import-time database queries in your code* anyway - rewrite your code so that it doesn’t do this.

This also applies to customized implementations of [`ready()`](../../../ref/applications/#django.apps.AppConfig.ready).

See also

- The [advanced multi-db testing topics](../advanced/#topics-testing-advanced-multidb).

### Order in Which Tests Are Executed

In order to guarantee that all [`TestCase`](../../../ref/django-admin/#cmdoption-test-failfast) code starts with a clean database, the Django test runner reorders tests in the following way:

1. All [`TestCase`](../../../ref/django-admin/#cmdoption-test-failfast) subclasses are run first.
2. Then, all other Django-based tests (test case classes based on [`SimpleTestCase`](../../../ref/django-admin/#cmdoption-test-failfast), including [`TransactionTestCase`](../../../ref/django-admin/#cmdoption-test-failfast)) are run with no particular ordering guaranteed nor enforced among them.
3. Then any other [`unittest.TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase) tests (including doctests) that may alter the database without restoring it to its original state are run.

**Note**

The new ordering of tests may reveal unexpected dependencies on test case ordering. This is the case with doctests that relied on state left in the database by a given [`TransactionTestCase`](../../../ref/django-admin/#cmdoption-test-failfast) test, they must be updated to be able to run independently.

**Note**

Failures detected when loading tests are ordered before all of the above for quicker feedback. This includes things like test modules that couldn’t be found or that couldn’t be loaded due to syntax errors.

You may randomize and/or reverse the execution order inside groups using the [`test --shuffle`](../../../ref/django-admin/#cmdoption-test-shuffle) and [`--reverse`](../../../ref/django-admin/#cmdoption-test-shuffle) options. This can help with ensuring your tests are independent from each other.

### Rollback Emulation

Any initial data loaded in migrations will only be available in [`TestCase`](../../../ref/django-admin/#cmdoption-test-failfast) tests and not in [`TransactionTestCase`](../../../ref/django-admin/#cmdoption-test-failfast) tests, and additionally only on backends where transactions are supported (the most important exception being MyISAM). This is also true for tests which rely on [`TransactionTestCase`](../../../ref/django-admin/#cmdoption-test-failfast) such as [`LiveServerTestCase`](../../../ref/django-admin/#cmdoption-test-failfast) and [`StaticLiveServerTestCase`](../../../ref/django-admin/#cmdoption-test-failfast).

Django can reload that data for you on a per-testcase basis by setting the `serialized_rollback` option to `True` in the body of the [`TestCase`](../../../ref/django-admin/#cmdoption-test-failfast) or [`TransactionTestCase`](../../../ref/django-admin/#cmdoption-test-failfast), but note that this will slow down that test suite by approximately 3x.

Third-party apps or those developing against MyISAM will need to set this; in general, however, you should be developing your own projects against a transactional database and be using [`TestCase`](../../../ref/django-admin/#cmdoption-test-failfast) for most tests, and thus not need this setting.

The initial serialization is usually very quick, but if you wish to exclude some apps from this process (and speed up test runs slightly), you may add those apps to [`TEST_NON_SERIALIZED_APPS`](../../../ref/settings/#std-setting-TEST_NON_SERIALIZED_APPS).

To prevent serialized data from being loaded twice, setting `serialized_rollback=True` disables the [`post_migrate`](../../../ref/signals/#django.db.models.signals.post_migrate) signal when flushing the test database.

**Changed in Django 5.2:**

For [`TransactionTestCase`](../../../ref/django-admin/#cmdoption-test-failfast), serialized migration data is made available during `setUpClass()`.

### Other Test Conditions

Regardless of the value of the [`DEBUG`](../../../ref/settings/#std-setting-DEBUG) setting in your configuration file, all Django tests run with [`DEBUG`](../../../ref/settings/#std-setting-DEBUG)=False. This is to ensure that the observed output of your code matches what will be seen in a production setting.

Caches are not cleared after each test, and running `manage.py test fooapp` can insert data from the tests into the cache of a live system if you run your tests in production because, unlike databases, a separate “test cache” is not used. This behavior [may change](https://code.djangoproject.com/ticket/11505) in the future.

### Understanding the Test Output

When you run your tests, you’ll see a number of messages as the test runner prepares itself. You can control the level of detail of these messages with the `verbosity` option on the command line:

```bash
Creating test database... Creating table myapp_animal Creating table myapp_mineral
```

This tells you that the test runner is creating a test database, as described in the previous section.

Once the test database has been created, Django will run your tests. If everything goes well, you’ll see something like this:

```bash
----------------------------------------------------------------------
Ran 22 tests in 0.221s OK
```

If there are test failures, however, you’ll see full details about which tests failed:

```bash
======================================================================
FAIL: test_was_published_recently_with_future_poll (polls.tests.PollMethodTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dev/mysite/polls/tests.py", line 16, in test_was_published_recently_with_future_poll
    self.assertIs(future_poll.was_published_recently(), False)
AssertionError: True is not False
----------------------------------------------------------------------
Ran 1 test in 0.003s FAILED (failures=1)
```

A full explanation of this error output is beyond the scope of this document, but it’s pretty intuitive. You can consult the documentation of Python’s [`unittest`](https://docs.python.org/3/library/unittest.html#module-unittest) library for details.

Note that the return code for the test-runner script is 1 for any number of failed tests (whether the failure was caused by an error, a failed assertion, or an unexpected success). If all the tests pass, the return code is 0. This feature is useful if you’re using the test-runner script in a shell script and need to test for success or failure at that level.

### Speeding Up the Tests

#### Running Tests in Parallel

As long as your tests are properly isolated, you can run them in parallel to gain a speed up on multi-core hardware. See [`test --parallel`](../../../ref/django-admin/#cmdoption-test-parallel).

#### Password Hashing

The default password hasher is rather slow by design. If you’re authenticating many users in your tests, you may want to use a custom settings file and set the [`PASSWORD_HASHERS`](../../../ref/settings/#std-setting-PASSWORD_HASHERS) setting to a faster hashing algorithm:

```python
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
```

Don’t forget to also include in [`PASSWORD_HASHERS`](../../../ref/settings/#std-setting-PASSWORD_HASHERS) any hashing algorithm used in fixtures, if any.

#### Preserving the Test Database

The [`test --keepdb`](../../../ref/django-admin/#cmdoption-test-keepdb) option preserves the test database between test runs. It skips the create and destroy actions which can greatly decrease the time to run tests.

#### Avoiding Disk Access for Media Files

The [`InMemoryStorage`](../../../ref/files/storage/#django.core.files.storage.InMemoryStorage) is a convenient way to prevent disk access for media files. All data is kept in memory, then it gets discarded after tests run.