# How To Install Django On Windows

This document will guide you through installing Python 3.13 and Django on Windows. It also provides instructions for setting up a virtual environment, which makes it easier to work on Python projects. This is meant as a beginner’s guide for users working on Django projects and does not reflect how Django should be installed when developing changes for Django itself.

The steps in this guide have been tested with Windows 10. In other versions, the steps would be similar. You will need to be familiar with using the Windows command prompt.

## Install Python

Django is a Python web framework, thus requiring Python to be installed on your machine. At the time of writing, Python 3.13 is the latest version.

To install Python on your machine go to <https://www.python.org/downloads/>. The website should offer you a download button for the latest Python version. Download the executable installer and run it. Check the boxes next to “Install launcher for all users (recommended)” then click “Install Now”.

After installation, open the command prompt and check that the Python version matches the version you installed by executing:

```
...\\> py --version
```

<div>
<p><code>py</code> is not recognized or found</p>
<p>Depending on how you’ve installed Python (such as via the Microsoft Store), <code>py</code> may not be available in the command prompt.</p>
<p>You will then need to use <code>python</code> instead of <code>py</code> when entering commands.</p>
</div>

<div>
<p>See also</p>
<p>For more details, see <a href="https://docs.python.org/3/using/windows.html" title="(in Python v3.13)">Using Python on Windows</a> documentation.</p>
</div>

## About `pip`

<a href="https://pypi.org/project/pip/">pip</a> is a package manager for Python and is included by default with the Python installer. It helps to install and uninstall Python packages (such as Django!). For the rest of the installation, we’ll use <code>pip</code> to install Python packages from the command line.

## Setting Up A Virtual Environment

It is best practice to provide a dedicated environment for each Django project you create. There are many options to manage environments and packages within the Python ecosystem, some of which are recommended in the <a href="https://packaging.python.org/guides/tool-recommendations/">Python documentation</a>. Python itself comes with <a href="https://docs.python.org/3/tutorial/venv.html" title="(in Python v3.13)">venv</a> for managing environments which we will use for this guide.

To create a virtual environment for your project, open a new command prompt, navigate to the folder where you want to create your project and then enter the following:

```
...\\> py -m venv project-name
```

This will create a folder called ‘project-name’ if it does not already exist and set up the virtual environment. To activate the environment, run:

```
...\\> project-name\\Scripts\\activate.bat
```

The virtual environment will be activated and you’ll see “(project-name)” next to the command prompt to designate that. Each time you start a new command prompt, you’ll need to activate the environment again.

## Install Django

Django can be installed easily using <code>pip</code> within your virtual environment.

In the command prompt, ensure your virtual environment is active, and execute the following command:

```
...\\> py -m pip install Django
```

This will download and install the latest Django release.

After the installation has completed, you can verify your Django installation by executing <code>django-admin --version</code> in the command prompt.

See <a href="../../topics/install/#database-installation">Get your database running</a> for information on database installation with Django.

## Colored Terminal Output

A quality-of-life feature adds colored (rather than monochrome) output to the terminal. In modern terminals this should work for both CMD and PowerShell. If for some reason this needs to be disabled, set the environmental variable <a href="../../ref/django-admin/#envvar-DJANGO_COLORS"><code>DJANGO_COLORS</code></a> to <code>nocolor</code>.

On older Windows versions, or legacy terminals, <a href="https://pypi.org/project/colorama/">colorama</a> 0.4.6+ must be installed to enable syntax coloring:

```
...\\> py -m pip install "colorama >= 0.4.6"
```

See <a href="../../ref/django-admin/#syntax-coloring">Syntax coloring</a> for more information on color settings.

## Common Pitfalls

*   If <code>django-admin</code> only displays the help text no matter what arguments it is given, there is probably a problem with the file association in Windows. Check if there is more than one environment variable set for running Python scripts in <code>PATH</code>. This usually occurs when there is more than one Python version installed.
*   If you are connecting to the internet behind a proxy, there might be problems in running the command <code>py -m pip install Django</code>. Set the environment variables for proxy configuration in the command prompt as follows:

    ```
    ...\\> set http_proxy=http://username:password@proxyserver:proxyport
    ...\\> set https_proxy=https://username:password@proxyserver:proxyport
    ```
*   In general, Django assumes that <code>UTF-8</code> encoding is used for I/O. This may cause problems if your system is set to use a different encoding. Recent versions of Python allow setting the <a href="https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUTF8" title="(in Python v3.13)"><code>PYTHONUTF8</code></a> environment variable in order to force a <code>UTF-8</code> encoding. Windows 10 also provides a system-wide setting by checking <code>Use Unicode UTF-8 for worldwide language support</code> in Language ‣ Administrative Language Settings ‣ Change system locale in system settings.