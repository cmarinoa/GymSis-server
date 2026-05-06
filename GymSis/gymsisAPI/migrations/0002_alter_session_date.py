# Generated manually for the session date field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gymsisAPI', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='date',
            field=models.DateField(),
        ),
    ]
