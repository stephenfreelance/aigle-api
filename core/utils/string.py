import re
import unicodedata


def snake_to_camel_case(name: str) -> str:
    parts = iter(name.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    return str(text)


def normalize(string: str) -> str:
    return re.sub(
        "[^a-zA-Z0-9 \n\\.]", " ", unicodedata.normalize("NFD", strip_accents(string))
    ).lower()


def slugify(string: str) -> str:
    normalized = normalize(string)
    spliteds = [splited for splited in normalized.split(" ") if splited]

    return "-".join(spliteds)
