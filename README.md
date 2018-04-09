# Ipython ODBC SQL Magic

Run SQL directly from Jupyter Notebook cell using ODBC without SQLAlchemy

## Installation

```bash
$ pip3 install -e git+https://gitlab.com/wakataw/ipython-odbc-sql.git
```

## Usage

### Load Extention
```
%load_ext odbc_sql
```

### Database Connection

#### Open Connection Using Line Magic
```
%dawetsql dsn
```

This is optional, you can pass parameter from `%%dawetsql` cell magic while executing query.

#### Close Connection

```
%dawetsqlclose
```

### Run SQL Query

```
%%dawetsql
SELECT * FROM tables
WHERE somecolumn = 'somevalue'
```

Query Results is presented using pandas dataframe with default limit 10 rows.

### Cell Magic Advance Usage

#### Start Connection and Run Query

```
%%dawetsql -x dsn
SELECT * FROM tables
WHERE somecolumn = 'somevalue'
```

#### Store Query Result to Variable

```
%%dawetsql --name=result_df
SELECT * FROM tables
WHERE somecolumn = 'somevalue'
```

#### Export Query Result to CSV

```
%%dawetsql --name=csvfilename.csv --resultformat=csv
SELECT * FROM tables
WHERE somecolumn = 'somevalue'
```

## Legal

This package is released under MIT License
