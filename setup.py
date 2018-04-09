from setuptools import setup

setup(
    name='ipython-odbc-sql',
    version='0.0.1',
    packages=['odbc_sql'],
    url='https://gitlab.com/wakataw/ipython-odbc-sql',
    license='MIT',
    author='Agung Pratama',
    author_email='me@agungpratama.id',
    description='Ipython ODBC SQL Magic',
    install_requires=[
        'pandas',
        'pyodbc',
        'ipython'
    ]
)
