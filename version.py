import re
import sys

def update_version(file, pattern, new_version):
    with open(file, 'r') as f:
        content = f.read()

    version = pattern.findall(content)
    content = content.replace(version[0], new_version)

    with open(file, 'w') as f:
        f.write(content)

    print("File: {}, Old Version: {}, New Version: {}".format(file, version[0], new_version))

if __name__ == '__main__':
    new_version = sys.argv[1]
    pattern = re.compile(r"version[\s+='_\"]+(.*)['\"]")
    update_version('setup.py', pattern, new_version)
    update_version('dawetsql/__init__.py', pattern, new_version)
