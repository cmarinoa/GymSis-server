import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import User, UserExercise
from .user_exercise_helpers import build_user_exercise_data, validate_user_exercise_name


# Manage saved exercises
@csrf_exempt
def user_exercises(request):
    if request.method == "GET":
        return get_user_exercises(request)

    if request.method == "POST":
        return register_user_exercise(request)

    return JsonResponse({"error": "Only GET and POST requests are allowed"}, status=405)


# Register a new saved exercise
def register_user_exercise(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = data.get("name")

    if isinstance(name, str):
        name = name.strip()

    name_error = validate_user_exercise_name(name)

    if name_error:
        return JsonResponse({"error": name_error}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if UserExercise.objects.filter(user=user, name=name, is_active=True).exists():
        return JsonResponse({"error": "Exercise already exists"}, status=400)

    exercise = UserExercise.objects.create(
        user=user,
        name=name,
        is_active=True
    )

    return JsonResponse({
        "message": "Exercise registered successfully",
        **build_user_exercise_data(exercise)
    }, status=201)


# Get all saved exercises from the logged in user
def get_user_exercises(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    saved_exercises = UserExercise.objects.filter(user_id=user_id, is_active=True).order_by("name", "id")
    exercise_list = []

    for exercise in saved_exercises:
        exercise_list.append(build_user_exercise_data(exercise))

    return JsonResponse({"exercises": exercise_list})


# Manage one saved exercise
@csrf_exempt
def user_exercise_detail(request, exercise_id):
    if request.method == "GET":
        return get_user_exercise(request, exercise_id)

    if request.method == "PUT":
        return update_user_exercise(request, exercise_id)

    if request.method == "DELETE":
        return delete_user_exercise(request, exercise_id)

    return JsonResponse({"error": "Only GET, PUT and DELETE requests are allowed"}, status=405)


# Get one saved exercise
def get_user_exercise(request, exercise_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        exercise = UserExercise.objects.get(id=exercise_id, user_id=user_id, is_active=True)
    except UserExercise.DoesNotExist:
        return JsonResponse({"error": "Exercise not found"}, status=404)

    return JsonResponse(build_user_exercise_data(exercise))


# Update one saved exercise
def update_user_exercise(request, exercise_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        exercise = UserExercise.objects.get(id=exercise_id, user_id=user_id, is_active=True)
    except UserExercise.DoesNotExist:
        return JsonResponse({"error": "Exercise not found"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = data.get("name")

    if isinstance(name, str):
        name = name.strip()

    name_error = validate_user_exercise_name(name)

    if name_error:
        return JsonResponse({"error": name_error}, status=400)

    if UserExercise.objects.filter(user_id=user_id, name=name, is_active=True).exclude(id=exercise.id).exists():
        return JsonResponse({"error": "Exercise already exists"}, status=400)

    exercise.name = name
    exercise.save()

    return JsonResponse({
        "message": "Exercise updated successfully",
        **build_user_exercise_data(exercise)
    })


# Delete one saved exercise
def delete_user_exercise(request, exercise_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    try:
        exercise = UserExercise.objects.get(id=exercise_id, user_id=user_id, is_active=True)
    except UserExercise.DoesNotExist:
        return JsonResponse({"error": "Exercise not found"}, status=404)

    exercise.is_active = False
    exercise.save()

    return JsonResponse({"message": "Exercise archived successfully"})
