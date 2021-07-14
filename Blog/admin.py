from django.contrib import admin
from .models import Post, Profile, Comment, Reaction, Follower, Notification
# Register your models here.


admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(Follower)
admin.site.register(Notification)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    class Media:
        js = ('Blog/js/tinymce.js',)
