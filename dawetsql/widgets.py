from ipywidgets import Textarea, Layout, Button, HBox, VBox, Output, Dropdown, Label


class SchemaExplorer(object):
    __query = '''SELECT 
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

    def __init__(self, dawetsql):
        self.__odbc = dawetsql
        self.out = Output()
        self.box = VBox()
        self.get_dbschema()
        self.schema_name = Dropdown(options=['Pilih Schema'] + self.dbschema.schemaname.unique().tolist())
        self.tables_name = Dropdown()
        self.detil_table = Button(description='Detil Table', button_style='success')
        self.query_area = Textarea(
            placeholder='Query',
            disabled=True
        )

        self.schema_name.observe(self.on_schema_change, names='value')
        self.detil_table.on_click(self.on_detiltable_click)

        display(Label('Schema Explorer'))
        display(HBox([self.schema_name, self.tables_name, self.detil_table]))
        display(self.box)

    def get_dbschema(self):
        with self.out:
            self.__odbc.odbc_connect('djpolap2')
            self.dbschema = self.__odbc.get_dataframe(self.__query)
            self.__odbc.odbc_disconnect()

    def on_schema_change(self, change):
        self.tables_name.options = ['Pilih Table'] + self.dbschema[
            (self.dbschema.schemaname == change['new'])].tablename.unique().tolist()

    def query_builder(self, schema, table, columns):
        query = "SELECT \n{}".format(',\n'.join(['    {}'.format(col) for col in columns]))[:-1]
        query += "\nFROM \n    {}.{}".format(schema, table)
        return query

    def on_detiltable_click(self, arg):
        self.out.clear_output()
        detil = self.dbschema[(self.dbschema.schemaname == self.schema_name.value) & (
                    self.dbschema.tablename == self.tables_name.value)].reset_index(drop=True)
        self.query_area.value = self.query_builder(detil.schemaname.unique()[0], detil.tablename.unique()[0],
                                                   detil.name.tolist())
        with self.out:
            display(detil)
        self.box.children = [self.query_area, self.out]