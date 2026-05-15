from decimal import Decimal, InvalidOperation
from django.utils.dateparse import parse_date


# Check if the username follows some basic rules
def validate_username(name):
    if len(name) < 3 or len(name) > 20:
        return "Username must have between 3 and 20 characters"

    for character in name:
        if not (character.isalnum() or character == "_"):
            return "Username can only use letters, numbers and underscores"

    return None


# Check if the password follows some basic rules
def validate_password(password):
    if len(password) < 8:
        return "Password must have at least 8 characters"

    has_letter = False
    has_number = False

    for character in password:
        if character.isalpha():
            has_letter = True

        if character.isdigit():
            has_number = True

    if not has_letter or not has_number:
        return "Password must include at least one letter and one number"

    return None


# Convert a text value into a decimal number
def parse_decimal_value(value):
    try:
        return Decimal(str(value)), None
    except (InvalidOperation, TypeError):
        return None, "Value must be a valid number"


# Convert a text value into an integer number
def parse_int_value(value):
    try:
        return int(value), None
    except (ValueError, TypeError):
        return None, "Value must be a valid whole number"


# Check if one measurement is inside the expected range
def validate_measurement_range(field, value):
    if field == "weight" and (value < Decimal("30") or value > Decimal("600")):
        return "Weight must be between 30 and 600 kilograms"

    if field == "height" and (value < Decimal("1") or value > Decimal("3")):
        return "Height must be between 1 and 3 metres"

    if field in ["chest", "thighs", "waist", "hips"]:
        if value < Decimal("10") or value > Decimal("200"):
            return f"{field.capitalize()} must be between 10 and 200 centimetres"

    return None


# Check if the cardio values are inside the expected range
def validate_cardio_values(level, time, incline):
    if level < 0 or level > 20:
        return "Level must be between 0 and 20"

    if time <= 0 or time > Decimal("500"):
        return "Time must be between 1 and 500 minutes"

    if incline < 0 or incline > 20:
        return "Incline must be between 0 and 20"

    return None


# Check if the weight training values are inside the expected range
def validate_weight_values(weight, reps):
    if weight <= 0 or weight > Decimal("200"):
        return "Weight must be between 1 and 200 kilograms"

    if reps <= 0 or reps > 100:
        return "Reps must be between 1 and 100"

    return None


# Check if the session filter dates can be used safely
def validate_session_filter_dates(date_from_text, date_to_text):
    date_from = None
    date_to = None

    if date_from_text:
        date_from = parse_date(date_from_text)

        if not date_from:
            return None, None, "From date must use YYYY-MM-DD format"

    if date_to_text:
        date_to = parse_date(date_to_text)

        if not date_to:
            return None, None, "To date must use YYYY-MM-DD format"

    if date_from and date_to and date_from > date_to:
        return None, None, "From date cannot be later than to date"

    return date_from, date_to, None
