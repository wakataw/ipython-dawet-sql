import unittest
import os
import platform

from dawetsql import utils

class TestDawetsqlUtils(unittest.TestCase):

    separator = os.sep

    def test_check_path_sep(self):
        path = os.sep.join(['foo', 'bar', 'bas'])

        self.assertEqual(utils.check_path_sep(path), path)

    def test_check_path_illegal_sep(self):
        if 'windows' in platform.platform().lower():
            path = 'foo\\\bar\\\bas'
        else:
            path = 'foo//bar//bas'

        self.assertNotEqual(utils.check_path_sep(path), path)

    def test_validate_variable_name(self):
        filename = 'foo'

        self.assertEqual(utils.validate_name(filename), (True, filename))

    def test_validate_csv_name(self):
        filename = 'foo.csv'

        self.assertEqual(utils.validate_name(filename), (True, filename))

    def test_validate_pickle_name(self):
        filename = 'foo.pkl'

        self.assertEqual(utils.validate_name(filename), (True, filename))

    def test_validate_unsupported_format(self):
        filename = 'foo.bar'

        self.assertEqual(utils.validate_name(filename), (True, 'foobar'))

    def test_validate_multiple_dot(self):
        filename = 'foo.bar.bas.csv'

        self.assertEqual(utils.validate_name(filename), (True, 'foobarbas.csv'))

    def test_validate_non_identifier_name(self):
        filename = '12345'

        self.assertFalse(utils.validate_name(filename)[0])

    def test_validate_name_with_subdirectory(self):
        filename = os.sep.join(['foo', 'bar', 'bas', 'qux.csv'])

        self.assertEqual(utils.validate_name(filename), (True, filename))

    def test_validate_name_with_illegal_char(self):
        filename = 'foo*bar&%#bas.csv'

        self.assertEqual(utils.validate_name(filename), (True, 'foobarbas.csv'))

    def test_limit_query(self):
        sql = '''SELECT * FROM FOO'''
        limited_sql = sql + '\nLIMIT 10'

        self.assertEqual(utils.limit_query(sql, 10), limited_sql)

    def test_limit_query_with_limit(self):
        sql = 'SELECT * FROM FOO LIMIT 100'
        limited_sql = 'SELECT * FROM FOO\nLIMIT 10'

        self.assertEqual(utils.limit_query(sql, 10), limited_sql)

if __name__ == '__main__':
    unittest.main()