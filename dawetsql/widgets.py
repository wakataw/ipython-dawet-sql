import configparser
import pandas

from IPython.display import display
from ipywidgets import Textarea, Button, HBox, VBox, Output, Dropdown, Label
from pathlib import Path
from . import  utils

WIDGET_PATH = Path.home().joinpath('.dawetsql')


class SchemaExplorer(object):

    def __init__(self, dawetsql):
        """
        Initialize SchemaExplorer
        :param dawetsql: OdbcSqlMagics object
        """
        WIDGET_PATH.mkdir(exist_ok=True)

        self.__dawetsql = dawetsql
        self.__settings = WidgetSettings()

    def show(self, force=False):
        """
        Display schema explorer widgets
        :return:
        """
        self.__out = Output()
        self.__box = VBox()
        self.__schema_list = Dropdown(options=['Choose Schema'] +
                                              self.__get_schemas(force=force).schemaname.unique().tolist())
        self.__table_list = Dropdown()
        self.__table_detail = Button(description='Table Detail', button_style='success')
        self.__generate_query = Button(description='Generate SQL', button_style='info')
        self.__data_preview = Button(description='Preview Data', button_style='primary')
        self.__query_area = Textarea(
            placeholder='Query',
            layout={'width': '100%', 'height': '500px'}
        )

        self.__schema_list.observe(self.__on_schema_change, names='value')
        self.__table_detail.on_click(self.__on_table_detail_click)
        self.__generate_query.on_click(self.__on_generate_query_click)
        self.__data_preview.on_click(self.__on_data_preview_click)

        display(Label('Schema Explorer'))
        display(HBox([self.__schema_list, self.__table_list, self.__table_detail, self.__generate_query, self.__data_preview]))
        display(self.__box)

    def __get_schemas(self, force=False):
        """
        Get database schema, table, and columns
        :return:
        """
        pickle_path = WIDGET_PATH.joinpath('schema.pkl')

        if force == False and pickle_path.is_file():
            self.__schemas = pandas.read_pickle(pickle_path)

            if not self.__schemas.empty:
                print('Schema is loaded from cache, use %explorer -f or --force to get as fresh as daisy schema')
                return self.__schemas

        with self.__out:
            self.__schemas = self.__dawetsql.get_dataframe(self.__settings.schema_query)

        self.__schemas.to_pickle(pickle_path.as_posix())

        return self.__schemas


    def __on_schema_change(self, change):
        """
        On Schema Dropdown change callback function
        :param change: dropdown update
        :return:
        """
        self.__table_list.options = ['Choose Table'] + \
                                    self.__schemas[
                                        (self.__schemas.schemaname == change['new'])
                                    ].tablename.unique().tolist()

    def __on_button_click(self, type):
        """
        Detail Table Button callback function
        :param arg: ipython widgets default arguments
        :return:
        """
        self.__out.clear_output()

        detail = self.__schemas[(self.__schemas.schemaname == self.__schema_list.value) & 
                                (self.__schemas.tablename == self.__table_list.value)].reset_index(drop=True)

        if detail.empty:
            return

        self.__query_area.value = self.__query_builder(detail.schemaname.unique()[0], detail.tablename.unique()[0],
                                                       detail.name.tolist())
        if type == 'detail':
            with self.__out:
                display(detail)
            children = self.__out
        elif type == 'preview':
            preview_query = utils.limit_query(self.__query_area.value, 10)
            preview_df = self.__dawetsql.get_dataframe(preview_query)

            with self.__out:
                display(preview_df)

            children = self.__out
        else:
            children = self.__query_area

        self.__box.children = [children]

    def __on_table_detail_click(self, arg):
        """
        Detail Table Button callback function
        :param arg: ipython widgets default arguments
        :return:
        """
        return self.__on_button_click(type='detail')

    def __on_generate_query_click(self, arg):
        return self.__on_button_click(type='query')

    def __on_data_preview_click(self, arg):
        return self.__on_button_click(type='preview')

    @staticmethod
    def __query_builder(schema, table, columns):
        """
        Generate SQL select query
        :param schema: schema name
        :param table: table name
        :param columns: table columns
        :return: SQL select query string
        """
        query = "SELECT \n{}".format(',\n'.join(['    {}'.format(col) for col in columns]))
        query += "\nFROM \n    {}.{}".format(schema, table)
        return query


class WidgetSettings(object):

    __settings_file = WIDGET_PATH.joinpath('settings.ini')
    __settings = configparser.ConfigParser()

    def __init__(self):
        if not self.__settings_file.is_file():
            self.__bootstrap()
            return

        self.__get_settings()

    def __bootstrap(self):
        query = "SELECT position, schemaname, tablename, name, javaclass " \
                "FROM columns " \
                "ORDER BY schemaname, tablename, position"

        self.__settings['QUERY'] = {'SchemaQuery': query}

        f = self.__settings_file.open(mode='w')
        self.__settings.write(f)
        f.close()

    def __get_settings(self):
        self.__settings.read(self.__settings_file.as_posix())

    @property
    def settings_file(self):
        return self.__settings_file.as_posix()

    @property
    def schema_query(self):
        return self.__settings['QUERY']['SchemaQuery']
