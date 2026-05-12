import json

from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from ..models import Session, User


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
