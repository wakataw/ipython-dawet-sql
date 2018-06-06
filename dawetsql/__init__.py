from .odbc_sql import OdbcSqlMagics

__version__ = '0.0.1.dev5'

def load_ipython_extension(ipython):
    ipython.register_magics(OdbcSqlMagics)