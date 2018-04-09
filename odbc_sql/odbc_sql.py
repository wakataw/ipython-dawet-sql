import logging
import pyodbc
import pandas

from IPython.core import magic_arguments
from IPython.core.magic import magics_class, Magics, line_magic, cell_magic

@magics_class
class OdbcSqlMagics(Magics):
    conn = None
    chunksize = 500

    def __init__(self, *args, **kwargs):
        super(OdbcSqlMagics, self).__init__(*args, **kwargs)

    def __connect(self, dsn):
        '''
        Open database connection
        :param dsn: ODBC DSN
        :return:
        '''
        try:
            self.conn = pyodbc.connect("DSN={}".format(dsn))
            if self.conn:
                print("Conected to {}".format(dsn))
        except Exception as e:
            logging.error(e)
            return

    @line_magic('dawetsql')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('dsn', type=str, help="ODBC DSN")
    def odbc_connect(self, arg):
        '''
        Open Database Connection line magic method
        :param arg: ODBC DSN
        :return:
        '''
        if self.conn:
            self.odbc_disconnect()

        args = magic_arguments.parse_argstring(self.odbc_connect, arg)
        return self.__connect(args.dsn)

    @line_magic('dawetsqlclose')
    def odbc_disconnect(self, *args):
        '''
        Close Database Connection line magic method
        :param args:
        :return:
        '''
        try:
            self.conn.close()
        except:
            pass
        finally:
            self.conn = None
            return

    @cell_magic('dawetsql')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-l', '--limit', type=int, default=10, help="Set result limit")
    @magic_arguments.argument('-n', '--name', type=str, default='result', help="File or variable name for result data")
    @magic_arguments.argument('-f', '--resultformat', type=str, default='dataframe', help="Download format")
    @magic_arguments.argument('-d', '--download', action='store_true', help="Download query result")
    @magic_arguments.argument('-x', '--dsn', type=str, help="ODBC DSN")
    def odbc_sql(self, arg, cell=None):
        '''
        Run SQL Query
        :param arg: optional argument
        :param cell: SQL Query string
        :return:
        '''
        args = magic_arguments.parse_argstring(self.odbc_sql, arg)

        if not self.conn:
            if args.dsn:
                self.__connect(args.dsn)
            else:
                logging.error(
                    "Please open connection first using %dawetsql line magic or pass -x parameter followed by odbc dsn")
                return

        if args.download:
            if args.resultformat == 'dataframe':
                self.to_dataframe(cell, args.name)
                return
            elif args.resultformat == 'csv':
                self.to_csv(cell, args.name)
                return
            else:
                logging.error("unknown format for {}".format(args.resultformat))
                return

        return pandas.read_sql("SELECT * FROM ({}) T LIMIT {}".format(cell, args.limit), self.conn)

    def download(self, query):
        return pandas.read_sql(query, self.conn, chunksize=self.chunksize)

    @staticmethod
    def print_process(total):
        print("Total {} row(s) downloaded".format(total), end='\r')

    def to_csv(self, query, filename):
        result = self.download(query)
        total = 0

        for chunk in result:
            chunk.to_csv(filename + '.csv', index=False, mode='a')
            total += len(chunk)
            self.print_process(total)

    def to_dataframe(self, query, varname):
        result = self.download(query)
        df = pandas.DataFrame()

        for chunk in result:
            if len(df) == 0:
                df = chunk.copy()
            else:
                df = df.append(chunk, ignore_index=False)
            self.print_process(len(df))

        self.shell.user_ns[varname] = df

    def __del__(self):
        if self.conn:
            self.conn.close()

        self.conn = None
