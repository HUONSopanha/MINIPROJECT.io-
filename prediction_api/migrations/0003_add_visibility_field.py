# Generated manually to add visibility field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prediction_api', '0002_auto_20250525_2039'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherprediction',
            name='visibility',
            field=models.FloatField(default=10.0),
        ),
    ]
