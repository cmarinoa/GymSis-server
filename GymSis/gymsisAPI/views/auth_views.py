import json

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import User


# Log in an existing user
@csrf_exempt
def login_user(request):
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

    try:
        user = User.objects.get(name=name)
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid name or password"}, status=400)

    if not check_password(password, user.password):
        return JsonResponse({"error": "Invalid name or password"}, status=400)

    request.session.flush()
    request.session["user_id"] = user.id
    request.session["user_name"] = user.name
    request.session.save()

    return JsonResponse({
        "message": "Login successful",
        "token": request.session.session_key,
        "user_id": user.id,
        "name": user.name
    })


# Check if a saved session is still valid
def get_saved_session(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

    user_id = request.session.get("user_id")
    user_name = request.session.get("user_name")

    if not user_id or not user_name:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    return JsonResponse({
        "message": "Session is valid",
        "user_id": user_id,
        "name": user_name
    })
