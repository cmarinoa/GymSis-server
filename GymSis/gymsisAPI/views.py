import json

from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from .models import Session, User


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

    if User.objects.filter(name=name).exists():
        return JsonResponse({"error": "User already exists"}, status=400)

    user = User.objects.create(
        name=name,
        password=make_password(password),
        weight=0,
        height=0,
        chest=0,
        waist=0,
        hips=0,
        thighs=0
    )

    return JsonResponse({
        "message": "User registered successfully",
        "user_id": user.id,
        "name": user.name
    }, status=201)


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


# Register a new gym session
@csrf_exempt
def register_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    date_text = data.get("date")

    if not date_text:
        return JsonResponse({"error": "Date is required"}, status=400)

    session_date = parse_date(date_text)

    if not session_date:
        return JsonResponse({"error": "Date must use YYYY-MM-DD format"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    session = Session.objects.create(
        user=user,
        date=session_date
    )

    return JsonResponse({
        "message": "Session registered successfully",
        "session_number": session.id,
        "date": session.date.isoformat()
    }, status=201)
