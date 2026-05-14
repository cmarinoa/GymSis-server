from django.db.models import Max
from django.http import JsonResponse

from ..models import SessionTraining, UserExercise


# Get the progress history for one saved exercise
def progress(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    exercise_id = request.GET.get("exercise_id")

    if not exercise_id:
        return JsonResponse({"error": "Exercise is required"}, status=400)

    try:
        user_exercise = UserExercise.objects.get(id=exercise_id, user_id=user_id)
    except UserExercise.DoesNotExist:
        return JsonResponse({"error": "Exercise not found"}, status=404)

    progress_rows = (
        SessionTraining.objects
        .filter(user_exercise=user_exercise, session__user_id=user_id)
        .values("session__date")
        .annotate(max_weight=Max("weight"))
        .order_by("session__date")
    )

    progress_list = []

    for row in progress_rows:
        progress_list.append({
            "date": row["session__date"].strftime("%d/%m/%Y"),
            "weight": str(row["max_weight"])
        })

    return JsonResponse({"progress": progress_list})
