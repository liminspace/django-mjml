.. image:: https://cloud.githubusercontent.com/assets/5173158/14615647/5fc03bf8-05af-11e6-8cdd-f87bf432c4a2.png
  :target:
  :alt: Django + MJML

django-mjml
===========

Use MJML in Django templates

Installation
------------

**Requirements:**

* Django v1.9+
* mjml v1.3.4+

**\1\. Install** ``mjml``.

See https://github.com/mjmlio/mjml#installation and https://mjml.io/documentation/#installation

**\2\. Install** ``django-mjml``.

* Via pip::

  $ pip install django-mjml

* Via setuptools::

  $ easy_install django-mjml
  

 For install development version use ``git+https://github.com/liminspace/django-mjml.git@develop`` instead ``django-mjml``.

**\3\. Set up** ``settings.py`` **in your django project.** ::

  INSTALLED_APPS = (
    ...,
    'mjml',
  )
