import json
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import User


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
            value = 0

        try:
            measurements[field] = Decimal(str(value))
        except (InvalidOperation, TypeError):
            return JsonResponse({"error": "Measurements must be valid numbers"}, status=400)

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
        "height": str(user.height),
        "weight": str(user.weight),
        "chest": str(user.chest),
        "thighs": str(user.thighs),
        "waist": str(user.waist),
        "hips": str(user.hips)
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
        "height": str(user.height),
        "weight": str(user.weight),
        "chest": str(user.chest),
        "thighs": str(user.thighs),
        "waist": str(user.waist),
        "hips": str(user.hips)
    })
