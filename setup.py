import os
from setuptools import setup, find_packages
import mjml


setup(
    name='django-mjml',
    version=mjml.__version__,
    description='Use MJML in Django templates',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license='MIT',
    author='Igor Melnyk @liminspace',
    author_email='liminspace@gmail.com',
    url='https://github.com/liminspace/django-mjml',
    packages=find_packages(exclude=('testprj', 'testprj.*')),
    include_package_data=True,
    zip_safe=False,  # because include static
    platforms=['OS Independent'],
    python_requires='>=3.6',
    install_requires=[
        'django >=2.2,<5.2',
    ],
    extras_require={
        'requests': [
            'requests >=2.24',
        ],
    },
    keywords=[
        'django', 'mjml', 'django-mjml', 'email', 'layout', 'template', 'templatetag',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
)
