import logging
import pypyodbc
import sys

from pandas import DataFrame, read_sql, concat
from IPython.core import magic_arguments
from IPython.core.magic import magics_class, Magics, line_magic, cell_magic
from dawetsql.widgets import SchemaExplorer
from . import utils
from cryptography.fernet import Fernet


@magics_class
class OdbcSqlMagics(Magics):
    conn = None
    chunksize = 500
    reconnect = False
    max_retry = 3
    retry = 0
    __user = None
    __password = None
    __dsn = None
    __conn_string = None

    def __init__(self, *args, **kwargs):
        super(OdbcSqlMagics, self).__init__(*args, **kwargs)

    def __connect(self, dsn, username, password, connection_string, verbose=True):
        """
        Open database connection
        :param dsn: ODBC DSN
        :return:
        """
        try:
            if connection_string:
                self.conn = pypyodbc.connect(connection_string)
            else:
                self.conn = pypyodbc.connect("DSN={};Username={};Password={}".format(dsn, username, password))
            if self.conn and verbose:
                    print("Connected to {}".format(dsn))
        except Exception as e:
            logging.error(e)
            return

    @line_magic('dawetsql')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-u', '--user', type=str, help="Dawet User")
    @magic_arguments.argument('-p', '--password', type=str, help="Dawet Password")
    @magic_arguments.argument('-d', '--dsn', type=str, help="Dawet DSN")
    @magic_arguments.argument('-x', '--connection', type=str, help="ODBC Connection String")
    @magic_arguments.argument('-c', '--chunksize', type=int, default=100, help="ODBC Fetch size")
    @magic_arguments.argument('-a', '--reconnect', action='store_true', help='Auto Reconnect')
    @magic_arguments.argument('-r', '--retry', type=int, default=3, help='Max Retry')
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
        self.max_retry = args.retry

        if args.reconnect:
            self.reconnect = True
            self.chipper = self.generate_chipper()
            self.__dsn = args.dsn
            self.__user = args.user
            
            if args.password:
                self.__password = self.chipper.encrypt(args.password.encode('utf8'))

            if args.connection:
                self.__conn_string = self.chipper.encrypt(args.connection.encode('utf8'))
            else:
                self.__conn_string = False

        return self.__connect(args.dsn, args.user, args.password, args.connection)

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

    @line_magic('dawetsqlreconnect')
    def odbc_reconnect(self, args=None, cell=None):
        if not self.reconnect:
            logging.error("You did not use reconnect arguments, try re initialize dawetsql with -a/--reconnect argument")
            return

        self.odbc_disconnect()

        if self.__conn_string:
            connection_string = self.chipper.decrypt(self.__conn_string).decode('utf8')
        else:
            connection_string = False
        
        if self.__password:
            password = self.chipper.decrypt(self.__password).decode('utf8')
        else:
            password = None

        return self.__connect(self.__dsn, self.__user, password, connection_string, verbose=False)

    @cell_magic('dawetsql')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-l', '--limit', type=int, default=10, help="Set result limit")
    @magic_arguments.argument('-o', '--ouput', default='_', type=str, help="File or Variable name for results data")
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
        query = ' '.join(cell.strip().split())

        if not ok:
            logging.error("Cannot proceed with `{}` as output name".format(varname))
            return

        if not self.conn:
            logging.error(
                "Please open connection first using %dawetsql line magic")
            return

        if valid_name != '_':
            if valid_name.lower().endswith('.csv'):
                self.to_csv(query, valid_name)
                return
            elif valid_name.lower().endswith('.pkl'):
                self.to_pickle(query, valid_name)
                return
            else:
                self.to_dataframe(query, valid_name, download=True)
                return

        return self.to_dataframe(utils.limit_query(query, args.limit), valid_name)

    def download(self, query):
        utils.log_query(self.__user, query)
        data = None
        try:
            data = read_sql(query, self.conn, chunksize=self.chunksize)
        except Exception as e:
            logging.error(e.__class__.__name__)
            logging.error(e)

            if utils.teiid_resource_exception.findall(str(e)) and self.reconnect:
                if self.retry >= self.max_retry:
                    self.retry = 0
                    raise Exception('Max Retry Exception')

                self.retry += 1
                self.odbc_reconnect()
                return self.download(query)
            else:
                raise e

        return data

    def get_dataframe(self, query, verbose=True):
        """
        Store query result to dataframe
        :param query: SQL Query
        :return: pandas dataframe
        :verbose: print process to stdout
        """
        print("Fetching result", flush=True) if verbose else None

        result = self.download(query)

        if result is None:
            return

        total = 0
        df_list = []

        for chunk in result:
            df_list.append(chunk)
            total += len(chunk)
            self.print_process(total) if verbose else None

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

        if result is None:
            return

        total = 0
        header = True

        for chunk in result:
            if header:
                mode = 'w'
            else:
                mode = 'a'
            chunk.to_csv(filename, index=False, mode=mode, header=header)
            total += len(chunk)
            self.print_process(total)
            header = False

    def to_dataframe(self, query, varname, download=False):
        """
        Store dataframe to shell variable
        :param query: SQL query
        :param varname: Dataframe variable name
        :param download: Download or just preview query result
        :return:
        """
        df = self.get_dataframe(query)

        if df is None:
            return

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

        if df is None:
            return

        df.to_pickle(pickle_name)

    @line_magic('explorer')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-f', '--force', action='store_true', help="Force explorer to re-index schema")
    def explore_schema(self, arg):
        """
        Display schema explorer widgets
        :return:
        """
        args = magic_arguments.parse_argstring(self.explore_schema, arg)

        print('Fetching schema detail..')

        explorer = SchemaExplorer(self)
        explorer.show(force=args.force)

    @staticmethod
    def generate_chipper():
        return Fernet(Fernet.generate_key())

    @staticmethod
    def print_process(total):
        sys.stdout.write("\rTotal {} row(s) downloaded".format(total))
        sys.stdout.flush()

    def __del__(self):
        if self.conn:
            self.conn.close()

        self.conn = None
