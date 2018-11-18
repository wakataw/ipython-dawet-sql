from .odbc_sql import OdbcSqlMagics

__version__ = '0.0.1.dev7'
__author__ = 'Agung Pratama'

def load_ipython_extension(ipython):
    ipython.register_magics(OdbcSqlMagics)