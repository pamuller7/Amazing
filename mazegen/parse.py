from typing import Tuple, Any, Optional, KeysView, List
from typing_extensions import Self
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator, ValidationError
from mazegen.graphics import drawings, themes
from mazegen.vector2 import Vector2


class CheckedConfig(BaseModel):
    """Validated configuration for a maze generation run.

    All fields are validated by Pydantic; cross-field invariants are
    enforced by the ``model_validator`` methods below.

    Attributes:
        width: Number of columns in the maze (2-1000).
        height: Number of rows in the maze (2-1000).
        entry: ``(x, y)`` grid coordinate of the entry cell.
        exit: ``(x, y)`` grid coordinate of the exit cell.
        output_file: Path of the file to write the hex-encoded maze into.
        perfect: When ``True`` the maze is a perfect maze (no loops).
        seed: Optional hex string used to seed the random generator.
        alt: When ``True`` use the Kruskal algorithm instead of the
            default random-walk algorithm.
        animate_generation: Stream generation frames to the terminal.
        animate_shortest_way: Stream solver frames to the terminal.
        interactive: Enable the interactive terminal menu after generation.
        drawing: Name of the decorative drawing embedded in the maze centre.
        theme: Name of the colour theme used for terminal rendering.
    """

    width: int = Field(ge=2, le=1000)
    height: int = Field(ge=2, le=1000)
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
        """Validate that entry and exit lie within the maze grid and differ.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If either coordinate is out of bounds or if entry
                equals exit.
        """
        if not self.assert_is_in_bound(Vector2.from_iter(self.entry)):
            raise ValueError(f"Entry = {self.entry} is not in bounds")
        if not self.assert_is_in_bound(Vector2.from_iter(self.exit)):
            raise ValueError(f"Exit = {self.exit} is not in bounds")
        if self.entry == self.exit:
            raise ValueError("Entry and Exit must be different")
        return self

    @model_validator(mode="after")
    def check_drawing_and_theme_attribute(self) -> Self:
        """Validate that ``drawing`` and ``theme`` are recognised names.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If either ``drawing`` or ``theme`` is not in the
                respective list of allowed values.
        """
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
        """Return whether *pos* falls inside the maze grid.

        Args:
            pos: The position to test.

        Returns:
            ``True`` if ``0 <= pos.x < width`` and ``0 <= pos.y < height``.
        """
        return (
            pos.x >= 0
            and pos.x < self.width
            and pos.y >= 0
            and pos.y < self.height
        )


class ParseError:
    """Represents a single error encountered while parsing the config file.

    Attributes:
        line_number: Zero-based index of the offending line.
        msg: Human-readable description of the problem.
    """

    def __init__(self, line_number: int, msg: str) -> None:
        """Initialise a parse error with location and message.

        Args:
            line_number: Zero-based index of the offending line.
            msg: Human-readable description of the problem.
        """
        self.line_number = line_number
        self.msg = msg

    def __str__(self) -> str:
        """Return a formatted ``"line N -- message"`` string."""
        return f"line {self.line_number} -- {self.msg}"


class KeyParseResult:
    """Holds a successfully parsed key-value pair ready to apply to a config.

    Attributes:
        key_name: The configuration key (e.g. ``"WIDTH"``).
        value: The parsed, typed value for that key.
    """

    def __init__(self, key_name: str, value: Any) -> None:
        """Initialise with a key name and its parsed value.

        Args:
            key_name: The configuration key.
            value: The parsed value to assign.
        """
        self.key_name = key_name
        self.value = value

    def apply(self, pr: CheckedConfig) -> None:
        """Write this result's value into *pr* using ``setattr``.

        Args:
            pr: The ``CheckedConfig`` instance to update.
        """
        setattr(pr, self.key_name.lower(), self.value)


class ArgParser(ABC):
    """Abstract base class for single-value parsers."""

    @abstractmethod
    def parse(self, str: str, line_number: int) -> Any | ParseError:
        """Parse *str* and return the typed value or a ``ParseError``.

        Args:
            str: The raw string value extracted from the config line.
            line_number: Zero-based line index, forwarded to any
                ``ParseError`` that is created.

        Returns:
            The parsed value on success, or a ``ParseError`` on failure.
        """
        pass


class KeyParser:
    """Associates a configuration key name with its ``ArgParser``.

    Attributes:
        key_name: Upper-case config key (e.g. ``"WIDTH"``).
        arg: The ``ArgParser`` responsible for the value portion.
    """

    def __init__(self, key_name: str, arg: ArgParser) -> None:
        """Initialise with a key name and its value parser.

        Args:
            key_name: Upper-case configuration key.
            arg: Parser for the value that follows the ``=`` sign.
        """
        self.key_name = key_name
        self.arg = arg

    def accepts(self, line: str) -> bool:
        """Return whether *line* starts with this key's ``KEY=`` prefix.

        Args:
            line: A single stripped line from the config file.

        Returns:
            ``True`` if the line begins with ``"<KEY_NAME>="``
            (case-insensitive).
        """
        return line.upper().startswith(f"{self.key_name}=")

    def parse(
        self, line: str, line_number: int
    ) -> KeyParseResult | ParseError:
        """Strip the key prefix and delegate value parsing to ``self.arg``.

        Args:
            line: The full config line, including the ``KEY=`` prefix.
            line_number: Zero-based line index for error reporting.

        Returns:
            A ``KeyParseResult`` on success or a ``ParseError``
            on failure.
        """
        line = line[len(f"{self.key_name}="):]
        ret = self.arg.parse(line, line_number)
        if isinstance(ret, ParseError):
            return ParseError(line_number, f"Key: {self.key_name} : {ret.msg}")
        return KeyParseResult(self.key_name, ret)


class OptKeyParser(KeyParser):
    """A ``KeyParser`` for optional configuration keys.

    Behaves identically to ``KeyParser``; the subclass distinction is used
    by ``Parser`` to decide whether a missing key is an error.
    """

    pass


class IntParser(ArgParser):
    """Parse a bare integer string."""

    def parse(self, str: str, line_number: int) -> ParseError | int:
        """Convert *str* to an ``int``.

        Args:
            str: Raw string to convert.
            line_number: Line index for error reporting.

        Returns:
            The integer value, or a ``ParseError`` if conversion fails.
        """
        try:
            return int(str)
        except ValueError:
            return ParseError(line_number, f"string {str} is not an integer")


class TupleIntParser(ArgParser):
    """Parse a ``"<int>,<int>"`` string into a two-element tuple."""

    def parse(
        self, str: str, line_number: int
    ) -> ParseError | Tuple[int, int]:
        """Convert a comma-separated pair of integers.

        Args:
            str: Raw string of the form ``"x,y"``.
            line_number: Line index for error reporting.

        Returns:
            A ``(int, int)`` tuple on success, or a ``ParseError`` on failure.
        """
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
    """Parse a non-empty, non-whitespace-only identifier string."""

    def parse(self, str: str, line_number: int) -> ParseError | str:
        """Strip *str* and verify it is a non-empty identifier.

        Args:
            str: Raw string to validate.
            line_number: Line index for error reporting.

        Returns:
            The stripped string on success, or a ``ParseError`` if the
            string is empty or whitespace-only.
        """
        str = str.strip()
        if len(str) == 0 or str.isspace():
            return ParseError(
                line_number,
                f"`{str!r}` is empty \
or space only, please use a valid name",
            )
        return str


class BoolParser(ArgParser):
    """Parse a ``"True"`` or ``"False"`` literal into a Python ``bool``."""

    def parse(self, str: str, line_number: int) -> ParseError | bool:
        """Convert the string ``"True"`` or ``"False"`` to a ``bool``.

        Args:
            str: Raw string to convert (whitespace is ignored).
            line_number: Line index for error reporting.

        Returns:
            ``True`` or ``False``, or a ``ParseError`` for any other value.
        """
        str = str.strip().replace(" ", "")
        if str == "True":
            return True
        elif str == "False":
            return False
        return ParseError(line_number, f"`{str}` should be `True` or `False`")


class DictKeysParser(ArgParser):
    """Parse a string that must be one of a fixed set of allowed keys.

    Attributes:
        allowed: List of accepted string values.
    """

    def __init__(self, allowed: KeysView[str]) -> None:
        """Initialise with the collection of allowed string values.

        Args:
            allowed: A ``KeysView`` (or any iterable) of accepted strings.
        """
        self.allowed: List[str] = list(allowed)

    def parse(self, str: str, line_number: int) -> "ParseError | str":
        """Verify that the stripped *str* is in ``self.allowed``.

        Args:
            str: Raw string to validate.
            line_number: Line index for error reporting.

        Returns:
            The validated string on success, or a ``ParseError`` if the
            value is not in the allowed set.
        """
        str = str.strip().replace(" ", "")
        if str not in self.allowed:
            return ParseError(
                line_number, f"`{str}` is not in valid keys: {self.allowed}"
            )
        return str


def key_fmt(p: KeyParser) -> str:
    """Return the human-readable format string for a ``KeyParser``.

    Optional keys are wrapped in square brackets.  The value placeholder
    reflects the type accepted by the parser (e.g. ``<int>``, ``True|False``).

    Args:
        p: The ``KeyParser`` (or ``OptKeyParser``) to format.

    Returns:
        A string such as ``"WIDTH=<int>"`` or ``"[ALT=True|False]"``.
    """

    def fmt_arg(a: ArgParser) -> str:
        """Return the placeholder string for a single ``ArgParser``."""
        if isinstance(a, IntParser):
            return "<int>"
        elif isinstance(a, TupleIntParser):
            return "<int>,<int>"
        elif isinstance(a, BoolParser):
            return "True|False"
        elif isinstance(a, IdentParser):
            return "<str>"
        elif isinstance(a, DictKeysParser):
            return "|".join(a.allowed)
        return ""

    def fmt(p: KeyParser) -> str:
        """Return the unbracketed ``KEY=<placeholder>`` string."""
        return f"{p.key_name}={fmt_arg(p.arg)}"

    if isinstance(p, OptKeyParser):
        return f"[{fmt(p)}]"
    return fmt(p)


class Parser:
    """Parse a plain-text config file into a ``CheckedConfig``.

    The expected format is one ``KEY=VALUE`` pair per line::

        WIDTH=<int>
        HEIGHT=<int>
        ENTRY=<int>,<int>
        EXIT=<int>,<int>
        OUTPUT_FILE=<str>
        PERFECT=True|False
        [ALT=True|False]
        [SEED=<str>]
        [ANIMATE_GENERATION=True|False]
        [ANIMATE_SHORTEST_WAY=True|False]
        [INTERACTIVE=True|False]
        [DRAWING=42|smiley|pac-man|no_drawing]
        [THEME=red|black|green|squeleton|rgb]

    Lines beginning with ``#`` and blank lines are ignored.
    Keys in square brackets are optional; all others are required.

    Raises:
        ValueError: If the text contains parse errors or missing required keys.
    """

    @classmethod
    def config_format(cls) -> str:
        """Return a multi-line string describing the expected config format.

        Returns:
            One ``key_fmt`` entry per line, in declaration order.
        """
        return "\n".join(list(map(key_fmt, cls.extractors)))

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
        """Return the subset of extractors that may be changed interactively.

        Returns:
            A list of ``KeyParser`` instances for all config keys that can
            be toggled or updated during an interactive session.
        """
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
        """Parse *txt* into a validated ``CheckedConfig``.

        Each non-comment, non-blank line is matched against the ordered
        list of ``extractors``.  Once an extractor matches it is removed
        from the candidate list so every key appears at most once.

        Args:
            txt: Full contents of the configuration file.

        Returns:
            A fully validated ``CheckedConfig`` instance.

        Raises:
            ValueError: If any required key is missing, any value is
                invalid, or an unrecognised key is encountered.
        """
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
            """Format an error message for a missing required key."""
            return f"Key: {kp.key_name} was not found"

        def is_not_opt(kp: KeyParser) -> bool:
            """Return ``True`` if *kp* is a mandatory (non-optional) key."""
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
            arr = []
            for err in e.errors():
                try:
                    arr.append(
                        "Invalid input for " + f"{err['loc'][0]}: {err['msg']}"
                    )
                except IndexError:
                    arr.append(f"Invalid input: {err['msg']}")
            raise ValueError("\n".join(arr))
