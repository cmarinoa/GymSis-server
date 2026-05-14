# Build the saved exercise dictionary shown to the frontend
def build_user_exercise_data(exercise):
    return {
        "exercise_id": exercise.id,
        "name": exercise.name,
        "is_active": exercise.is_active
    }


# Check if the exercise name follows some basic rules
def validate_user_exercise_name(name):
    if not name:
        return "Exercise name is required"

    if len(name) > 120:
        return "Exercise name must have 120 characters or fewer"

    return None
