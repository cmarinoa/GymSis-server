import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from .models import Cardio, Session, SessionCardio, SessionTraining, User, WeightTraining


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


# Get all sessions from the logged in user
def get_sessions(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    sessions = Session.objects.filter(user_id=user_id).order_by("date", "id")
    session_list = []

    for session in sessions:
        session_list.append({
            "session_number": session.id,
            "date": session.date.isoformat()
        })

    return JsonResponse({"sessions": session_list})


# Get all exercises from one session
def get_exercises(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    session_id = request.GET.get("session_id")

    if not session_id:
        return JsonResponse({"error": "Session is required"}, status=400)

    try:
        session = Session.objects.get(id=session_id, user_id=user_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

    exercise_list = []

    for exercise in SessionCardio.objects.filter(session=session):
        exercise_list.append({
            "exercise_id": exercise.id,
            "exercise_type": "cardio",
            "name": exercise.cardio.name,
            "level": exercise.level,
            "time": str(exercise.time),
            "incline": exercise.incline
        })

    for exercise in SessionTraining.objects.filter(session=session):
        exercise_list.append({
            "exercise_id": exercise.id,
            "exercise_type": "weights",
            "name": exercise.training.name,
            "weight": str(exercise.weight),
            "reps": exercise.reps
        })

    return JsonResponse({"exercises": exercise_list})


# Register a new exercise inside a session
@csrf_exempt
def register_exercise(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    session_id = data.get("session_id")
    exercise_type = data.get("exercise_type")

    if not session_id or not exercise_type:
        return JsonResponse({"error": "Session and exercise type are required"}, status=400)

    try:
        session = Session.objects.get(id=session_id, user_id=user_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

    if exercise_type == "cardio":
        return register_cardio_exercise(data, session)

    if exercise_type == "weights":
        return register_weight_exercise(data, session)

    return JsonResponse({"error": "Invalid exercise type"}, status=400)


# Register a cardio exercise
def register_cardio_exercise(data, session):
    cardio_name = data.get("name")
    level = data.get("level")
    time = data.get("time")
    incline = data.get("incline", 0)

    cardio_options = [
        "Treadmill",
        "Bike",
        "Stairmaster",
        "Elliptical",
        "Rowing machine",
        "Swimming"
    ]

    if cardio_name not in cardio_options:
        return JsonResponse({"error": "Invalid cardio exercise"}, status=400)

    if cardio_name == "Swimming":
        level = 0
    elif not level:
        return JsonResponse({"error": "Level is required"}, status=400)

    if not time:
        return JsonResponse({"error": "Time is required"}, status=400)

    if cardio_name == "Treadmill" and incline == "":
        return JsonResponse({"error": "Incline is required for treadmill"}, status=400)

    try:
        level = int(level)
        time = Decimal(str(time))
        incline = int(incline or 0)
    except (ValueError, InvalidOperation):
        return JsonResponse({"error": "Exercise values must be valid numbers"}, status=400)

    cardio, created = Cardio.objects.get_or_create(name=cardio_name)
    exercise = SessionCardio.objects.create(
        session=session,
        cardio=cardio,
        level=level,
        time=time,
        incline=incline
    )

    return JsonResponse({
        "message": "Exercise registered successfully",
        "exercise_id": exercise.id,
        "exercise_type": "cardio",
        "name": cardio.name,
        "level": exercise.level,
        "time": str(exercise.time),
        "incline": exercise.incline
    }, status=201)


# Register a weight training exercise
def register_weight_exercise(data, session):
    exercise_name = data.get("name")
    weight = data.get("weight")
    reps = data.get("reps")

    if not exercise_name or not weight or not reps:
        return JsonResponse({"error": "Name, weight and reps are required"}, status=400)

    try:
        weight = Decimal(str(weight))
        reps = int(reps)
    except (ValueError, InvalidOperation):
        return JsonResponse({"error": "Exercise values must be valid numbers"}, status=400)

    training, created = WeightTraining.objects.get_or_create(name=exercise_name)
    exercise = SessionTraining.objects.create(
        session=session,
        training=training,
        weight=weight,
        reps=reps
    )

    return JsonResponse({
        "message": "Exercise registered successfully",
        "exercise_id": exercise.id,
        "exercise_type": "weights",
        "name": training.name,
        "weight": str(exercise.weight),
        "reps": exercise.reps
    }, status=201)
