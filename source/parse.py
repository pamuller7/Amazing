from typing import Tuple, Any
from abc import ABC, abstractmethod


class ParseResult:
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: None | str

    def __init__(self) -> None:
        self.seed = None


class ParseError:
    def __init__(self, line_number: int, msg: str) -> None:
        self.line_number = line_number
        self.msg = msg

    def __str__(self) -> str:
        return f"line {self.line_number} -- {self.msg}"


class KeyParseResult:
    def __init__(self, key_name: str, value: Any) -> None:
        self.key_name = key_name
        self.value = value

    def apply(self, pr: ParseResult):
        setattr(pr, self.key_name.lower(), self.value)


class ArgParser(ABC):
    @abstractmethod
    def parse(self, str: str, line_number: int) -> Any | ParseError:
        pass


class KeyParser:
    def __init__(self, key_name: str, arg: ArgParser) -> None:
        self.key_name = key_name
        self.arg = arg

    def accepts(self, line: str):
        return line.startswith(f"{self.key_name}=")

    def parse(
        self, line: str, line_number: int
    ) -> KeyParseResult | ParseError:
        line = line[len(f"{self.key_name}=") :]
        ret = self.arg.parse(line, line_number)
        if isinstance(ret, ParseError):
            return ParseError(line_number, f"Key: {self.key_name} : {ret.msg}")
        return KeyParseResult(self.key_name, ret)


class OptKeyParser(KeyParser):
    pass


class IntParser(ArgParser):
    def parse(self, str: str, line_number: int) -> ParseError | int:
        try:
            return int(str)
        except ValueError:
            return ParseError(line_number, f"string {str} is not an integer")


class TupleIntParser(ArgParser):
    def parse(
        self, str: str, line_number: int
    ) -> ParseError | Tuple[int, int]:
        numbers = str.split(",")
        if len(numbers) != 2:
            return ParseError(
                line_number,
                "Did not find precisely two comma separeted elements",
            )
        try:
            return (int(numbers[0]), int(numbers[1]))
        except ValueError:
            return ParseError(
                line_number, f"at least oneof {str} is not an integer"
            )


class IdentParser(ArgParser):
    def parse(self, str: str, line_number: int) -> ParseError | str:
        if len(str) == 0 or str.isspace():
            return ParseError(line_number, f"`{str!r}` is empty or space only")
        return str


class BoolParser(ArgParser):
    def parse(self, str: str, line_number: int) -> ParseError | bool:
        if str == "True":
            return True
        elif str == "False":
            return False
        return ParseError(line_number, f"`{str}` should be `True` or `False`")


class Parser:
    """Receives a string of the form:
    ```
    WIDTH=<int>
    HEIGHT=<int>
    ENTRY=<int>,<int>
    EXIT=<int>,<int>
    OUTPUT_FILE=<filename>
    PERFECT=True|False
    [SEED=<str>]
    ```
    and parses it into a ParseResult.

    empty lines and lines starting with `#` are ignored.

    raises a ValueError if string is not valid.
    """

    @staticmethod
    def parse(txt: str):
        extractors: list[KeyParser] = [
            KeyParser("WIDTH", IntParser()),
            KeyParser("HEIGHT", IntParser()),
            KeyParser("ENTRY", TupleIntParser()),
            KeyParser("EXIT", TupleIntParser()),
            KeyParser("OUTPUT_FILE", IdentParser()),
            KeyParser("PERFECT", BoolParser()),
            OptKeyParser("SEED", IdentParser()),
        ]
        errors = []
        results = []
        for i, line in enumerate(map(str.strip, txt.splitlines())):
            extracted = False
            if line.startswith("#") or line.isspace() or len(line) == 0:
                continue
            for extractor in extractors:
                if extractor.accepts(line):
                    extracted = True
                    res = extractor.parse(line, i)
                    if isinstance(res, ParseError):
                        errors.append(res)
                    else:
                        results.append(res)
                    extractors.remove(extractor)
                    break
            if not extracted:
                if len(extractors) == 0:
                    errors.append(ParseError(i, "All keys were parsed"))
                else:
                    errors.append(ParseError(i, "key not recognized"))

        def to_leftover_err(kp: KeyParser) -> str:
            return f"Key: {kp.key_name} was not found"

        def is_not_opt(kp: KeyParser):
            return not isinstance(kp, OptKeyParser)

        leftover = list(map(to_leftover_err, filter(is_not_opt, extractors)))
        if len(errors) != 0 or len(leftover) != 0:
            sep = "\n" if len(errors) != 0 and len(leftover) != 0 else ""
            raise ValueError(
                "\n".join(map(str, errors)) + sep + "\n".join(leftover)
            )
        pr = ParseResult()
        print(str(pr))
        for k in results:
            k.apply(pr)
        return pr
