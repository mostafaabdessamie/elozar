from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import *

urlpatterns = [
    path('', home_maths, name='home_maths'),
    path('home_chate', home_chat, name='home_chat'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
            
    path('users/', CustomUserListView.as_view(), name='customuser_list'),
    path('users/<int:pk>/', CustomUserDetailView.as_view(), name='customuser_detail'),
    path('users/create/', CustomUserCreateView.as_view(), name='customuser_create'),
    path('users/<int:pk>/update/', CustomUserUpdateView.as_view(), name='customuser_update'),
    path('users/<int:pk>/delete/', CustomUserDeleteView.as_view(), name='customuser_delete'),

    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),

    path('friend/request/<int:user_id>/', FriendRequestView.as_view(), name='friend_request'),
    path('friend/requests/', FriendRequestListView.as_view(), name='friend_request_list'),
    path('friend/accept/<int:pk>/', FriendRequestAcceptView.as_view(), name='friend_request_accept'),

    path('posts/', PostListView.as_view(), name='post_list'),
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:post_id>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('post/<int:post_id>/like/', LikeView.as_view(), name='like_post'),
    
    path('chat/', ChatListView.as_view(), name='chat_list'),
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat_detail'),
     path('chat/create/', ChatCreateView.as_view(), name='chat_create'),
    path('chat/<int:chat_id>/message/', MessageCreateView.as_view(), name='message_create'),

    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('notifications/read/', mark_all_read, name='mark_all_read'),
    path('notifications/<int:pk>/', notification_click, name='notification_click'),
    path('fix-notifs/', fix_old_notifications, name='fix_old_notifications'),

    path('send_message/', SendMessageView.as_view(), name='send_message'),
    path('send_friend_request/', SendFriendRequestView.as_view(), name='send_friend_request'),

    path('comment/create/<int:post_id>/', comment_create, name='comment_create'),
    path('like/post/<int:post_id>/', like_post, name='like_post'),
    path('friend-request/send/', send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('friend-request/reject/<int:request_id>/', reject_friend_request, name='reject_friend_request'),
    path('message/send/', send_message, name='send_message'),
]
