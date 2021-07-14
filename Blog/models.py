from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from PIL import Image

# Create your models here.


CATEGORIES = (
    ('Entertainment', 'Entertainment'),
    ('Education', 'Education'),
    ('Sports', 'Sports'),
    ('Technology', 'Technology'),
    ('Food', 'Food'),
    ('Fashion', 'Fashion'),
    ('Travel', 'Travel'),
    ('News', 'News'),
    ('Science', 'Science'),
    ('Lifestyle', 'Lifestyle'),
    ('Fitness', 'Fitness'),
    ('Finance', 'Finance'),
    ('Health', 'Health'),
    ('Political', 'Political'),
    ('Business', 'Business'),
    ('Movie', 'Movie'),
    ('Gaming', 'Gaming'),
    ('Beauty', 'Beauty'),
    ('Others', 'Others'),
)


# post model

class Post(models.Model):
    title = models.CharField(max_length=100)
    tagline = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    views = models.IntegerField(default=0)
    category = models.CharField(max_length=100, choices=CATEGORIES)
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'Post:-{self.title} by {self.author} on {self.created_on}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)

    @property
    def no_of_likes(self):
        return Reaction.objects.filter(post=self, reaction=1).count()

    @property
    def no_of_dislikes(self):
        return Reaction.objects.filter(post=self, reaction=-1).count()

    @property
    def no_of_comments(self):
        return Comment.objects.filter(post=self).count()


# user profile model

class Profile(models.Model):
    bio = models.TextField(max_length=200, blank=True)
    profile_pic = models.ImageField(
        default='profile_pic/default.jpg', upload_to='profile_pic')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='profile')
    cover_pic = models.ImageField(
        default='cover_pic/default.jpg', upload_to='cover_pic')
    age = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

    def save(self, *args, **kwargs):
        print(self.profile_pic.url)

        super().save(*args, **kwargs)
        # for resizing the image
        img = Image.open(self.profile_pic.path)
        cimg = Image.open(self.cover_pic.path)
        if img.height > 250 or img.width > 250:
            output_size = (250, 250)
            img.thumbnail(output_size)
            img.save(self.profile_pic.path)
        if cimg.height > 1500 or cimg.width > 1500:
            coutput_size = (1500, 1500)
            cimg.thumbnail(coutput_size)
            cimg.save(self.cover_pic.path)

        comments = Comment.objects.filter(user_posting=self.user).all()
        for i in comments:
            i.profile_pic = self.profile_pic
            i.save()

    @property
    def followers(self):
        return Follower.objects.filter(follow=self.user).count()

    @property
    def following(self):
        return Follower.objects.filter(user=self.user).count()


# model  for like dislike
REACTION_OPTIONS = (
    (1, 'Like'),
    (-1, 'Dislike'),
    (0, 'No Reaction'),

)


class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    reaction = models.IntegerField(choices=REACTION_OPTIONS, default=0)

    def __str__(self):
        if self.reaction == -1:
            return f'{self.user.username}  disliked {self.post.title} post'
        elif self.reaction == 1:
            return f'{self.user.username}  liked {self.post.title} post'
        else:
            return f'No reaction by {self.user.username}!'

    def save(self, *args, **kwargs):
        if self.reaction == -1 and self.user != self.post.author:
            notification = Notification(
                user_notify=self.post.author, user=self.user, post=self.post, notify_reason='disliked')
            notification.save()
        elif self.reaction == 1 and self.user != self.post.author:
            notification = Notification(
                user_notify=self.post.author, user=self.user, post=self.post, notify_reason='liked')
            notification.save()
        return super(Reaction, self).save(*args, **kwargs)


# model for follow and unfollow


class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follow = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user} started following {self.follow} '

    def save(self, *args, **kwargs):
        notification = Notification(
            user_notify=self.follow, user=self.user, notify_reason='follow')
        notification.save()
        return super(Follower, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        notification = Notification(
            user_notify=self.follow, user=self.user, notify_reason='unfollow')
        notification.save()
        return super(Follower, self).delete(*args, **kwargs)


# model for comment section

class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    user_posting = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    profile_pic = models.ImageField()
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']

    def __str__(self):
        if(self.parent):
            return f'{self.user_posting.username} replied to a comment.'
        else:
            return f'{self.user_posting.username} commented on a post.'

    def save(self, *args, **kwargs):
        profile = Profile.objects.filter(user=self.user_posting).first()
        self.profile_pic = profile.profile_pic
        super(Comment, self).save(*args, **kwargs)

        if self.user_posting != self.post.author:
            notification = Notification(
                user_notify=self.post.author, user=self.user_posting, post=self.post, notify_reason='commented', comment=self)
            notification.save()
        if self.parent and self.parent.user_posting != self.user_posting:
            parent_notification = Notification(
                user_notify=self.parent.user_posting, user=self.user_posting, post=self.post, notify_reason='replied', comment=self)
            parent_notification.save()


NOTIFY_CHOICES = (
    ('welcome', 'Welcome'),
    ('liked', 'Liked'),
    ('disliked', 'Disliked'),
    ('commented', 'Commented'),
    ('replied', 'Replied'),
    ('follow', 'Follow'),
    ('unfollow', 'Unfollowed')
)


# model for notifications

class Notification(models.Model):
    user_notify = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='nofify_user')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, blank=True, null=True)
    notify_reason = models.CharField(
        max_length=50, choices=NOTIFY_CHOICES, default='welcome')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_notify} gets a notification."
