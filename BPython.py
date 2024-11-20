import ast
import argparse
import code
import tokenize
from io import BytesIO

from речника_на_баце import MAP, REVERSE_MAP


class Bpython_to_python:
    """Bpython to Python translator."""

    def __init__(self, mapping):
        self._mapping = mapping

    def __call__(self, input_code):
        """Translate Bpython to native Python code."""
        code_bytes = BytesIO(input_code.encode("utf-8")).readlines()
        tokens = tokenize.tokenize(BytesIO(b"".join(code_bytes)).readline)
        py_tokens = []
        for token in tokens:
            if token.type == tokenize.NAME and token.string in MAP:
                py_tokens.append(tokenize.TokenInfo(type=token.type,
                                                    string=MAP[token.string],
                                                    start=token.start,
                                                    end=token.end,
                                                    line=token.line))
            else:
                py_tokens.append(token)
        return tokenize.untokenize(py_tokens).decode("utf-8")


class BpythonConsole(code.InteractiveConsole):
    """Interactive console for Bpython."""

    def __init__(self, *args, **kwargs):
        self._translator = Bpython_to_python(MAP)
        super().__init__(*args, **kwargs)

    def runsource(self, source, filename="<input>", symbol="single"):
        translated_source = self._translator(source)
        return super().runsource(translated_source, filename, symbol)


def къ(*args):
    """Print help messages."""
    if not args:
        print("И я не знам къ а са опраиш. \nПробвай да кажеш "
              "къ(<име>) и ако тава име го знам, ше ти каа.")
    elif len(args) == 1:
        arg, = args
        if (translated:=REVERSE_MAP.get(arg, None)) is not None:
            print(f"Е па \"{arg}\" на врачански е \"{translated}\", баце")
        else:
            print(f"Не знам, баце. Пробвай да си ползваш \"{arg}\".")
    else:
        print("Бацеее, айде да слушаме, а?")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()
    if args.file is None:
        BANNER = ("Ооо, къде одиш бе, нашио?\n"
                  "Bpython е баш като Python, ма за ора естете.\n"
                  "На́пиши 'къ()' таа вииш къ а са опраиш.\n"
                  "На́пиши 'ae' таа излееш.")
        console = BpythonConsole(locals=locals())
        console.interact(banner=BANNER)
    else:
        try:
            with open(args.file, encoding="utf-8") as file:
                content = file.read()
        except Exception as exe:
            print(f"Баце, но моа отвора тоа файл.\n{exe}")
        translator = Bpython_to_python(MAP)
        translated = translator(content)
        tree = ast.parse(translated)
        exec(compile(tree, filename="<string>", mode="exec"))
