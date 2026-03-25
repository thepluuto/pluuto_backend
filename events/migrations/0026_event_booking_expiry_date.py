# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0025_scratchcard_prize'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='booking_expiry_date',
            field=models.DateField(blank=True, help_text='Last date to book tickets', null=True),
        ),
    ]
