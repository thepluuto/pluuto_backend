# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_scratchprize_expiry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='scratchcard',
            name='prize',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='won_cards', to='events.scratchprize'),
        ),
    ]
