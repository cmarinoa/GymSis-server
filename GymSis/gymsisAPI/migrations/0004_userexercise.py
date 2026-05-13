# Generated manually for user saved exercises

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gymsisAPI', '0003_user_measurements_nullable'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExercise',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=120)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_exercises', to='gymsisAPI.user')),
            ],
        ),
    ]
