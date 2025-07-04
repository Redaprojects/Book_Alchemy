import re
from datetime import date


def is_valid_name(name: str) -> bool:
    """
    Validates an author or person's name.
    Accepts letters, spaces, apostrophes, and hyphens.
    """
    if not name or not isinstance(name, str):
        return False
    return bool(re.fullmatch(r"[A-Za-z\s'.-]+", name.strip()))


def is_valid_isbn(isbn: str) -> bool:
    """
    Validates that the ISBN is a 13-digit number (e.g., '9781234567897').
    """
    return bool(re.fullmatch(r"\d{10}|\d{13}", isbn.strip()))


def is_valid_rating(value: str) -> bool:
    """
    Validates rating is an Integer between 1 and 5 (inclusive).
    """
    try:
        rating = float(value)
        return 1.0 <= rating <= 5.0
    except (ValueError, TypeError):
        return False


def is_valid_year(value: str) -> bool:
    """
    Validates that the year is numeric and not in the future.
    """
    if not value.isdigit():
        return False
    year = int(value)
    return 0 < year <= date.today().year


def validate_dates(birth_date, death_date=None) -> tuple[bool, str]:
    """
    Validates:
    - birth date is provided
    - death date (if given) is after birth and not in the future
    Returns (is_valid: bool, error_message: str)
    """
    if not birth_date:
        return False, "Birth date is required."
    if death_date:
        if death_date < birth_date:
            return False, "Death date can't be before birth date."
        if death_date > date.today():
            return False, "Death date can't be in the future."
    return True, ""

