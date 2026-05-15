import json

from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from ..models import Session, User
from .validation_helpers import validate_session_filter_dates


# Build the session dictionary shown to the frontend
def build_session_data(session, session_number):
    return {
        "session_id": session.id,
        "session_number": session_number,
        "date": session.date.strftime("%d/%m/%Y")
    }


# Calculate the visible number for one session inside one user's list
def get_session_number(session):
    ordered_sessions = Session.objects.filter(user_id=session.user_id).order_by("date", "id")

    for index, saved_session in enumerate(ordered_sessions, start=1):
        if saved_session.id == session.id:
            return index

    return None


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

    session_number = get_session_number(session)

    return JsonResponse(
        {
            "message": "Session registered successfully",
            **build_session_data(session, session_number)
        },
        status=201
    )


# Get all sessions from the logged in user
def get_sessions(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User is not logged in"}, status=401)

    date_from_text = request.GET.get("date_from", "")
    date_to_text = request.GET.get("date_to", "")
    date_from, date_to, date_error = validate_session_filter_dates(date_from_text, date_to_text)

    if date_error:
        return JsonResponse({"error": date_error}, status=400)

    sessions = Session.objects.filter(user_id=user_id)

    if date_from:
        sessions = sessions.filter(date__gte=date_from)

    if date_to:
        sessions = sessions.filter(date__lte=date_to)

    sessions = sessions.order_by("date", "id")
    session_list = []

    for index, session in enumerate(sessions, start=1):
        session_list.append(build_session_data(session, index))

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

    session_number = get_session_number(session)

    return JsonResponse({
        "message": "Session updated successfully",
        **build_session_data(session, session_number)
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
