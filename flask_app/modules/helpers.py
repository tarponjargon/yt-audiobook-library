import unicodedata
import html
import re


def string_to_ascii(input_string):
    """
    Converts the input string to its ASCII representation by removing non-ASCII characters.

    Args:
        input_string (str): The string to be converted.

    Returns:
        str: The ASCII-only version of the input string.
    """
    return (
        unicodedata.normalize("NFKD", input_string)
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )


def html_entities_to_chars(input_string):
    """
    Converts HTML entities in a string to their corresponding characters.

    Args:
        input_string (str): The string containing HTML entities.

    Returns:
        str: The string with HTML entities converted to characters.
    """
    return html.unescape(input_string)


def trim_and_reduce_whitespace(input_string):
    """
    Trims leading and trailing spaces and replaces multiple consecutive whitespace characters with a single space.

    Args:
        input_string (str): The string to be trimmed and processed.

    Returns:
        str: The processed string with trimmed spaces and reduced whitespace.
    """

    # Replace multiple whitespace characters with a single space
    reduced_whitespace = re.sub(r"\s+", " ", input_string)

    # Trim leading and trailing spaces
    trimmed = reduced_whitespace.strip()

    return trimmed
