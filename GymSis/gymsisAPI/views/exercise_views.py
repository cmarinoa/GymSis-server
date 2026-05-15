import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import Session, SessionCardio, SessionTraining
from .exercise_helpers import get_saved_exercise, register_cardio_exercise, register_weight_exercise, update_cardio_exercise, update_weight_exercise


# Manage exercises
@csrf_exempt
def exercises(request):
    if request.method == "GET":
        return get_exercises(request)

    if request.method == "POST":
        return register_exercise(request)

    return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)


# Get all exercises from one session
def get_exercises(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    session_id = request.GET.get("session_id")
    search = request.GET.get("search", "")

    if isinstance(search, str):
        search = search.strip()

    if not session_id:
        return JsonResponse({"error": "Session is required"}, status=400)

    try:
        session = Session.objects.get(id=session_id, user_id=user_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

    exercise_list = []
    cardio_exercises = SessionCardio.objects.filter(session=session)
    weight_exercises = SessionTraining.objects.filter(session=session)

    if search:
        cardio_exercises = cardio_exercises.filter(cardio__name__icontains=search)
        weight_exercises = weight_exercises.filter(user_exercise__name__icontains=search)

    for exercise in cardio_exercises:
        exercise_list.append({
            "exercise_id": f"cardio-{exercise.id}",
            "exercise_type": "cardio",
            "name": exercise.cardio.name,
            "level": exercise.level,
            "time": str(exercise.time),
            "incline": exercise.incline
        })

    for exercise in weight_exercises:
        exercise_list.append({
            "exercise_id": f"weights-{exercise.id}",
            "exercise_type": "weights",
            "user_exercise_id": exercise.user_exercise.id,
            "name": exercise.user_exercise.name,
            "weight": str(exercise.weight),
            "reps": exercise.reps
        })

    return JsonResponse({"exercises": exercise_list})


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
