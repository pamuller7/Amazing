from unittest import TestCase
from source.parse import Parser


class ParsingTests(TestCase):
    def test_empty(self):
        txt = """"""
        try:
            Parser.parse(txt)
            self.fail("should raise Value Error with missing keys")
        except ValueError as v:
            pass

    def test_missing_key(self):
        txt = """WIDTH=4
                 HEIGHT=5
                 ENTRY=6,7
                 OUTPUT_FILE=x
                 PERFECT=True
                 """
        try:
            Parser.parse(txt)
            self.fail("should fail with missing key")
        except ValueError as v:
            pass

    def test_bad_int_value(self):
        txt = """WIDTH=4
                 HEIGHT=ewr
                 ENTRY=6,7
                 EXIT=0,9
                 OUTPUT_FILE=x
                 PERFECT=True
                 """
        try:
            Parser.parse(txt)
            self.fail("should fail with bad int value")
        except ValueError as v:
            pass

    def test_bad_bool_value(self):
        txt = """WIDTH=4
                 HEIGHT=5
                 ENTRY=6,7
                 EXIT=0,9
                 OUTPUT_FILE=x
                 PERFECT=Treue
                 """
        try:
            Parser.parse(txt)
            self.fail("should fail with missing key")
        except ValueError as v:
            pass

    def test_good_data(self):
        txt = """WIDTH=4
                 HEIGHT=5
                 ENTRY=6,7
                 EXIT=8,9
                 OUTPUT_FILE=x
                 PERFECT=True
                 """
        try:
            ret = Parser.parse(txt)
            self.assertEqual(ret.width, 4)
            self.assertEqual(ret.height, 5)
            self.assertEqual(ret.entry, (6, 7))
            self.assertEqual(ret.exit, (8, 9))
            self.assertEqual(ret.output_file, "x")
            self.assertEqual(ret.perfect, True)
            self.assertEqual(ret.seed, None)
        except ValueError as v:
            self.fail("should parse succesfully")

    def test_good_data_with_seed(self):
        txt = """WIDTH=4
                 HEIGHT=5
                 ENTRY=6,7
                 EXIT=8,9
                 OUTPUT_FILE=x
                 PERFECT=True
                 SEED=eyyeyeye
                 """
        try:
            ret = Parser.parse(txt)
            self.assertEqual(ret.width, 4)
            self.assertEqual(ret.height, 5)
            self.assertEqual(ret.entry, (6, 7))
            self.assertEqual(ret.exit, (8, 9))
            self.assertEqual(ret.output_file, "x")
            self.assertEqual(ret.perfect, True)
            self.assertEqual(ret.seed, "eyyeyeye")
        except ValueError as v:
            self.fail("should parse the file succesfully")
