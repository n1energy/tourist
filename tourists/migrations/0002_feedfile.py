# Generated by Django 2.2.2 on 2019-07-11 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tourists', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='files/%Y/%m/%d')),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tourists.Tourist')),
            ],
            options={
                'verbose_name': 'Другие документы',
                'verbose_name_plural': 'Другие документы',
            },
        ),
    ]
