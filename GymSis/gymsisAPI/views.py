# to do: separate endpoints into different files

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


# Manage gym sessions
@csrf_exempt
def sessions(request):
    if request.method == "GET":
        return get_sessions(request)

    if request.method == "POST":
        return register_session(request)

    return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)


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


# Manage one session
@csrf_exempt
def session_detail(request, session_id):
    if request.method == "PUT":
        return update_session(request, session_id)

    if request.method == "DELETE":
        return delete_session(request, session_id)

    return JsonResponse({"error": "Only PUT and DELETE requests are allowed"}, status=405)


# Update the date of one session
def update_session(request, session_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        session = Session.objects.get(id=session_id, user_id=user_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

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

    session.date = session_date
    session.save()

    return JsonResponse({
        "message": "Session updated successfully",
        "session_number": session.id,
        "date": session.date.isoformat()
    })


# Delete one session
def delete_session(request, session_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        session = Session.objects.get(id=session_id, user_id=user_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

    session.delete()

    return JsonResponse({"message": "Session deleted successfully"})


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
            "exercise_id": f"cardio-{exercise.id}",
            "exercise_type": "cardio",
            "name": exercise.cardio.name,
            "level": exercise.level,
            "time": str(exercise.time),
            "incline": exercise.incline
        })

    for exercise in SessionTraining.objects.filter(session=session):
        exercise_list.append({
            "exercise_id": f"weights-{exercise.id}",
            "exercise_type": "weights",
            "name": exercise.training.name,
            "weight": str(exercise.weight),
            "reps": exercise.reps
        })

    return JsonResponse({"exercises": exercise_list})


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


# Manage exercises
@csrf_exempt
def exercises(request):
    if request.method == "GET":
        return get_exercises(request)

    if request.method == "POST":
        return register_exercise(request)

    return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)


# Manage one exercise
@csrf_exempt
def exercise_detail(request, exercise_id):
    if request.method == "PUT":
        return update_exercise(request, exercise_id)

    if request.method == "DELETE":
        return delete_exercise(request, exercise_id)

    return JsonResponse({"error": "Only PUT and DELETE requests are allowed"}, status=405)


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


# Update one exercise
def update_exercise(request, exercise_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    exercise_type, exercise = get_saved_exercise(exercise_id, user_id)

    if not exercise:
        return JsonResponse({"error": "Exercise not found"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if exercise_type == "cardio":
        return update_cardio_exercise(data, exercise)

    return update_weight_exercise(data, exercise)


# Delete one exercise
def delete_exercise(request, exercise_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    exercise_type, exercise = get_saved_exercise(exercise_id, user_id)

    if not exercise:
        return JsonResponse({"error": "Exercise not found"}, status=404)

    exercise.delete()

    return JsonResponse({"message": "Exercise deleted successfully"})


# Find one saved exercise using its type prefix and id
def get_saved_exercise(exercise_id, user_id):
    if exercise_id.startswith("cardio-"):
        cardio_id = exercise_id.replace("cardio-", "", 1)

        try:
            exercise = SessionCardio.objects.get(id=cardio_id, session__user_id=user_id)
        except SessionCardio.DoesNotExist:
            return None, None

        return "cardio", exercise

    if exercise_id.startswith("weights-"):
        weight_id = exercise_id.replace("weights-", "", 1)

        try:
            exercise = SessionTraining.objects.get(id=weight_id, session__user_id=user_id)
        except SessionTraining.DoesNotExist:
            return None, None

        return "weights", exercise

    return None, None


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
        "exercise_id": f"cardio-{exercise.id}",
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
        "exercise_id": f"weights-{exercise.id}",
        "exercise_type": "weights",
        "name": training.name,
        "weight": str(exercise.weight),
        "reps": exercise.reps
    }, status=201)


# Update a cardio exercise
def update_cardio_exercise(data, exercise):
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
    exercise.cardio = cardio
    exercise.level = level
    exercise.time = time
    exercise.incline = incline
    exercise.save()

    return JsonResponse({
        "message": "Exercise updated successfully",
        "exercise_id": f"cardio-{exercise.id}",
        "exercise_type": "cardio",
        "name": exercise.cardio.name,
        "level": exercise.level,
        "time": str(exercise.time),
        "incline": exercise.incline
    })


# Update a weight training exercise
def update_weight_exercise(data, exercise):
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
    exercise.training = training
    exercise.weight = weight
    exercise.reps = reps
    exercise.save()

    return JsonResponse({
        "message": "Exercise updated successfully",
        "exercise_id": f"weights-{exercise.id}",
        "exercise_type": "weights",
        "name": exercise.training.name,
        "weight": str(exercise.weight),
        "reps": exercise.reps
    })
