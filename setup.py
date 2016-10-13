import os
from distutils.core import setup
from setuptools import find_packages
import mjml


setup(
    name='django-mjml',
    version=mjml.__version__,
    description='Use MJML in Django templates',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license='MIT',
    author='Igor Melnyk',
    author_email='liminspace@gmail.com',
    url='https://github.com/liminspace/django-mjml',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,  # because include static
    install_requires=[
        'django>=1.8,<1.11',
    ],
    keywords=[
        'django', 'mjml', 'django-mjml', 'email', 'layout', 'template', 'templatetag',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
)
