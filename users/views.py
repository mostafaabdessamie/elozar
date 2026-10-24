from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile, Friendship, Post, Comment, Like, Chat, Message, Notification
from .forms import CustomUserForm, MessageForm, PostForm, CommentForm, FriendRequestForm, CustomUserUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

def home_maths(request):
    table_multiplication = [[i * j for j in range(1, 11)] for i in range(1, 11)]
    return render(request, 'users/home_maths.html', {'table_multiplication': table_multiplication})

def home_chat(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = Profile.objects.all()

    posts = Post.objects.select_related('user').prefetch_related('comments__user').order_by('-created_at')
    friend_requests = Friendship.objects.filter(to_user=request.user, accepted=False)
    received_messages = Message.objects.filter(receiver=request.user).select_related('sender')
    notifications = Notification.objects.filter(user=request.user, read=False)
    all_users = CustomUser.objects.exclude(id=request.user.id)

    context = {
        'friends': profile,  
        'posts': posts,
        'friend_requests': friend_requests,
        'received_messages': received_messages,
        'notifications': notifications,
        'all_users': all_users,
    }

    return render(request, 'users/home.html', context)

class SendMessageView(FormView):
    form_class = MessageForm
    template_name = 'users/home.html'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home_chat')



class CustomUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'users/customuser/customuser_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 1


class CustomUserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CustomUser
    template_name = 'users/customuser/customuser_detail.html'
    context_object_name = 'profile_user' 

    def test_func(self):
        user = self.get_object()
        return self.request.user.user_type == 3 or self.request.user == user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        u = self.get_object()

        posts = Post.objects.filter(user=u).order_by('-created_at').prefetch_related('likes', 'comments')

        context['posts'] = posts
        context['posts_count'] = posts.count()
        context['likes_received'] = Like.objects.filter(post__user=u).count()
        context['likes_given'] = Like.objects.filter(user=u).count()
        context['friends_count'] = Friendship.objects.filter(from_user=u, accepted=True).count() + Friendship.objects.filter(to_user=u, accepted=True).count()

        return context
    
class CustomUserCreateView(CreateView):
    model = CustomUser
    form_class = CustomUserForm
    template_name = 'users/customuser/customuser_form.html'
    success_url = reverse_lazy('login')

class CustomUserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'users/customuser/customuser_form.html'
    success_url = reverse_lazy('home_chat')

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj or self.request.user.user_type == 1

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_authenticated:
            raise PermissionDenied("Connectez-vous d'abord")
        if request.user != obj and request.user.user_type != 1:
            from django.shortcuts import redirect
            return redirect('home_chat')
        return super().dispatch(request, *args, **kwargs)

class CustomUserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'users/customuser/customuser_confirm_delete.html'
    success_url = reverse_lazy('customuser_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 1:
            return redirect('home_chat') 
        return super().dispatch(request, *args, **kwargs)

class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'users/profile/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self):
        if self.request.user.is_authenticated:
            profile, created = Profile.objects.get_or_create(user=self.request.user)
            return profile
        return None  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            context['friends'] = profile.friends.all()
            context['friend_requests'] = profile.friend_requests.all()
            context['messges'] = Message.objects.filter(receiver=self.request.user)
            context['message_form'] = MessageForm()
            context['friend_request_form'] = FriendRequestForm()
        return context

class ProfileUpdateView(UpdateView):
    model = Profile
    fields = '__all__'
    template_name = 'users/profile/profile_form.html'
    success_url = reverse_lazy('home_chat')

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

class FriendRequestView(CreateView):
    model = Friendship
    fields = []
    template_name = 'users/chat/friend_request.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.to_user = CustomUser.objects.get(pk=self.kwargs['user_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'pk': self.kwargs['user_id']})

class FriendRequestListView(ListView):
    model = Friendship
    template_name = 'users/chat/friend_request_list.html'
    context_object_name = 'friend_requests'

    def get_queryset(self):
        return Friendship.objects.filter(to_user=self.request.user, accepted=False)

class FriendRequestAcceptView(View):
    def get(self, request, *args, **kwargs):
        friendship = get_object_or_404(Friendship, pk=kwargs['pk'])
        friendship.accepted = True
        friendship.save()
        return redirect('friend_request_list')
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'users/post/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'users/post/post_form.html'
    success_url = reverse_lazy('home_chat')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PostDetailView(DetailView):
    model = Post
    template_name = 'users/post/post_detail.html'
    context_object_name = 'post'

class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'users/comment/comment_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.kwargs['post_id']})

class LikeView(View):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['post_id'])
        if request.user.is_authenticated:
            Like.objects.create(post=post, user=request.user)
            return render(request, 'users/comment/like_post.html', {'post': post})
        else:
            raise PermissionDenied("Vous devez être connecté pour aimer un post.")

class ChatListView(ListView):
    model = Chat
    template_name = 'users/chat/chat_list.html'
    context_object_name = 'chats'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            chats =  self.request.user.chats.all()
            return chats
        return Chat.objects.none()


class ChatDetailView(DetailView):
    model = Chat
    template_name = 'users/chat/chat_detail.html'
    context_object_name = 'chat'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = MessageForm()
        return context

    def post(self, request, *args, **kwargs):
        chat = self.get_object()
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.receiver = chat.participants.exclude(id=request.user.id).first()
            message.save()
            return self.get(request, *args, **kwargs)  
        return self.render_to_response({'form': form}) 

class ChatCreateView(CreateView):
    model = Chat
    fields = ['participants']
    template_name = 'users/chat/chat_form.html'
    success_url = reverse_lazy('chat_list')

    def form_valid(self, form):
        chat = form.save(commit=False)
        chat.save()
        form.save_m2m() 
        return super().form_valid(form)


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'users/chat/message_form.html'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.chat = Chat.objects.get(pk=self.kwargs['chat_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('chat_detail', kwargs={'pk': self.kwargs['chat_id']})

class NotificationListView(ListView):
    model = Notification
    template_name = 'users/chat/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, read=False)

class SendMessageView(FormView):
    form_class = MessageForm
    template_name = 'users/profile/profile_detail.html'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'pk': self.request.user.profile.pk})

class SendFriendRequestView(FormView):
    form_class = FriendRequestForm
    template_name = 'users/profile/profile_detail.html'

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'pk': self.request.user.profile.pk})

def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home_chat')
    else:
        form = PostForm()
    return render(request, 'post_form.html', {'form': form})

def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            Notification.objects.create(
                user=post.user,
                message=f"{request.user.username} a commenté votre post.",
                content=comment.content[:100],
                link=f"/users/post/{post.id}/", 
                notif_type='comment',
                related_id=post.id
            )
            return redirect('home_chat')
        
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    Like.objects.get_or_create(post=post, user=request.user)
    if post.user != request.user:
        Notification.objects.create(
            user=post.user,
            message=f"{request.user.username} a aimé votre post.",
            link=f"/users/post/{post.id}/",
            notif_type='like',
            related_id=post.id
        )
    return redirect('home_chat')

def send_friend_request(request):
    if request.method == 'POST':
        to_user_id = request.POST.get('to_user')
        to_user = get_object_or_404(CustomUser, id=to_user_id)
        Friendship.objects.create(from_user=request.user, to_user=to_user)
        return redirect('home_chat')

def accept_friend_request(request, request_id):
    friendship = get_object_or_404(Friendship, id=request_id)
    friendship.accepted = True
    friendship.save()
    return redirect('home_chat')

def reject_friend_request(request, request_id):
    friendship = get_object_or_404(Friendship, id=request_id)
    friendship.delete()
    return redirect('home_chat')

@receiver(post_save, sender=Friendship)
def create_friend_request_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.to_user,
            message=f"{instance.from_user.username} vous a envoyé une demande d'ami."
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.post.user,
            message=f"{instance.user.username} a commenté votre post."
        )

def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect('home_chat')
    
@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def notification_click(request, pk):  
    notif = get_object_or_404(Notification, id=pk, user=request.user)
    notif.read = True
    notif.save()

    if hasattr(notif, 'link') and notif.link:
        link = notif.link.replace('/chat/', '/users/')
        if '/post/' in link:
            return redirect(link)
    return redirect(request.META.get('HTTP_REFERER', 'home_chat'))

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home_chat'))

def fix_old_notifications(request):
    for n in Notification.objects.all():
        if n.link and 'chat/post' in str(n.link):
            n.link = n.link.replace('/chat/', '/users/')
            n.save()
    return redirect('notifications')