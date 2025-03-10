# Generated by Django 4.2 on 2025-02-15 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=30, unique=True)),
                ('first_name', models.CharField(db_index=True, max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_name', models.CharField(db_index=True, max_length=30)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('role', models.CharField(blank=True, max_length=30)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.volunteer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.team')),
            ],
        ),
    ]
