from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0009_donations_is_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='donations',
            name='organization_name',
            field=models.CharField(blank=True, default='Jamia Mosque Committee', max_length=255),
        ),
    ]
