from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='Home'),
    path('about', views.about, name='About'),
    path('contact', views.contact, name='Contact'),
    path('post/<slug:postslug>/<int:pk>', views.post, name='Post'),
    path('newpost', views.new_post, name='New-Post'),
    path('signin', views.user_login, name='Signin'),
    path('userlogout', views.user_logout, name='Logout'),
    path('signup', views.signup, name='Signup'),
    path('myprofile', views.my_profile, name='My-Profile'),
    path('follow', views.follow, name='Follow'),
    path('unfollow', views.unfollow, name='Unfollow'),
    path('changepassword', views.change_pwd, name='Changepwd'),
    path('updateprofilepic', views.update_profile_pic, name='Update-Pic'),
    path('updatepost/<int:pk>,', views.update_post, name='Update-Post'),
    path('deletepost', views.delete_post, name='Del-Post'),
    path('addcomment/<int:pk>', views.add_comment, name='Add-Comnt'),
    path('delcomment', views.delete_comment, name='Del-Comnt'),
    path('addreply/<int:pk>', views.add_reply, name='Add-Reply'),
    path('postreaction/<int:pk>', views.post_reaction, name="Post-Rec"),
    path('postsearch', views.post_search, name='Search'),
    path('updatecoverpic', views.update_cover, name='Update-Cover'),
    path('updateprofileinfo', views.update_profile_info, name='Update-Profileinfo'),
    path('viewprofile/<int:pk>', views.view_profile, name='User-Profile'),
    path('filterandsort', views.filter_and_sort, name='Filter-Sort'),
    path('delnotification', views.delete_notification, name='Del-Notification'),
    path('password-reset', auth_views.PasswordResetView.as_view(
        template_name='Blog/password_reset.html'), name='password_reset'),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(
        template_name='Blog/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='Blog/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(
        template_name='Blog/password_reset_complete.html'), name='password_reset_complete'),

]
