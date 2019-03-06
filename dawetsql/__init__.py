from .odbc_sql import OdbcSqlMagics

__version__ = '0.1b1'
__author__ = 'Agung Pratama'

def load_ipython_extension(ipython):
    ipython.register_magics(OdbcSqlMagics)