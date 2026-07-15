"""Validation rules shared by the sign-up form, the account page and the
Database page, so the same rules apply wherever a user record is created or
edited.
"""
from django.core.validators import RegexValidator

# --- Names -----------------------------------------------------------------
# A name is letters, and may contain a space, hyphen, apostrophe or period
# between them (Jean-Luc, O'Brien, van der Berg, J. Smith).
#
# The letter class is [^\W\d_]: "a word character, but not a digit and not an
# underscore" - which in Python means A LETTER IN ANY ALPHABET. That is
# deliberate. A plain [A-Za-z] rule would reject the customers this site is
# actually for: Greek names (Ελένη Παπαδοπούλου) and accented ones (Müller)
# would all be turned away. This rule still blocks what we want to block -
# digits, @, #, <, >, and other symbols.
name_validator = RegexValidator(
    regex=r"^[^\W\d_]+(?:[ '\-.][^\W\d_]+)*$",
    message="Please use letters only. A name may include spaces, hyphens (-) "
            "and apostrophes ('), but not numbers or symbols.",
)

# --- Phone -----------------------------------------------------------------
# Digits, with an optional leading + and any mix of spaces, hyphens or brackets
# for readability, e.g. '+30 6900 111111' or '(210) 555-0123'.
# At least 8 digits, so a number that could never be dialled is refused.
# The same rule as an HTML pattern attribute (no ^ $ - the browser adds them),
# so the browser and the server cannot drift apart.
#
# Reading it: an optional leading '+', then a look-ahead demanding at least 8
# digits somewhere in the value, then the characters that are allowed at all
# (digits, spaces, brackets and hyphens). The look-ahead is what makes '12' and
# '()-- --' fail: they are made of legal characters but are not real numbers.
# NOTE the escaped brackets: \( \) rather than ( ). Browsers compile a pattern
# attribute with the unicode 'v' flag, which REQUIRES brackets inside a character
# class to be escaped; an unescaped one makes the whole pattern fail to compile,
# and a browser silently ignores a pattern it cannot compile - so the rule would
# quietly do nothing in the browser. Python accepts the escaped form too, so one
# string can safely serve both.
PHONE_PATTERN = r'\+?(?=(?:\D*\d){8,})[\d \(\)\-]{8,20}'

phone_validator = RegexValidator(
    regex=r'^' + PHONE_PATTERN + r'$',
    message='Please enter a valid phone number with at least 8 digits, '
            'e.g. +30 6900 111111.',
)


def clean_text(value):
    """Trim the ends of a typed string and collapse runs of inner spaces.

    '  Nikos   Papas ' becomes 'Nikos Papas'. Without this, a stray space makes
    two identical-looking values different as far as the database is concerned.
    """
    return ' '.join((value or '').split())


def clean_email(value):
    """Trim an email address and lowercase the whole of it.

    Email addresses are case-insensitive in practice, but the database's unique
    check is case-SENSITIVE, so without this 'Test@Bar.com' and 'test@bar.com'
    are two different accounts for the same person. (Django's normalize_email
    only lowercases the domain part, so it does not close this gap on its own.)
    """
    return (value or '').strip().lower()
