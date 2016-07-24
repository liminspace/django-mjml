
.. figure:: https://travis-ci.org/liminspace/django-mjml.svg?branch=develop
  :target: https://travis-ci.org/liminspace/django-mjml

|

.. image:: https://cloud.githubusercontent.com/assets/5173158/14615647/5fc03bf8-05af-11e6-8cdd-f87bf432c4a2.png
  :target: #
  :alt: Django + MJML

django-mjml
===========

The simplest way to use `MJML <https://mjml.io/>`_ in `Django <https://www.djangoproject.com/>`_ templates.

|

Installation
------------

**Requirements:**

* Django v1.9+
* mjml v2.0+

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

|

Usage
-----

Load ``mjml`` in your django template and use ``mjml`` tag that will compile mjml to html::

  {% load mjml %}
  
  {% mjml %}
      <mjml>
      <mj-body>
      <mj-container>
          <mj-section>
              <mj-column>
                  <mj-text>Hello world!</mj-text>
              </mj-column>
          </mj-section>
      </mj-container>
      </mj-body>
      </mjml>
  {% endmjml %}

|

Advanced settings
-----

There are two backend modes for compiling: ``cmd`` and ``tcpserver``. ``cmd`` is used by default.

``**cmd**``
