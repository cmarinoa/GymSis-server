import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import User
from .validation_helpers import parse_decimal_value, validate_measurement_range


# Return a blank value when the measurement has not been filled yet
def format_measurement_value(value):
    if value is None or str(value) == "0" or str(value) == "0.00":
        return ""

    return str(value)


# Manage the user's body measurements
@csrf_exempt
def measurements(request):
    if request.method == "GET":
        return get_measurements(request)

    if request.method == "POST":
        return register_measurements(request)

    return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)


# Register the user's body measurements
def register_measurements(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    fields = ["height", "weight", "chest", "thighs", "waist", "hips"]
    measurements = {}

    for field in fields:
        value = data.get(field)

        if value == "":
            measurements[field] = None
            continue

        measurements[field], error_message = parse_decimal_value(value)

        if error_message:
            return JsonResponse({"error": "Measurements must be valid numbers"}, status=400)

        range_error = validate_measurement_range(field, measurements[field])

        if range_error:
            return JsonResponse({"error": range_error}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    user.height = measurements["height"]
    user.weight = measurements["weight"]
    user.chest = measurements["chest"]
    user.thighs = measurements["thighs"]
    user.waist = measurements["waist"]
    user.hips = measurements["hips"]
    user.save()

    return JsonResponse({
        "message": "Measurements registered successfully",
        "height": format_measurement_value(user.height),
        "weight": format_measurement_value(user.weight),
        "chest": format_measurement_value(user.chest),
        "thighs": format_measurement_value(user.thighs),
        "waist": format_measurement_value(user.waist),
        "hips": format_measurement_value(user.hips)
    })


# Get the user's body measurements
def get_measurements(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({
        "height": format_measurement_value(user.height),
        "weight": format_measurement_value(user.weight),
        "chest": format_measurement_value(user.chest),
        "thighs": format_measurement_value(user.thighs),
        "waist": format_measurement_value(user.waist),
        "hips": format_measurement_value(user.hips)
    })
