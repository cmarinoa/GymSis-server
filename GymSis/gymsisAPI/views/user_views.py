import json

from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import User
from .validation_helpers import validate_password, validate_username


# Register a new user
@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = data.get("name")
    password = data.get("password")

    if not name or not password:
        return JsonResponse({"error": "Name and password are required"}, status=400)

    username_error = validate_username(name)

    if username_error:
        return JsonResponse({"error": username_error}, status=400)

    password_error = validate_password(password)

    if password_error:
        return JsonResponse({"error": password_error}, status=400)

    if User.objects.filter(name=name).exists():
        return JsonResponse({"error": "User already exists"}, status=400)

    user = User.objects.create(
        name=name,
        password=make_password(password),
        weight=None,
        height=None,
        chest=None,
        waist=None,
        hips=None,
        thighs=None
    )

    return JsonResponse({
        "message": "User registered successfully",
        "user_id": user.id,
        "name": user.name
    }, status=201)
