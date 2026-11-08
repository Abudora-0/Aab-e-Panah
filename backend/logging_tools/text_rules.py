# All line break rules live here, so they are not written twice.

import unicodedata


def is_control_character(character):
    category = unicodedata.category(character)
    return category == "Cc" or category == "Zl" or category == "Zp"


def has_control_characters(text):
    for character in text:
        if is_control_character(character):
            return True
    return False


def clean_text(value):
    cleaned = ""
    text = str(value)
    for character in text:
        if is_control_character(character):
            cleaned += " "
        else:
            cleaned += character
    return cleaned
