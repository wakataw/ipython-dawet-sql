import re
import csv
from datetime import datetime
from pathlib import Path

cleanser = re.compile(r'\s+|"|\'')
alphanum = re.compile(r'[a-zA-Z0-9_]')
alphanum_name = lambda x: ''.join(alphanum.findall(x))
query_pattern = re.compile(r'(.*)LIMIT\s+\d+$', flags=re.DOTALL|re.I)
widget_path = Path.home().joinpath('.dawetsql')

def validate_name(varname):
    valid_name = cleanser.sub('', varname)

    if valid_name.lower().endswith('.csv') or valid_name.lower().endswith('.pkl'):
        _valid_name = valid_name.split('.')
        filetype = _valid_name[-1]
        filename = alphanum_name(''.join(_valid_name[:-1]))

        if filename == '':
            return False, valid_name

        return True, "{}.{}".format(filename, filetype)

    else:
        valid_name = alphanum_name(valid_name)
        if valid_name.isidentifier():
            return True, valid_name
        else:
            return False, varname

def limit_query(query, limit):
    is_limited = query_pattern.findall(query)

    if is_limited:
        query = is_limited[0]

    return query.strip() + '\nLIMIT {}'.format(limit)

def log_query(user, query):
    query = ' '.join([i for i in query.strip().split('\n') if i.strip() != ''])
    with open(str(widget_path.joinpath('query.log')), 'a', newline='') as f:
        writer = csv.writer(f, delimiter='|', quoting=csv.QUOTE_ALL)
        writer.writerow([user, query, str(datetime.now())])
