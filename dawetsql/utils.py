import re

cleanser = re.compile(r'\s+|"|\'')
alphanum = re.compile(r'[a-zA-Z0-9_]')
alphanum_name = lambda x: ''.join(alphanum.findall(x))

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
