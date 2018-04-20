# Ipython ODBC SQL Magic

Run SQL directly from Jupyter Notebook cell using ODBC without SQLAlchemy

## Installation

```bash
$ pip3 install -e git+https://gitlab.com/wakataw/ipython-dawet-sql.git#egg=ipython_dawet_sql --user
```

### Installation with spesific tag
```bash
$ pip3 install https://gitlab.com/wakataw/ipython-dawet-sql/-/archive/<tag>/ipython-dawet-sql-<tag>.zip
```

You can find available tags [here](https://gitlab.com/wakataw/ipython-dawet-sql/tags)

## Usage

### Load Extention
```
%load_ext dawetsql
```

### Database Connection

#### Open Connection Using Line Magic
```
%dawetsql dsn
```

This is optional, you can pass parameter from `%%dawetsql` cell magic while executing query.

#### Set Chunk Size

By default, `dawetsql` set chunk size to 500 rows. You can change it by passing `-c` or `--chunksize` arguments

```
%dawetsql -c 100 dsn
```


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

Query Results Preview is presented using pandas dataframe with default limit 10 rows.
You can access preview dataframe within notebook by calling `_` variable.

### Cell Magic Advance Usage

#### Start Connection and Run Query

```
%%dawetsql -x dsn
SELECT * FROM tables
WHERE somecolumn = 'somevalue'
```

#### Store Query Result to Variable

```
%%dawetsql --ouput variablename --download
SELECT * FROM tables
WHERE somecolumn = 'somevalue'
```

#### Export Query Result to CSV

```
%%dawetsql --output filename.csv --download
SELECT * FROM tables
WHERE somecolumn = 'somevalue'
```

#### Export Query Result to Pickle

```
%%dawetsql --output picklename.pkl --download
SELECT * FROM tables
WHERE somecolumn = 'somevalue'
```

## Legal

This package is released under MIT License
