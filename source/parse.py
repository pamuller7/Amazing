from typing import Tuple, Any, Optional, KeysView, List
from typing_extensions import Self
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator, ValidationError
from source.graphics import drawings, themes
from source.vector2 import Vector2


class CheckedConfig(BaseModel):
    width: int = Field(ge=2, le=10_000)
    height: int = Field(ge=2, le=10_000)
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[str] = None
    alt: bool = False
    animate_generation: bool = False
    animate_shortest_way: bool = False
    interactive: bool = False
    drawing: str = "42"
    theme: str = "squeleton"

    @model_validator(mode="after")
    def entry_and_exit_must_be_in_bound(self) -> Self:
        if not self.assert_is_in_bound(Vector2.from_iter(self.entry)):
            raise ValueError(f"Entry = {self.entry} is not in bounds")
        if not self.assert_is_in_bound(Vector2.from_iter(self.exit)):
            raise ValueError(f"Exit = {self.exit} is not in bounds")
        if self.entry == self.exit:
            raise ValueError("Entry and Exit must be different")
        return self

    @model_validator(mode="after")
    def check_drawing_and_theme_attribute(self) -> Self:
        drawings_available = ["42", "smiley", "no_drawing", "pac-man"]
        theme_available = ["red", "green", "squeleton", "rgb"]
        if self.drawing not in drawings_available:
            raise ValueError(
                "The drawing {} doesn't exist, \
                    please choose one among {}".format(
                    self.drawing, drawings_available
                )
            )
        if self.theme not in theme_available:
            raise ValueError(
                "The theme {} doesn't exist, \
                    please choose one among {}".format(
                    self.theme, theme_available
                )
            )
        return self

    def assert_is_in_bound(self, pos: Vector2) -> bool:
        return (
            pos.x >= 0
            and pos.x < self.width
            and pos.y >= 0
            and pos.y < self.height
        )


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

    def apply(self, pr: CheckedConfig) -> None:
        setattr(pr, self.key_name.lower(), self.value)


class ArgParser(ABC):
    @abstractmethod
    def parse(self, str: str, line_number: int) -> Any | ParseError:
        pass


class KeyParser:
    def __init__(self, key_name: str, arg: ArgParser) -> None:
        self.key_name = key_name
        self.arg = arg

    def accepts(self, line: str) -> bool:
        return line.upper().startswith(f"{self.key_name}=")

    def parse(
        self, line: str, line_number: int
    ) -> KeyParseResult | ParseError:
        line = line[len(f"{self.key_name}="):]
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
        str = str.strip()
        if len(str) == 0 or str.isspace():
            return ParseError(
                line_number,
                f"`{str!r}` is empty \
or space only, please use a valid name",
            )
        return str


class BoolParser(ArgParser):
    def parse(self, str: str, line_number: int) -> ParseError | bool:
        str = str.strip().replace(" ", "")
        if str == "True":
            return True
        elif str == "False":
            return False
        return ParseError(line_number, f"`{str}` should be `True` or `False`")


class DictKeysParser(ArgParser):
    def __init__(self, allowed: KeysView) -> None:
        self.allowed: List[str] = list(allowed)

    def parse(self, str: str, line_number: int) -> ParseError | str:
        str = str.strip().replace(" ", "")
        if str not in self.allowed:
            return ParseError(
                line_number, f"`{str}` is not in valid keys: {self.allowed}"
            )
        return str


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
    [ANIMATE_GENERATION=<bool>]
    [ANIMATE_SHORTEST_WAY=<bool>]
    ```
    and parses it into a ParseResult.

    empty lines and lines starting with `#` are ignored.

    raises a ValueError if string is not valid.
    """

    extractors: list[KeyParser] = [
        KeyParser("WIDTH", IntParser()),
        KeyParser("HEIGHT", IntParser()),
        KeyParser("ENTRY", TupleIntParser()),
        KeyParser("EXIT", TupleIntParser()),
        KeyParser("OUTPUT_FILE", IdentParser()),
        KeyParser("PERFECT", BoolParser()),
        OptKeyParser("ALT", BoolParser()),
        OptKeyParser("SEED", IdentParser()),
        OptKeyParser("ANIMATE_GENERATION", BoolParser()),
        OptKeyParser("ANIMATE_SHORTEST_WAY", BoolParser()),
        OptKeyParser("INTERACTIVE", BoolParser()),
        OptKeyParser("DRAWING", DictKeysParser(drawings.keys())),
        OptKeyParser("THEME", DictKeysParser(themes.keys())),
    ]

    @classmethod
    def interactable_extractors(cls) -> list[KeyParser]:
        return [
            KeyParser("PERFECT", BoolParser()),
            OptKeyParser("ALT", BoolParser()),
            OptKeyParser("SEED", IdentParser()),
            OptKeyParser("ANIMATE_GENERATION", BoolParser()),
            OptKeyParser("ANIMATE_SHORTEST_WAY", BoolParser()),
            OptKeyParser("DRAWING", DictKeysParser(drawings.keys())),
            OptKeyParser("THEME", DictKeysParser(themes.keys())),
        ]

    @classmethod
    def parse(cls, txt: str) -> CheckedConfig:
        extractors: list[KeyParser] = cls.extractors.copy()
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
                    errors.append(
                        ParseError(
                            i,
                            f"key '{line}' \
not recognized",
                        )
                    )

        def to_leftover_err(kp: KeyParser) -> str:
            return f"Key: {kp.key_name} was not found"

        def is_not_opt(kp: KeyParser) -> bool:
            return not isinstance(kp, OptKeyParser)

        leftover = list(map(to_leftover_err, filter(is_not_opt, extractors)))
        if len(errors) != 0 or len(leftover) != 0:
            sep = "\n" if len(errors) != 0 and len(leftover) != 0 else ""
            raise ValueError(
                "\n".join(map(str, errors)) + sep + "\n".join(leftover)
            )
        pr = CheckedConfig.model_construct()
        for k in results:
            k.apply(pr)
        try:
            pr = CheckedConfig(**vars(pr))
            return pr
        except ValidationError as e:
            raise ValueError(e.errors()[0]["msg"])
