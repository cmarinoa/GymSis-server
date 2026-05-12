from django.http import JsonResponse

from ..models import Cardio, SessionCardio, SessionTraining, WeightTraining
from .validation_helpers import parse_decimal_value, parse_int_value, validate_cardio_values, validate_weight_values


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

    level, level_error = parse_int_value(level)
    time, time_error = parse_decimal_value(time)
    incline, incline_error = parse_int_value(incline or 0)

    if level_error or time_error or incline_error:
        return JsonResponse({"error": "Exercise values must be valid numbers"}, status=400)

    range_error = validate_cardio_values(level, time, incline)

    if range_error:
        return JsonResponse({"error": range_error}, status=400)

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

    weight, weight_error = parse_decimal_value(weight)
    reps, reps_error = parse_int_value(reps)

    if weight_error or reps_error:
        return JsonResponse({"error": "Exercise values must be valid numbers"}, status=400)

    range_error = validate_weight_values(weight, reps)

    if range_error:
        return JsonResponse({"error": range_error}, status=400)

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

    level, level_error = parse_int_value(level)
    time, time_error = parse_decimal_value(time)
    incline, incline_error = parse_int_value(incline or 0)

    if level_error or time_error or incline_error:
        return JsonResponse({"error": "Exercise values must be valid numbers"}, status=400)

    range_error = validate_cardio_values(level, time, incline)

    if range_error:
        return JsonResponse({"error": range_error}, status=400)

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

    weight, weight_error = parse_decimal_value(weight)
    reps, reps_error = parse_int_value(reps)

    if weight_error or reps_error:
        return JsonResponse({"error": "Exercise values must be valid numbers"}, status=400)

    range_error = validate_weight_values(weight, reps)

    if range_error:
        return JsonResponse({"error": range_error}, status=400)

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
