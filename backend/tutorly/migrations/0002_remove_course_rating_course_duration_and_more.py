# Generated by Django 5.0.5 on 2025-02-23 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorly', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='rating',
        ),
        migrations.AddField(
            model_name='course',
            name='duration',
            field=models.CharField(default='4 weeks', max_length=50),
        ),
        migrations.AddField(
            model_name='course',
            name='instructor',
            field=models.CharField(default='Unknown Instructor', max_length=255),
        ),
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='course',
            name='syllabus',
            field=models.TextField(default='No syllabus available'),
        ),
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
