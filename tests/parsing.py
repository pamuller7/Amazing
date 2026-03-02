from unittest import TestCase
from source.parse import Parser
from pydantic import ValidationError


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
            self.fail("should fail with bas bool")
        except ValueError as v:
            pass

    def test_too_big(self):
        txt = """WIDTH=14000
                 HEIGHT=5
                 ENTRY=6,7
                 EXIT=0,9
                 OUTPUT_FILE=x
                 PERFECT=True
                 """
        try:
            Parser.parse(txt)
            self.fail("should fail with too large")
        except ValidationError as v:
            pass

    def test_outside(self):
        txt = """WIDTH=14
                 HEIGHT=5
                 ENTRY=14,7
                 EXIT=0,9
                 OUTPUT_FILE=x
                 PERFECT=True
                 """
        try:
            Parser.parse(txt)
            self.fail("should fail with outside")
        except ValidationError as v:
            pass

    def test_good_data(self):
        txt = """WIDTH=7
                 HEIGHT=8
                 ENTRY=1,2
                 EXIT=3,0
                 OUTPUT_FILE=x
                 PERFECT=True
                 """
        try:
            ret = Parser.parse(txt)
            self.assertEqual(ret.width, 7)
            self.assertEqual(ret.height, 8)
            self.assertEqual(ret.entry, (1, 2))
            self.assertEqual(ret.exit, (3, 0))
            self.assertEqual(ret.output_file, "x")
            self.assertEqual(ret.perfect, True)
            self.assertEqual(ret.seed, None)
        except ValueError as v:
            self.fail("should parse succesfully")

    def test_good_data_with_seed(self):
        txt = """WIDTH=7
                 HEIGHT=8
                 ENTRY=1,2
                 EXIT=3,0
                 OUTPUT_FILE=x
                 PERFECT=True
                 SEED=eyyeyeye
                 """
        try:
            ret = Parser.parse(txt)
            self.assertEqual(ret.width, 7)
            self.assertEqual(ret.height, 8)
            self.assertEqual(ret.entry, (1, 2))
            self.assertEqual(ret.exit, (3, 0))
            self.assertEqual(ret.output_file, "x")
            self.assertEqual(ret.perfect, True)
            self.assertEqual(ret.seed, "eyyeyeye")
        except ValidationError as v:
            print("HERE")
            for k in v.errors():
                print(k["msg"])

            # self.fail(v)
