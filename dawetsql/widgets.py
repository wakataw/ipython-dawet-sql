import configparser

from IPython.display import display
from ipywidgets import Textarea, Button, HBox, VBox, Output, Dropdown, Label
from pathlib import Path

WIDGET_PATH = Path.home().joinpath('.dawetsql')


class SchemaExplorer(object):

    def __init__(self, dawetsql):
        """
        Initialize SchemaExplorer
        :param dawetsql: OdbcSqlMagics object
        """
        self.__dawetsql = dawetsql
        WIDGET_PATH.mkdir(exist_ok=True)

    def show(self):
        """
        Display schema explorer widgets
        :return:
        """
        self.__out = Output()
        self.__box = VBox()
        self.__schema_list = Dropdown(options=['Choose Schema'] + self.__get_schemas().schemaname.unique().tolist())
        self.__table_list = Dropdown()
        self.__table_detail = Button(description='Table Detail', button_style='success')
        self.__query_area = Textarea(
            placeholder='Query',
            disabled=True
        )

        self.__schema_list.observe(self.__on_schema_change, names='value')
        self.__table_detail.on_click(self.__on_table_detail_click)

        display((Label('Schema Explorer'),))
        display((HBox([self.__schema_list, self.__table_list, self.__table_detail]),))
        display((self.__box,))

    def __get_settings(self):
        """
        Get widget setting from external file
        :return:
        """
        self.__settings = WidgetSettings()

    def __get_schemas(self):
        """
        Get database schema, table, and columns
        :return:
        """

        # TODO: cache schema dataframe

        with self.__out:
            self.__schemas = self.__dawetsql.get_dataframe(self.__settings.schema_query)

        return self.__schemas

    def __on_schema_change(self, change):
        """
        On Schema Dropdown change callback function
        :param change: dropdown update
        :return:
        """
        self.__table_list.options = ['Choose Table'] + self.__schemas[
            (self.__schemas.schemaname == change['new'])].tablename.unique().tolist()

    def __on_table_detail_click(self, arg):
        """
        Detail Table Button callback function
        :param arg: ipython widgets default arguments
        :return:
        """
        self.__out.clear_output()
        detil = self.__schemas[(self.__schemas.schemaname == self.__schema_list.value) & (
                self.__schemas.tablename == self.__table_list.value)].reset_index(drop=True)
        self.__query_area.value = self.__query_builder(detil.schemaname.unique()[0], detil.tablename.unique()[0],
                                                       detil.name.tolist())
        with self.__out:
            display(detil)
        self.__box.children = [self.__query_area, self.__out]

    @staticmethod
    def __query_builder(schema, table, columns):
        """
        Generate SQL select query
        :param schema: schema name
        :param table: table name
        :param columns: table columns
        :return: SQL select query string
        """
        query = "SELECT \n{}".format(',\n'.join(['    {}'.format(col) for col in columns]))[:-1]
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
