from django.contrib import admin
from django.urls import path
from gymsisAPI.views import exercise_detail, exercises, get_saved_session, login_user, measurements, register_user, session_detail, sessions, user_exercise_detail, user_exercises

# Main routes used by the desktop app
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', register_user),
    path('auth/login/', login_user),
    path('auth/session/', get_saved_session),
    path('sessions/', sessions),
    path('sessions/<int:session_id>/', session_detail),
    path('exercises/', exercises),
    # exercise_id is a string because it includes the type too, for example cardio-3.
    # what this achieves is that we can reuse this detail endpoint for the two different
    # types of exercises
    path('exercises/<str:exercise_id>/', exercise_detail),
    path('user-exercises/', user_exercises),
    path('user-exercises/<int:exercise_id>/', user_exercise_detail),
    path('profile/', measurements),
]
