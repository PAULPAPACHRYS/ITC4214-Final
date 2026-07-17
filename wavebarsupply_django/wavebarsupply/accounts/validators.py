from django.core.validators import RegexValidator

"""
A name is letters, and may contain a space, hyphen, apostrophe or period
between them (ex: Jean-Luc, O'Brien, van der Berg, J. Smith)

The letter class is [^\W\d_], a word character, but not a digit and not an underscore
If I used [A-Za-z], then names like Ελένη Παπαδοπούλου and Müller would all be turned away. 
The rule I used still blocks digits, @, #, <, >, and other symbols
"""
name_validator = RegexValidator(
    regex=r"^[^\W\d_]+(?:[ '\-.][^\W\d_]+)*$",
    message="Please use letters only. A name may include spaces, hyphens (-) "
            "and apostrophes ('), but not numbers or symbols.",
)

"""
A phone number is at least 8 digits and can contain an optional leading + and 
any mix of spaces, hyphens or brackets ex: '+30 6900 111111' or '(210) 555-0123'

The same rule as an HTML pattern attribute (no ^ $ - the browser adds them),
so the browser and the server cannot drift apart.
"""
PHONE_PATTERN = r'\+?(?=(?:\D*\d){8,})[\d \(\)\-]{8,20}'

phone_validator = RegexValidator(
    regex=r'^' + PHONE_PATTERN + r'$',
    message='Please enter a valid phone number with at least 8 digits, '
            'e.g. +30 6900 111111.',
)


def clean_text(value):
    #trim the ends of a typed string and collapse runs of inner spaces.
    return ' '.join((value or '').split())


def clean_email(value):
    #trim an email address and lowercase the whole of it.
    return (value or '').strip().lower()
