from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from .models import Post, Profile, Comment, Reaction, Follower, Notification
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db.models import Q
from math import ceil
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from random import shuffle
from django.conf import settings
import os
from django.contrib import messages
from django.core.mail import send_mail
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
import json
from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
# Create your views here.


# homepage view


def home(request):
    Posts = Post.objects.all().order_by('-created_on')

    # pagination logic
    page = request.GET.get('page', 1)
    paginator = Paginator(Posts, 6)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'Blog/index.html', {'posts': posts})


# about view


def about(request):
    return render(request, 'Blog/about.html')


# send message for contacting


def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone_no = request.POST['phone']
        message = request.POST['message']

        # logic for sending mail
        if name and email and phone_no and message:
            email_from = settings.EMAIL_HOST_USER
            recipient_list = ['piyushsati311999@gmail.com',
                              'piyushsati1999@gmail.com', ]
            subject = 'Hi someone is trying to reach you from Blogjet '
            try:
                send_mail(
                    subject, f'Name: {name} \nemail: {email} \nphone_no: {phone_no} \nMessage: {message} \n', email_from, recipient_list)
                messages.add_message(
                    request, messages.SUCCESS, 'Message sent successfully!')
            except Exception:
                messages.add_message(
                    request, messages.ERROR, 'Error ocurred!')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Missing some required field values!')
    return render(request, 'Blog/contact.html')


# view a post


def post(request, postslug, pk):
    post = Post.objects.get(pk=pk)

    # logic for post views and fetching likes dislikes comments for a post
    post.views += 1
    post.save()
    allcomments = post.comments.filter(
        post=post, active=True, parent__isnull=True).reverse()
    userreaction = 0
    if request.user.is_authenticated:
        userreaction = Reaction.objects.filter(post=post, user=request.user).first(
        ).reaction if Reaction.objects.filter(post=post, user=request.user).exists() else 0
    return render(request, 'Blog/post.html', {'post': post, 'comments': allcomments, 'userreaction': userreaction})


# post a newpost


def new_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            posttitle = request.POST['title']
            posttagline = request.POST['tline']
            postcontent = request.POST["content"]
            postcategory = request.POST['category']

            # logic for adding newpost
            if posttitle and posttagline and postcategory and postcontent:
                addedpost = Post(title=posttitle, tagline=posttagline,
                                 author=request.user, content=postcontent, category=postcategory)
                addedpost.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Post posted successfully!')
            else:
                messages.add_message(
                    request, messages.ERROR, 'Missing some required field values!')
        return render(request, 'Blog/new_post.html')
    messages.add_message(request, messages.ERROR, 'Login to add a post!')
    return render(request, 'Blog/login.html', {'redirect': 'New-Post'})


# signup


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(
        max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2',)

# create account for a user


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.add_message(
                    request, messages.ERROR, 'A user already exists with this email!')
                return redirect('Signup')
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            authenticate(username=username, password=raw_password)
            messages.add_message(
                request, messages.SUCCESS, 'Account created successfully!')
            return redirect('Signin')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = SignUpForm()
    return render(request, 'Blog/signup.html', {'form': form})


# login in the valid user

def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST['uname']
            password = request.POST['pass']
            redirect_url_name = request.POST.get('redirect', 'Home')
            if username and password:
                user = authenticate(
                    request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.add_message(
                        request, messages.SUCCESS, f'Welcome {request.user.username} to Blogjet')
                    return redirect(redirect_url_name)
                else:
                    messages.add_message(
                        request, messages.ERROR, 'Invalid Credentials')
            else:
                messages.add_message(
                    request, messages.ERROR, 'Missing some required field values!')
            if redirect_url_name != 'Home':
                return render(request, "Blog/login.html", {'redirect': redirect_url_name})
        return render(request, 'Blog/login.html')
    else:
        messages.add_message(request, messages.SUCCESS,
                             f'Welcome {request.user.username} to Blogjet')
        return redirect('Home')


# logging out the user


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.add_message(request, messages.SUCCESS,
                             'Logged out successfully!')
    return redirect('Home')


# my profile view

def my_profile(request):
    if request.user.is_authenticated:
        posts = Post.objects.filter(
            author=request.user).order_by('-created_on').all()
        # profile=Profile.objects.filter(user=request.user).first()
        profile = request.user.profile.filter().first()

        notifications = Notification.objects.filter(
            user_notify=request.user).order_by('-date').all()

        comments = Comment.objects.filter(
            user_posting=request.user).order_by('-created').all()
        following = Follower.objects.filter(
            user=request.user).order_by('-date').all()
        fuser = []
        for usr in following:
            fuser.append(Profile.objects.filter(user=usr.follow).first())
        followinguser = zip(following, fuser)
        likedposts = Reaction.objects.filter(
            user=request.user, reaction=1).order_by('-created').all()
        dislikedposts = Reaction.objects.filter(
            user=request.user, reaction=-1).order_by('-created').all()
        return render(request, 'Blog/my_profile.html', {'profile': profile, 'posts': posts, 'likedposts': likedposts, 'dislikedposts': dislikedposts,
                                                        'comments': comments, 'notifications': notifications, 'followinguser': followinguser,
                                                        })
    return redirect('Signin')


# change password of a user


def change_pwd(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return redirect('Changepwd')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'Blog/change_pwd.html', {'form': form})


# update profile pic of user


def update_profile_pic(request):
    if request.user.is_authenticated and request.method == 'POST':
        file = request.FILES['file1']
        if file:
            profile = Profile.objects.filter(user=request.user).first()
            oldpic = profile.profile_pic.name
            profile.profile_pic = file

            # logic for deleting old picture after uploading a new pic for storage optimization

            if str(oldpic) != 'profile_pic/default.jpg':
                os.remove(os.path.join(settings.MEDIA_ROOT,
                                       'profile_pic', oldpic[12:]))
            profile.save()
            messages.add_message(
                request, messages.SUCCESS, 'Profile picture updated!')
        else:
            messages.add_message(
                request, messages.ERROR, 'No image selected to upload!')
        return redirect('My-Profile')
    raise Http404


# update cover pic of a user

def update_cover(request):
    if request.user.is_authenticated and request.method == 'POST':
        file = request.FILES['file2']
        if file:
            profile = Profile.objects.filter(user=request.user).first()
            oldpic = profile.cover_pic.name
            profile.cover_pic = file

            # logic for deleting old picture after uploading a new pic for storage optimization

            if str(oldpic) != 'cover_pic/default.jpg':
                os.remove(os.path.join(settings.MEDIA_ROOT,
                                       'cover_pic', oldpic[10:]))
            profile.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Cover picture updated!')
        else:
            messages.add_message(request, messages.ERROR,
                                 'No image selected to upload!')
        return redirect('My-Profile')
    raise Http404


# view  profile section of user

def view_profile(request, pk):
    if request.user.is_authenticated and pk == request.user.pk:
        return redirect('My-Profile')
    else:
        usr = User.objects.get(pk=pk)
        posts = Post.objects.filter(author=usr).order_by('-created_on').all()
        profile = usr.profile.filter().first()
        comments = Comment.objects.filter(
            user_posting=usr).order_by('-created').all()
        likedposts = Reaction.objects.filter(
            user=usr, reaction=1).order_by('-created').all()
        dislikedposts = Reaction.objects.filter(
            user=usr, reaction=-1).order_by('-created').all()
        if request.user.is_authenticated:
            follow_or_unfollow = Follower.objects.filter(
                user=request.user, follow=usr).exists()
            return render(request, 'Blog/profile.html', {'profile': profile, 'posts': posts, 'likedposts': likedposts, 'dislikedposts': dislikedposts, 'comments': comments, 'follow_or_unfollow': follow_or_unfollow})
        return render(request, 'Blog/profile.html', {'profile': profile, 'posts': posts, 'likedposts': likedposts, 'dislikedposts': dislikedposts, 'comments': comments})


# update profile information view

def update_profile_info(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            uname = request.POST.get('uname')
            email = request.POST.get('email')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            age = request.POST.get('age')
            location = request.POST.get('location')
            bio = request.POST.get('bio')
            if uname and email:
                if request.user.get_username() != uname and User.objects.filter(username=uname).exists():
                    messages.add_message(
                        request, messages.ERROR, 'Username already taken!')
                    return redirect('My-Profile')
                if request.user.email != email and User.objects.filter(email=email).exists():
                    messages.add_message(
                        request, messages.ERROR, 'A user already exists with this email!')
                    return redirect('My-Profile')
                request.user.username = uname
                request.user.email = email
                request.user.first_name = fname
                request.user.last_name = lname
                profile = Profile.objects.filter(user=request.user).first()
                profile.age = age if age else 0
                profile.location = location
                profile.bio = bio
                request.user.save()
                profile.save()
                messages.add_message(
                    request, messages.SUCCESS, "Profile info updated!")
            else:
                messages.add_message(
                    request, messages.ERROR, 'Missing some required field value!')
            return redirect('My-Profile')
    raise Http404


# deleting post

def delete_post(request):
    if request.user.is_authenticated and request.method == 'POST':
        pk = request.POST.get('postpk')
        post = Post.objects.get(pk=pk)
        if post.author == request.user:
            post.delete()
            return HttpResponse('Post deleted')
    raise Http404


# updating a posted post


def update_post(request, pk):
    if request.user.is_authenticated:
        post = Post.objects.get(pk=pk)
        if request.method == 'POST':
            posttitle = request.POST['title']
            posttagline = request.POST['tline']
            postcontent = request.POST["content"]
            post.title = posttitle
            post.tagline = posttagline
            post.content = postcontent
            post.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Post updated successfully!')
            return redirect('My-Profile')
        else:
            return render(request, 'Blog/update_post.html', {'post': post})
    raise Http404


# posting a comment


def add_comment(request, pk):
    if request.method == "POST":
        post = Post.objects.get(pk=pk)
        if request.user.is_authenticated:
            comment = request.POST['comment']
            addedcomment = Comment(
                post=post, user_posting=request.user, content=comment)
            addedcomment.save()
            created = addedcomment.created
            created = str(naturaltime(created))
            data = {'pk': addedcomment.pk, 'user_posting': addedcomment.user_posting.get_username(), 'content': addedcomment.content,
                    'created': created, 'profile_pic': addedcomment.profile_pic.url, 'userpk': addedcomment.user_posting.pk,
                    }
            data = json.dumps(data)
            return HttpResponse(data, content_type='application/json')
        messages.add_message(request, messages.ERROR,
                             'Login to add a comment!')
        return render(request, 'Blog/login.html', {'redirect': f'/Blog/post/{post.slug}/{pk}#add-comment'})

    raise Http404


# post a reply

def add_reply(request, pk):
    if request.method == "POST" and request.user.is_authenticated:
        post = Post.objects.get(pk=pk)
        reply = request.POST['reply']
        cmtpk = request.POST['cmtpk']
        commentrply = Comment.objects.get(pk=cmtpk)
        addedreply = Comment(
            post=post, user_posting=request.user, parent=commentrply, content=reply)
        addedreply.save()
        created = addedreply.created
        created = str(naturaltime(created))
        data = {'pk': addedreply.pk, 'user_posting': addedreply.user_posting.get_username(), 'content': addedreply.content,
                'created': created, 'profile_pic': addedreply.profile_pic.url, 'userpk': addedreply.user_posting.pk,
                }
        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')
    raise Http404


# deleting the posted comment


def delete_comment(request):
    if request.method == "POST" and request.user.is_authenticated:
        commentpk = request.POST['cmntpk']
        comment = Comment.objects.get(pk=commentpk)
        comment.delete()
        return HttpResponse("Comment deleted")
    raise Http404


# post search view


def post_search(request):
    searchquery = request.GET.get('searchquery')
    if searchquery:
        if len(searchquery) > 100:
            Posts = Post.objects.none()
        else:
            Posts = Post.objects.filter(Q(title__icontains=searchquery) | Q(
                tagline__icontains=searchquery) | Q(content__icontains=searchquery))
            Posts = list(Posts)
            temp = Post.objects.all()
            for i in temp:
                if i.author.username.lower() in searchquery.lower() or searchquery.lower() in i.author.username.lower():
                    Posts.append(i)
    else:
        Posts = Post.objects.none()

    # pagination logic
    page = request.GET.get('page', 1)
    paginator = Paginator(Posts, 6)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'Blog/index.html', {'posts': posts, 'searchquery': searchquery, 'Page': 'search_result'})


# filtering and sorting post


def filter_and_sort(request):
    categoryparameter = request.GET.get('ctg')
    sortparameter = request.GET.get('sort')
    # logic for filtering and sorting post

    if categoryparameter == 'All':
        Posts = Post.objects.all()
    else:
        Posts = Post.objects.filter(category=categoryparameter)

    if sortparameter == '1':
        Posts = Posts.order_by('-created_on')
    elif sortparameter == '2':
        Posts = Posts.order_by('created_on')
    elif sortparameter == '3':
        Posts = list(Posts.all())
        shuffle(Posts)
    elif sortparameter == '4':
        Posts = Posts.order_by('-views')
    elif sortparameter == '5':
        r = []
        for i in Posts:
            lkcount = i.no_of_likes
            if lkcount:
                r.append([lkcount, i])
        r.sort(key=lambda a: a[0], reverse=True)
        Posts = []
        for i in r:
            Posts.append(i[1])
    else:
        r = []
        for i in Posts:
            lkcount = i.no_of_dislikes
            if lkcount:
                r.append([lkcount, i])
        r.sort(key=lambda a: a[0], reverse=True)
        Posts = []
        for i in r:
            Posts.append(i[1])

    # pagination logic

    page = request.GET.get('page', 1)
    paginator = Paginator(Posts, 6)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'Blog/index.html', {'posts': posts, 'ctg': categoryparameter, 'sort': sortparameter, 'Page': 'filter_and_sort_result'})


# like or  dislike a post


def post_reaction(request, pk):
    if request.method == 'POST':
        post = Post.objects.get(pk=pk)
        if request.user.is_authenticated:
            if Reaction.objects.filter(user=request.user, post=post).exists():
                Postreaction = Reaction.objects.filter(
                    user=request.user, post=post).first()
            else:
                Postreaction = Reaction(user=request.user, post=post)
            liked = int(request.POST.get('like', 0))
            disliked = int(request.POST.get('dislike', 0))

            # logic for liking and  disliking the post

            if (Postreaction.reaction == -1 and disliked == -1) or (Postreaction.reaction == 1 and liked == 1):
                Postreaction.reaction = 0
            else:
                Postreaction.reaction = liked+disliked
            Postreaction.save()
            d = 'r'
            l = 'r'
            if Postreaction.reaction == 1:
                l = 's'
            elif Postreaction.reaction == -1:
                d = 's'
            else:
                Postreaction.delete()
            data = {'likescount': post.no_of_likes,
                    'dislikescount': post.no_of_dislikes, 'd': d, 'l': l}
            data = json.dumps(data)
            return HttpResponse(data, content_type='application/json')
        messages.add_message(request, messages.ERROR,
                             'Login to like or dislike the post!')
        return render(request, 'Blog/login.html', {'redirect': f'/Blog/post/{post.slug}/{pk}'})
    raise Http404


# follow a user


def follow(request):
    if request.method == 'POST':
        pk = request.POST['follow']
        if request.user.is_authenticated:
            user = User.objects.get(pk=pk)

            # logic for following a user

            if not Follower.objects.filter(user=request.user, follow=user).exists():
                follower = Follower(user=request.user, follow=user)
                follower.save()
                return HttpResponse('Followed')
        messages.add_message(request, messages.ERROR,
                             'Login to follow or unfollow!')
        return render(request, 'Blog/login.html', {'redirect': f'/Blog/viewprofile/{pk}'})

    raise Http404


# unfollow a followed user


def unfollow(request):
    if request.method == 'POST' and request.user.is_authenticated:
        pk = request.POST['unfollow']
        user = User.objects.get(pk=pk)

        # logic for unfollowing a followed user

        if Follower.objects.filter(user=request.user, follow=user).exists():
            follower = Follower.objects.filter(user=request.user, follow=user)
            follower.delete()
            return HttpResponse('Unfollowed')
    raise Http404


# delete the notification

def delete_notification(request):
    if request.user.is_authenticated and request.method == 'POST':
        notificationpk = request.POST['delnoti']
        notification = Notification.objects.get(pk=notificationpk)
        notification.delete()
        return HttpResponse('Notification deleted')
    raise Http404


# custom error page handlers

def error_404(request, exception):
    return render(request, 'Blog/error.html', {'code': 404, 'msg': 'page not found'})


def error_500(request):
    return render(request, 'Blog/error.html', {'code': 500, 'msg': 'Internal Error'})


def error_400(request, exception):
    return render(request, 'Blog/error.html', {'code': 400, 'msg': 'Bad request'})
