import math
import unittest
import sys
from ..test_data import Test
from serializers.json import JSON
from .__init__ import ComplexSerializer
from ..test_module import _t

sys.path.append("..")


class ParserTest(unittest.TestCase):

    def test_instance(self):
        inst = Test(1, 2)

        parser = ComplexSerializer(JSON(), inst)

        inst = parser.t
        inst2 = Test(1, 2)

        self.assertEqual((inst.a, inst.b, inst.print_hello()),
                         (inst2.a, inst2.b, inst2.print_hello()))

    def test_class(self):
        parser = ComplexSerializer(JSON(), Test)
        t1 = Test(1, 2)
        t2 = parser.t(1, 2)
        self.assertEqual((t1.a, t1.b, t1.print_hello()),
                         (t2.a, t1.b, t2.print_hello()))

    def test_function(self):
        parser = ComplexSerializer(JSON(), _t)
        self.assertEqual(parser.t(2), math.sin(2*123*2*5))


if __name__ == "__main__":
    unittest.main()
