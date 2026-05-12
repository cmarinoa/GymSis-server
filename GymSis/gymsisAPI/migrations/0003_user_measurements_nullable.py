# Generated manually for nullable user measurements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gymsisAPI', '0002_alter_session_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='chest',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='waist',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='hips',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='thighs',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
