def convert_to_persian_numerals(text: str) -> str:
    """
    Converts standard English numerals to Persian numerals.
    """
    english_to_persian = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    return text.translate(english_to_persian)