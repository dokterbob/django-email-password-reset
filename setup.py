from setuptools import setup, find_packages

try:
    README = open('README.rst').read()
except:
    README = None

setup(
    name='django-email-password-reset',
    version='0.1.1',
    description='Minimalist app disabling all passwords and sending password reset emails.',
    long_description=README,
    license='BSD',
    author='Mathijs de Bruin',
    author_email='mathijs@mathijsfietst.nl',
    url='https://github.com/dokterbob/django-email-password-reset/',
    packages=find_packages(),
    include_package_data=True,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    )
)
