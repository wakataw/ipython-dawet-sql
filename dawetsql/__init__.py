from .odbc_sql import OdbcSqlMagics

__version__ = '0.1b'
__author__ = 'Agung Pratama'

def load_ipython_extension(ipython):
    ipython.register_magics(OdbcSqlMagics)