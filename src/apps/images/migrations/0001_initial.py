# Generated by Django 4.0.6 on 2022-07-05 20:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('height', models.IntegerField()),
                ('width', models.IntegerField()),
                ('image', models.ImageField(height_field='height', upload_to='images', width_field='width')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ThumbnailSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('height', models.IntegerField()),
                ('width', models.IntegerField()),
                ('thumbnail', models.ImageField(height_field='height', upload_to='thumbnails', width_field='width')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.image')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]