# Generated by Django 2.0.6 on 2020-12-08 05:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AUGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(default='Lobby', max_length=16, verbose_name='state')),
                ('code', models.CharField(default='Lobby', max_length=6, unique=True, verbose_name='code')),
            ],
        ),
        migrations.CreateModel(
            name='AUPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField(default=0)),
                ('y', models.FloatField(default=0)),
                ('vx', models.FloatField(default=0)),
                ('vy', models.FloatField(default=0)),
                ('col', models.CharField(default='ff0000', max_length=6, verbose_name='code')),
                ('mask', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='sandbox.AUGame', verbose_name='token')),
            ],
        ),
    ]
