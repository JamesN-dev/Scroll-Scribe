# Django’s Security Policies

Django’s development team is strongly committed to responsible reporting and disclosure of security-related issues. As such, we’ve adopted and follow a set of policies which conform to that ideal and are geared toward allowing us to deliver timely security updates to the official distribution of Django, as well as to third-party distributions.

## Reporting Security Issues

**Short version: please report security issues by emailing security@djangoproject.com**.

Most normal bugs in Django are reported to [our public Trac instance](https://code.djangoproject.com/query), but due to the sensitive nature of security issues, we ask that they **not** be publicly reported in this fashion.

Instead, if you believe you’ve found something in Django which has security implications, please send a description of the issue via email to `security@djangoproject.com`. Mail sent to that address reaches the [security team](https://www.djangoproject.com/foundation/teams/#security-team).

Once you’ve submitted an issue via email, you should receive an acknowledgment from a member of the security team within 3 working days. After that, the security team will begin their analysis. Depending on the action to be taken, you may receive followup emails. It can take several weeks before the security team comes to a conclusion. There is no need to chase the security team unless you discover new, relevant information. All reports aim to be resolved within the industry-standard 90 days. Confirmed vulnerabilities with a [high severity level](#severity-levels) will be addressed promptly.

<div>
<p>Sending encrypted reports</p>
<p>If you want to send an encrypted email (<em>optional</em>), the public key ID for <code>security@djangoproject.com</code> is <code>0xfcb84b8d1d17f80b</code>, and this public key is available from most commonly-used keyservers.</p>
</div>

### Reporting Guidelines

#### Include A Runnable Proof Of Concept

Please privately share a minimal Django project or code snippet that demonstrates the potential vulnerability. Include clear instructions on how to set up, run, and reproduce the issue.

Please do not attach screenshots of code.

#### User Input Must Be Sanitized

Reports based on a failure to sanitize user input are not valid security vulnerabilities. It is the developer’s responsibility to properly handle user input. This principle is explained in our [security documentation](../../topics/security/#sanitize-user-input).

For example, the following is **not considered valid** because `email` has not been sanitized:

```python
from django.core.mail import send_mail
from django.http import JsonResponse

def my_proof_of_concept(request):
    email = request.GET.get("email", "")
    send_mail("Email subject", "Email body", email, ["admin@example.com"])
    return JsonResponse(status=200)
```

Developers must **always validate and sanitize input** before using it. The correct approach would be to use a Django form to ensure `email` is properly validated:

```python
from django import forms
from django.core.mail import send_mail
from django.http import JsonResponse

class EmailForm(forms.Form):
    email = forms.EmailField()

def my_proof_of_concept(request):
    form = EmailForm(request.GET)
    if form.is_valid():
        send_mail(
            "Email subject",
            "Email body",
            form.cleaned_data["email"],
            ["admin@example.com"],
        )
        return JsonResponse(status=200)
    return JsonResponse(form.errors, status=400)
```

Similarly, as Django’s raw SQL constructs (such as [extra()](../../ref/models/querysets/#django.db.models.query.QuerySet.extra) and [RawSQL](../../ref/models/expressions/#django.db.models.expressions.RawSQL) expression) provide developers with full control over the query, they are insecure if user input is not properly handled. As explained in our [security documentation](../../topics/security/#sql-injection-protection), it is the developer’s responsibility to safely process user input for these functions.

For instance, the following is **not considered valid** because `query` has not been sanitized:

```python
from django.shortcuts import HttpResponse
from .models import MyModel

def my_proof_of_concept(request):
    query = request.GET.get("query", "")
    q = MyModel.objects.extra(select={"id": query})
    return HttpResponse(q.values())
```

#### Request Headers And Urls Must Be Under 8K Bytes

To prevent denial-of-service (DoS) attacks, production-grade servers impose limits on request header and URL sizes. For example, by default Gunicorn allows up to roughly:

*   [4k bytes for a URL](https://docs.gunicorn.org/en/stable/settings.html#limit-request-line)
*   [8K bytes for a request header](https://docs.gunicorn.org/en/stable/settings.html#limit-request-field-size)

Other web servers, such as Nginx and Apache, have similar restrictions to prevent excessive resource consumption.

Consequently, the Django security team will not consider reports that rely on request headers or URLs exceeding 8K bytes, as such inputs are already mitigated at the server level in production environments.

<div>
<p>[<code>runserver</code>](../../ref/django-admin/#django-admin-runserver) should never be used in production</p>
<p>Django’s built-in development server does not enforce these limits because it is not designed to be a production server.</p>
</div>

#### The Request Body Must Be Under 2.5 MB

The [<code>DATA_UPLOAD_MAX_MEMORY_SIZE</code>](../../ref/settings/#std-setting-DATA_UPLOAD_MAX_MEMORY_SIZE) setting limits the default maximum request body size to 2.5 MB.

As this is enforced on all production-grade Django projects by default, a proof of concept must not exceed 2.5 MB in the request body to be considered valid.

Issues resulting from large, but potentially reasonable setting values, should be reported using the [public ticket tracker](https://code.djangoproject.com/) for hardening.

#### Code Under Test Must Feasibly Exist In A Django Project

The proof of concept must plausibly occur in a production-grade Django application, reflecting real-world scenarios and following standard development practices.

Django contains many private and undocumented functions that are not part of its public API. If a vulnerability depends on directly calling these internal functions in an unsafe way, it will not be considered a valid security issue.

#### Content Displayed By The Django Template Language Must Be Under 100 KB

The Django Template Language (DTL) is designed for building the content needed to display web pages. In particular its text filters are meant for that kind of usage.

For reference, the complete works of Shakespeare have about 3.5 million bytes in plain-text ASCII encoding. Displaying such in a single request is beyond the scope of almost all websites, and so outside the scope of the DTL too.

Text processing is expensive. Django makes no guarantee that DTL text filters are never subject to degraded performance if passed deliberately crafted, sufficiently large inputs. Under default configurations, Django makes it difficult for sites to accidentally accept such payloads from untrusted sources, but, if it is necessary to display large amounts of user-provided content, it’s important that basic security measures are taken.

User-provided content should always be constrained to known maximum length. It should be filtered to remove malicious content, and validated to match expected formats. It should then be processed offline, if necessary, before being displayed.

Proof of concepts which use over 100 KB of data to be processed by the DTL will be considered invalid.

## How Does Django Evaluate A Report

These are criteria used by the security team when evaluating whether a report requires a security release:

*   The vulnerability is within a [supported version](#security-support) of Django.
*   The vulnerability does not depend on manual actions that rely on code external to Django. This includes actions performed by a project’s developer or maintainer using developer tools or the Django CLI. For example, attacks that require running management commands with uncommon or insecure options do not qualify.
*   The vulnerability applies to a production-grade Django application. This means the following scenarios do not require a security release:
    *   Exploits that only affect local development, for example when using [<code>runserver</code>](../../ref/django-admin/#django-admin-runserver).
    *   Exploits which fail to follow security best practices, such as failure to sanitize user input. For other examples, see our [security documentation](../../topics/security/#cross-site-scripting).
    *   Exploits in AI generated code that do not adhere to security best practices.

The security team may conclude that the source of the vulnerability is within the Python standard library, in which case the reporter will be asked to report the vulnerability to the Python core team. For further details see the [Python security guidelines](https://www.python.org/dev/security/).

On occasion, a security release may be issued to help resolve a security vulnerability within a popular third-party package. These reports should come from the package maintainers.

If you are unsure whether your finding meets these criteria, please still report it [privately by emailing security@djangoproject.com](#reporting-security-issues). The security team will review your report and recommend the correct course of action.

## Supported Versions

At any given time, the Django team provides official security support for several versions of Django:

*   The [main development branch](https://github.com/django/django/), hosted on GitHub, which will become the next major release of Django, receives security support. Security issues that only affect the main development branch and not any stable released versions are fixed in public without going through the [disclosure process](#security-disclosure).
*   The two most recent Django release series receive security support. For example, during the development cycle leading to the release of Django 1.5, support will be provided for Django 1.4 and Django 1.3. Upon the release of Django 1.5, Django 1.3’s security support will end.
*   [Long-term support releases](../release-process/#term-Long-term-support-release) will receive security updates for a specified period.

When new releases are issued for security reasons, the accompanying notice will include a list of affected versions. This list is comprised solely of *supported* versions of Django: older versions may also be affected, but we do not investigate to determine that, and will not issue patches or new releases for those versions.

## Security Issue Severity Levels

The severity level of a security vulnerability is determined by the attack type.

Severity levels are:

*   **High**
    *   Remote code execution
    *   SQL injection
*   **Moderate**
    *   Cross site scripting (XSS)
    *   Cross site request forgery (CSRF)
    *   Denial-of-service attacks
    *   Broken authentication
*   **Low**
    *   Sensitive data exposure
    *   Broken session management
    *   Unvalidated redirects/forwards
    *   Issues requiring an uncommon configuration option

## How Django Discloses Security Issues

Our process for taking a security issue from private discussion to public disclosure involves multiple steps.

Approximately one week before public disclosure, we send two notifications:

First, we notify [django-announce](../mailing-lists/#django-announce-mailing-list) of the date and approximate time of the upcoming security release, as well as the severity of the issues. This is to aid organizations that need to ensure they have staff available to handle triaging our announcement and upgrade Django as needed.

Second, we notify a list of [people and organizations](#security-notifications), primarily composed of operating-system vendors and other distributors of Django. This email is signed with the PGP key of someone from [Django’s release team](https://www.djangoproject.com/foundation/teams/#releasers-team) and consists of:

*   A full description of the issue and the affected versions of Django.
*   The steps we will be taking to remedy the issue.
*   The patch(es), if any, that will be applied to Django.
*   The date on which the Django team will apply these patches, issue new releases and publicly disclose the issue.

On the day of disclosure, we will take the following steps:

1.  Apply the relevant patch(es) to Django’s codebase.
2.  Issue the relevant release(s), by placing new packages on the [Python Package Index](https://pypi.org/project/Django/) and on the [djangoproject.com website](https://www.djangoproject.com/download/), and tagging the new release(s) in Django’s git repository.
3.  Post a public entry on [the official Django development blog](https://www.djangoproject.com/weblog/), describing the issue and its resolution in detail, pointing to the relevant patches and new releases, and crediting the reporter of the issue (if the reporter wishes to be publicly identified).
4.  Post a notice to the [django-announce](../mailing-lists/#django-announce-mailing-list) and [oss-security@lists.openwall.com](mailto:oss-security%40lists.openwall.com) mailing lists that links to the blog post.

If a reported issue is believed to be particularly time-sensitive – due to a known exploit in the wild, for example – the time between advance notification and public disclosure may be shortened considerably.

Additionally, if we have reason to believe that an issue reported to us affects other frameworks or tools in the Python/web ecosystem, we may privately contact and discuss those issues with the appropriate maintainers, and coordinate our own disclosure and resolution with theirs.

The Django team also maintains an [archive of security issues disclosed in Django](../../releases/security/).

## Who Receives Advance Notification

The full list of people and organizations who receive advance notification of security issues is not and will not be made public.

We also aim to keep this list as small as effectively possible, in order to better manage the flow of confidential information prior to disclosure. As such, our notification list is *not* simply a list of users of Django, and being a user of Django is not sufficient reason to be placed on the notification list.

In broad terms, recipients of security notifications fall into three groups:

1.  Operating-system vendors and other distributors of Django who provide a suitably-generic (i.e., *not* an individual’s personal email address) contact address for reporting issues with their Django package, or for general security reporting. In either case, such addresses **must not** forward to public mailing lists or bug trackers. Addresses which forward to the private email of an individual maintainer or security-response contact are acceptable, although private security trackers or security-response groups are strongly preferred.
2.  On a case-by-case basis, individual package maintainers who have demonstrated a commitment to responding to and responsibly acting on these notifications.
3.  On a case-by-case basis, other entities who, in the judgment of the Django development team, need to be made aware of a pending security issue. Typically, membership in this group will consist of some of the largest and/or most likely to be severely impacted known users or distributors of Django, and will require a demonstrated ability to responsibly receive, keep confidential and act on these notifications.

<div>
<p>Security audit and scanning entities</p>
<p>As a policy, we do not add these types of entities to the notification list.</p>
</div>

## Requesting Notifications

If you believe that you, or an organization you are authorized to represent, fall into one of the groups listed above, you can ask to be added to Django’s notification list by emailing `security@djangoproject.com`. Please use the subject line “Security notification request”.

Your request **must** include the following information:

*   Your full, real name and the name of the organization you represent, if applicable, as well as your role within that organization.
*   A detailed explanation of how you or your organization fit at least one set of criteria listed above.
*   A detailed explanation of why you are requesting security notifications. Again, please keep in mind that this is *not* simply a list for users of Django, and the overwhelming majority of users should subscribe to [django-announce](../mailing-lists/#django-announce-mailing-list) to receive advanced notice of when a security release will happen, without the details of the issues, rather than request detailed notifications.
*   The email address you would like to have added to our notification list.
*   An explanation of who will be receiving/reviewing mail sent to that address, as well as information regarding any automated actions that will be taken (i.e., filing of a confidential issue in a bug tracker).
*   For individuals, the ID of a public key associated with your address which can be used to verify email received from you and encrypt email sent to you, as needed.

Once submitted, your request will be considered by the Django development team; you will receive a reply notifying you of the result of your request within 30 days.

Please also bear in mind that for any individual or organization, receiving security notifications is a privilege granted at the sole discretion of the Django development team, and that this privilege can be revoked at any time, with or without explanation.

<div>
<p>Provide all required information</p>
<p>A failure to provide the required information in your initial contact will count against you when making the decision on whether or not to approve your request.</p>
</div>

## LLM Notes:

No issues encountered.