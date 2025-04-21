# What To Read Next

So you’ve read all the [introductory material](https://docs.djangoproject.com/en/5.2/) and have decided you’d like to keep using Django. We’ve only just scratched the surface with this intro (in fact, if you’ve read every single word, you’ve read about 5% of the overall documentation).

So what’s next?

Well, we’ve always been big fans of learning by doing. At this point you should know enough to start a project of your own and start fooling around. As you need to learn new tricks, come back to the documentation.

We’ve put a lot of effort into making Django’s documentation useful, clear and as complete as possible. The rest of this document explains more about how the documentation works so that you can get the most out of it.

(Yes, this is documentation about documentation. Rest assured we have no plans to write a document about how to read the document about documentation.)

## Finding Documentation

Django’s got a *lot* of documentation – almost 450,000 words and counting – so finding what you need can sometimes be tricky. A good place to start is the [Index](https://docs.djangoproject.com/en/5.2/genindex/). We also recommend using the builtin search feature.

Or you can just browse around!

## How The Documentation Is Organized

Django’s main documentation is broken up into “chunks” designed to fill different needs:

*   The [introductory material](https://docs.djangoproject.com/en/5.2/) is designed for people new to Django – or to web development in general. It doesn’t cover anything in depth, but instead gives a high-level overview of how developing in Django “feels”.

*   The [topic guides](https://docs.djangoproject.com/en/5.2/topics/), on the other hand, dive deep into individual parts of Django. There are complete guides to Django’s [model system](https://docs.djangoproject.com/en/5.2/topics/db/), [template engine](https://docs.djangoproject.com/en/5.2/topics/templates/), [forms framework](https://docs.djangoproject.com/en/5.2/topics/forms/), and much more.

    This is probably where you’ll want to spend most of your time; if you work your way through these guides you should come out knowing pretty much everything there is to know about Django.

*   Web development is often broad, not deep – problems span many domains. We’ve written a set of [how-to guides](https://docs.djangoproject.com/en/5.2/howto/) that answer common “How do I …?” questions. Here you’ll find information about [generating PDFs with Django](https://docs.djangoproject.com/en/5.2/howto/outputting-pdf/), [writing custom template tags](https://docs.djangoproject.com/en/5.2/howto/custom-template-tags/), and more.

    Answers to really common questions can also be found in the [FAQ](https://docs.djangoproject.com/en/5.2/faq/).

*   The guides and how-to’s don’t cover every single class, function, and method available in Django – that would be overwhelming when you’re trying to learn. Instead, details about individual classes, functions, methods, and modules are kept in the [reference](https://docs.djangoproject.com/en/5.2/ref/). This is where you’ll turn to find the details of a particular function or whatever you need.

*   If you are interested in deploying a project for public use, our docs have [several guides](https://docs.djangoproject.com/en/5.2/howto/deployment/) for various deployment setups as well as a [deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) for some things you’ll need to think about.

*   Finally, there’s some “specialized” documentation not usually relevant to most developers. This includes the [release notes](https://docs.djangoproject.com/en/5.2/releases/) and [internals documentation](https://docs.djangoproject.com/en/5.2/internals/) for those who want to add code to Django itself, and a [few other things that don’t fit elsewhere](https://docs.djangoproject.com/en/5.2/misc/).

## How Documentation Is Updated

Just as the Django code base is developed and improved on a daily basis, our documentation is consistently improving. We improve documentation for several reasons:

*   To make content fixes, such as grammar/typo corrections.

*   To add information and/or examples to existing sections that need to be expanded.

*   To document Django features that aren’t yet documented. (The list of such features is shrinking but exists nonetheless.)

*   To add documentation for new features as new features get added, or as Django APIs or behaviors change.

Django’s documentation is kept in the same source control system as its code. It lives in the [docs](https://github.com/django/django/blob/main/docs) directory of our Git repository. Each document online is a separate text file in the repository.

## Where To Get It

You can read Django documentation in several ways. They are, in order of preference:

### On The Web

The most recent version of the Django documentation lives at [https://docs.djangoproject.com/en/dev/](https://docs.djangoproject.com/en/dev/). These HTML pages are generated automatically from the text files in source control. That means they reflect the “latest and greatest” in Django – they include the very latest corrections and additions, and they discuss the latest Django features, which may only be available to users of the Django development version. (See [Differences between versions](https://docs.djangoproject.com/en/5.2/intro/whatsnext/#differences-between-versions) below.)

We encourage you to help improve the docs by submitting changes, corrections and suggestions in the [ticket system](https://code.djangoproject.com/). The Django developers actively monitor the ticket system and use your feedback to improve the documentation for everybody.

Note, however, that tickets should explicitly relate to the documentation, rather than asking broad tech-support questions. If you need help with your particular Django setup, try the [Django Forum](https://forum.djangoproject.com/) or the [Django Discord server](https://chat.djangoproject.com) instead.

### In Plain Text

For offline reading, or just for convenience, you can read the Django documentation in plain text.

If you’re using an official release of Django, the zipped package (tarball) of the code includes a `docs/` directory, which contains all the documentation for that release.

If you’re using the development version of Django (aka the main branch), the `docs/` directory contains all of the documentation. You can update your Git checkout to get the latest changes.

One low-tech way of taking advantage of the text documentation is by using the Unix `grep` utility to search for a phrase in all of the documentation. For example, this will show you each mention of the phrase “max_length” in any Django document:

```
$ grep -r max_length /path/to/django/docs/
```

```
...> grep -r max_length \path\to\django\docs\
```

### As Html, Locally

You can get a local copy of the HTML documentation following a few steps:

*   Django’s documentation uses a system called [Sphinx](https://www.sphinx-doc.org/) to convert from plain text to HTML. You’ll need to install Sphinx by either downloading and installing the package from the Sphinx website, or with `pip`:

```
$ python -m pip install Sphinx
```

```
...> py -m pip install Sphinx
```

*   Then, use the included `Makefile` to turn the documentation into HTML:

```
$ cd path/to/django/docs
$ make html
```

You’ll need [GNU Make](https://www.gnu.org/software/make/) installed for this.

If you’re on Windows you can alternatively use the included batch file:

```
cd path\to\django\docs
make.bat html
```

*   The HTML documentation will be placed in `docs/_build/html`.

## Differences Between Versions

The text documentation in the main branch of the Git repository contains the “latest and greatest” changes and additions. These changes include documentation of new features targeted for Django’s next [feature release](https://docs.djangoproject.com/en/5.2/internals/release-process/#term-Feature-release). For that reason, it’s worth pointing out our policy to highlight recent changes and additions to Django.

We follow this policy:

*   The development documentation at [https://docs.djangoproject.com/en/dev/](https://docs.djangoproject.com/en/dev/) is from the main branch. These docs correspond to the latest feature release, plus whatever features have been added/changed in the framework since then.

*   As we add features to Django’s development version, we update the documentation in the same Git commit transaction.

*   To distinguish feature changes/additions in the docs, we use the phrase: “New in Django Development version” for the version of Django that hasn’t been released yet, or “New in version X.Y” for released versions.

*   Documentation fixes and improvements may be backported to the last release branch, at the discretion of the merger, however, once a version of Django is [no longer supported](https://docs.djangoproject.com/en/5.2/internals/release-process/#supported-versions-policy), that version of the docs won’t get any further updates.

*   The [main documentation web page](https://docs.djangoproject.com/en/dev/) includes links to documentation for previous versions. Be sure you are using the version of the docs corresponding to the version of Django you are using!