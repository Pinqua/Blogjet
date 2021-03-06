# Generated by Django 3.1.1 on 2020-09-30 12:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('tagline', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100)),
                ('views', models.IntegerField(default=0)),
                ('category', models.CharField(choices=[('Entertainment', 'Entertainment'), ('Education', 'Education'), ('Sports', 'Sports'), ('Technology', 'Technology'), ('Food', 'Food'), ('Fashion', 'Fashion'), ('Travel', 'Travel'), ('News', 'News'), ('Science', 'Science'), ('Lifestyle', 'Lifestyle'), ('Fitness', 'Fitness'), ('Finance', 'Finance'), ('Health', 'Health'), ('Political', 'Political'), ('Business', 'Business'), ('Movie', 'Movie'), ('Gaming', 'Gaming'), ('Beauty', 'Beauty'), ('Others', 'Others')], max_length=100)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('content', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('reaction', models.IntegerField(default=0)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Blog.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=200)),
                ('profile_pic', models.ImageField(default='profile_pic/default.jpg', upload_to='profile_pic')),
                ('cover_pic', models.ImageField(default='cover_pic/default.jpg', upload_to='cover_pic')),
                ('age', models.IntegerField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=30, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify_reason', models.CharField(choices=[('welcome', 'Welcome'), ('liked', 'Liked'), ('disliked', 'Disliked'), ('commented', 'Commented'), ('follow', 'Follow'), ('unfollow', 'Unfollowed')], default='welcome', max_length=50)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Blog.post')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_notify', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nofify_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('follow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('profile_pic', models.ImageField(upload_to='')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='Blog.comment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='Blog.post')),
                ('user_posting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]
