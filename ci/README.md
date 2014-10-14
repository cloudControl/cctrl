Continous releasing
===================

This CI setup releases `cctrl` and `dotcloudng` packages on PyPI whenever a new bumped version
is pushed into master branch.

Requirements
------------

* Create a [PyPI account](https://pypi.python.org/pypi?%3Aaction=register_form) for jenkins user.
* Create `.pypirc` file at jenkins user's $HOME:

~~~
[distutils]
index-servers =
    pypi

[pypi]
username:{Jenkins username at PyPI}
password:{Jenkins password at PyPI}
~~~

* Add _maintainer_ [role](https://pypi.python.org/pypi?:action=role_form&package_name=cctrl) in `cctrl` and `dotcloung` to jenkins user.

Build Configuration
-------------------

Build configuration is basic and similar to other jenkins builds. Furthermore,
_Execute shell_ is pretty simple:

    ci/prepare
    python ci/release.py

Double checking
---------------

When build is executed, you should find fresh new packages released under:

* `cctrl`: https://pypi.python.org/pypi/cctrl
* `dotcloudng`: https://pypi.python.org/pypi/dotcloudng
* `cnh`: https://pypi.python.org/pypi/cnh
