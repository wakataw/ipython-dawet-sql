import logging
import pyodbc
import sys

from pandas import DataFrame, read_sql, concat
from IPython.core import magic_arguments
from IPython.core.magic import magics_class, Magics, line_magic, cell_magic
from . import utils


@magics_class
class OdbcSqlMagics(Magics):
    conn = None
    chunksize = 500

    def __init__(self, *args, **kwargs):
        super(OdbcSqlMagics, self).__init__(*args, **kwargs)

    def __connect(self, dsn):
        """
        Open database connection
        :param dsn: ODBC DSN
        :return:
        """
        try:
            self.conn = pyodbc.connect("DSN={}".format(dsn))
            if self.conn:
                print("Connected to {}".format(dsn))
        except Exception as e:
            logging.error(e)
            return

    @line_magic('dawetsql')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-c', '--chunksize', type=int, default=100, help="ODBC Fetch size")
    @magic_arguments.argument('dsn', type=str, help="ODBC DSN")
    def odbc_connect(self, arg):
        """
        Open Database Connection line magic method
        :param arg: ODBC DSN
        :return:
        """
        if self.conn:
            self.odbc_disconnect()

        args = magic_arguments.parse_argstring(self.odbc_connect, arg)

        self.chunksize = args.chunksize

        return self.__connect(args.dsn)

    @line_magic('dawetsqlclose')
    def odbc_disconnect(self, *args, **kwargs):
        """
        Close Database Connection line magic method
        :return:
        """
        try:
            self.conn.close()
            print("Disconnected")
        except:
            pass
        finally:
            self.conn = None
            return

    @cell_magic('dawetsql')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-l', '--limit', type=int, default=10, help="Set result limit")
    @magic_arguments.argument('-x', '--dsn', type=str, help="ODBC DSN")
    @magic_arguments.argument('-o', '--ouput', default='_', type=str, help="File or Variable name for results data")
    @magic_arguments.argument('-d', '--download', action='store_true', help="Download query result")
    def odbc_sql(self, arg, cell=None):
        """
        Run SQL Query
        :param arg: optional argument
        :param cell: SQL Query string
        :return:
        """
        args = magic_arguments.parse_argstring(self.odbc_sql, arg)
        varname = args.ouput.strip()

        ok, valid_name = utils.validate_name(varname)

        if not ok:
            logging.error("Cannot proceed with `{}` as output name".format(varname))
            return

        if not self.conn:
            if args.dsn:
                self.__connect(args.dsn)
            else:
                logging.error(
                    "Please open connection first using %dawetsql line magic or pass -x parameter followed by odbc dsn")
                return

        if args.download:
            if valid_name.lower().endswith('.csv'):
                self.to_csv(cell, valid_name)
                return
            elif valid_name.lower().endswith('.pkl'):
                self.to_pickle(cell, valid_name)
                return
            else:
                self.to_dataframe(cell, valid_name, download=True)
                return

        return self.to_dataframe("SELECT * FROM ({}) T LIMIT {}".format(cell, args.limit), valid_name)

    def download(self, query):
        return read_sql(query, self.conn, chunksize=self.chunksize)

    @staticmethod
    def print_process(total):
        sys.stdout.write("\rTotal {} row(s) downloaded".format(total))
        sys.stdout.flush()

    def get_dataframe(self, query):
        """
        Store query result to dataframe
        :param query: SQL Query
        :return: pandas dataframe
        """
        print("Fetching result", flush=True)
        result = self.download(query)
        total = 0
        df_list = []

        for chunk in result:
            df_list.append(chunk)
            total += len(chunk)
            self.print_process(total)

        if df_list:
            df = concat(df_list, ignore_index=True)
            return df

        return DataFrame()

    def to_csv(self, query, filename):
        """
        Export query result to csv
        :param query: SQL Query
        :param filename: csv filename
        :return:
        """
        result = self.download(query)
        total = 0

        for chunk in result:
            chunk.to_csv(filename, index=False, mode='a')
            total += len(chunk)
            self.print_process(total)

    def to_dataframe(self, query, varname, download=False):
        """
        Store dataframe to shell variable
        :param query: SQL query
        :param varname: Dataframe variable name
        :param download: Download or just preview query result
        :return:
        """
        df = self.get_dataframe(query)
        self.shell.user_ns[varname] = df
        if not download:
            return df

    def to_pickle(self, query, pickle_name):
        """
        Export query result to python pickle
        :param query: SQL Query
        :param pickle_name: pickle file name
        :return:
        """
        df = self.get_dataframe(query)
        df.to_pickle(pickle_name)

    def __del__(self):
        if self.conn:
            self.conn.close()

        self.conn = None
