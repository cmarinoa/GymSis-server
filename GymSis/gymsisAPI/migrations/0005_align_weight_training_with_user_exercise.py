# Generated manually to move weight training data into user exercises

from django.db import migrations, models
import django.db.models.deletion


def copy_weight_training_to_user_exercise(apps, schema_editor):
    SessionTraining = apps.get_model("gymsisAPI", "SessionTraining")
    UserExercise = apps.get_model("gymsisAPI", "UserExercise")

    for session_training in SessionTraining.objects.select_related("session", "training"):
        user_id = session_training.session.user_id
        exercise_name = session_training.training.name

        user_exercise, created = UserExercise.objects.get_or_create(
            user_id=user_id,
            name=exercise_name,
            defaults={"is_active": True}
        )

        session_training.user_exercise = user_exercise
        session_training.save(update_fields=["user_exercise"])


class Migration(migrations.Migration):

    dependencies = [
        ("gymsisAPI", "0004_userexercise"),
    ]

    operations = [
        migrations.AddField(
            model_name="userexercise",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="sessiontraining",
            name="user_exercise",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="gymsisAPI.userexercise"),
        ),
        migrations.RunPython(copy_weight_training_to_user_exercise, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="sessiontraining",
            name="training",
        ),
        migrations.AlterField(
            model_name="sessiontraining",
            name="user_exercise",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="gymsisAPI.userexercise"),
        ),
        migrations.DeleteModel(
            name="WeightTraining",
        ),
    ]
