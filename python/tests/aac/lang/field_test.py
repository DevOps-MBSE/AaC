import unittest
from aac.lang.field import Field

class TestField(unittest.TestCase):
    def test_required_field(self):
        field = Field(name='my_field', type='string', is_required=True)
        self.assertEqual(field.name, 'my_field')
        self.assertEqual(field.type, 'string')
        self.assertEqual(field.is_required, True)

    def test_optional_field(self):
        field = Field(name='my_field', type='int', is_required=False)
        self.assertEqual(field.name, 'my_field')
        self.assertEqual(field.type, 'int')
        self.assertEqual(field.is_required, False)

    def test_list_field(self):
        field = Field(name='my_field', type='string[]', is_required=True)
        self.assertEqual(field.name, 'my_field')
        self.assertEqual(field.type, 'string[]')
        self.assertEqual(field.is_required, True)

    def test_custom_type_list_field(self):
        field = Field(name='my_field', type='MyType[]', is_required=True)
        self.assertEqual(field.name, 'my_field')
        self.assertEqual(field.type, 'MyType[]')
        self.assertEqual(field.is_required, True)

    def test_from_dict(self):
        field_dict = {
            'name': 'my_field',
            'type': 'string',
            'is_required': True
        }
        field = Field.from_dict(field_dict)
        self.assertEqual(field.name, 'my_field')
        self.assertEqual(field.type, 'string')
        self.assertEqual(field.is_required, True)

    def test_from_dict_list_field(self):
        field_dict = {
            'name': 'my_field',
            'type': 'string[]',
            'is_required': True
        }
        field = Field.from_dict(field_dict)
        self.assertEqual(field.name, 'my_field')
        self.assertEqual(field.type, 'string[]')
        self.assertEqual(field.is_required, True)

    def test_from_dict_custom_type_list_field(self):
        field_dict = {
            'name': 'my_field',
            'type': 'MyType[]',
            'is_required': True,
        }
        field = Field.from_dict(field_dict)
        self.assertEqual(field.name, 'my_field')
        self.assertEqual(field.type, 'MyType[]')
        self.assertEqual(field.is_required, True)

if __name__ == '__main__':
    unittest.main()