from setuptools import setup

setup(
    name='ipython-dawet-sql',
    version='0.0.1.dev3',
    packages=['dawetsql'],
    url='https://gitlab.com/wakataw/ipython-dawet-sql',
    license='MIT',
    author='Agung Pratama',
    author_email='me@agungpratama.id',
    description='Ipython ODBC SQL Magic for Dawet',
    install_requires=[
        'pandas',
        'pypyodbc',
        'ipython'
    ]
)
