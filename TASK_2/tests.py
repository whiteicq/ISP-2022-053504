import unittest
import json
from serializers.yaml import YAML
from serializers.toml import TOML
from serializers.json import JSON
from parser import ComplexSerializer
from test_data import fact, Test


class SerializersTest(unittest.TestCase):

    def test_toml(self):
        serializer = ComplexSerializer(TOML())
        fact_data = serializer.dumps(fact)
        test_data = serializer.dumps(Test)
        fact_result = serializer.loads(fact_data)
        test_result = serializer.loads(test_data)
        t1 = test_result(1, 2)
        t2 = Test(1, 2)
        self.assertEqual((fact_result(5), t1.a, t1.b, t1.print_hello()), (fact(5), t2.a, t2.b, t2.print_hello()))

    def test_yaml(self):
        serializer = ComplexSerializer(YAML())
        fact_data = serializer.dumps(fact)
        test_data = serializer.dumps(Test)
        fact_result = serializer.loads(fact_data)
        test_result = serializer.loads(test_data)
        t1 = test_result(1, 2)
        t2 = Test(1, 2)
        self.assertEqual((fact_result(5), t1.a, t1.b, t1.print_hello()), (fact(5), t2.a, t2.b, t2.print_hello()))

    def test_json(self):
        serializer = ComplexSerializer(JSON())
        fact_data = serializer.dumps(fact)
        test_data = serializer.dumps(Test)
        fact_result = serializer.loads(fact_data)
        test_result = serializer.loads(test_data)
        t1 = test_result(1, 2)
        t2 = Test(1, 2)
        self.assertEqual((fact_result(5), t1.a, t1.b, t1.print_hello()), (fact(5), t2.a, t2.b, t2.print_hello()))


if __name__ == "__main__":
    unittest.main()
