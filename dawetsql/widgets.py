from IPython.display import display
from ipywidgets import Textarea, Button, HBox, VBox, Output, Dropdown, Label


class SchemaExplorer(object):

    def __init__(self, dawetsql):
        '''
        Initialize SchemaExplorer
        :param dawetsql: OdbcSqlMagics object
        '''
        self.__odbc = dawetsql
        self.out = Output()
        self.box = VBox()
        self.get_schemas()
        self.schema_list = Dropdown(options=['Choose Schema'] + self.schemas.schemaname.unique().tolist())
        self.table_list = Dropdown()
        self.table_detail = Button(description='Table Detail', button_style='success')
        self.query_area = Textarea(
            placeholder='Query',
            disabled=True
        )

        self.schema_list.observe(self.on_schema_change, names='value')
        self.table_detail.on_click(self.on_table_detail_click)

        display(Label('Schema Explorer'))
        display(HBox([self.schema_list, self.table_list, self.table_detail]))
        display(self.box)

    def get_schemas(self):
        '''
        Get database schema, table, and columns
        :return:
        '''
        query = '''SELECT 
            position,
            schemaname,
            tablename,
            name,
            javaclass
        FROM columns
        WHERE vdbname = 'DJPOLAP2'
        ORDER BY
            schemaname,
            tablename,
            position'''

        with self.out:
            self.__odbc.odbc_connect('djpolap2')
            self.schemas = self.__odbc.get_dataframe(query)
            self.__odbc.odbc_disconnect()

    def on_schema_change(self, change):
        '''
        On Schema Dropdown change callback function
        :param change: dropdown update
        :return:
        '''
        self.table_list.options = ['Choose Table'] + self.schemas[
            (self.schemas.schemaname == change['new'])].tablename.unique().tolist()

    def query_builder(self, schema, table, columns):
        '''
        Generate SQL select query
        :param schema: schema name
        :param table: table name
        :param columns: table columns
        :return: SQL select query string
        '''
        query = "SELECT \n{}".format(',\n'.join(['    {}'.format(col) for col in columns]))[:-1]
        query += "\nFROM \n    {}.{}".format(schema, table)
        return query

    def on_table_detail_click(self, arg):
        '''
        Detail Table Button callback function
        :param arg: ipython widgets default arguments
        :return:
        '''
        self.out.clear_output()
        detil = self.schemas[(self.schemas.schemaname == self.schema_list.value) & (
                self.schemas.tablename == self.table_list.value)].reset_index(drop=True)
        self.query_area.value = self.query_builder(detil.schemaname.unique()[0], detil.tablename.unique()[0],
                                                   detil.name.tolist())
        with self.out:
            display(detil)
        self.box.children = [self.query_area, self.out]