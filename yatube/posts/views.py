from django.shortcuts import redirect, get_object_or_404
from .models import Follow, Post, Group, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.views.generic import View
from django.views.generic.edit import BaseCreateView
from django.urls import reverse

User = get_user_model()


class IndexPageView(ListView):
    model = Post
    allow_empty: bool = True
    template_name: str = 'posts/index.html'
    paginate_by: int = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class GroupPageView(ListView):
    model = Post
    allow_empty: bool = True
    template_name: str = 'posts/group_list.html'
    paginate_by: int = 10

    def get_queryset(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])
        group_posts = self.group.posts.all()
        return group_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


class ProfilePageView(ListView):
    model = Post
    allow_empty: bool = True
    template_name: str = 'posts/profile.html'
    paginate_by: int = 10

    def get_queryset(self):
        self.author = get_object_or_404(User,
                                        username=self.kwargs['username'])
        author_posts = self.author.posts.all()
        return author_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user_is_in_followings = (Follow.
                                         objects.
                                         filter(user__id=self.request.user.id).
                                         filter(author=self.author).exists())

        context['author'] = self.author
        context['following'] = profile_user_is_in_followings
        return context


class PostDetailView(DetailView):
    template_name = 'posts/post_detail.html'
    model = Post
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context['comments'] = self.get_object().comments.all()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm
    context_object_name = "form"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return redirect('posts:profile', username=self.request.user.username)


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'posts/create_post.html'
    fields = ['text', 'image', 'group']

    def get_success_url(self):
        return reverse('posts:post_detail', args=(self.get_object().pk,))

    def get(self, request, pk):
        if self.get_object().author != request.user:
            return redirect('posts:post_detail', post_id=self.get_object().pk)
        return super().get(request, pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        if self.get_object().author != self.request.user:
            return redirect('posts:post_detail', post_id=self.get_object().pk)

        form.save()
        return redirect('posts:post_detail', post_id=self.get_object().pk)


class AddCommentView(LoginRequiredMixin, BaseCreateView):
    model = Comment
    fields = ['text']
    form_class: CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment = form.save(commit=False)  # type: Comment
        comment.author = self.request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post.pk)


class FollowView(LoginRequiredMixin, View):
    def get(self, request, username):

        author = get_object_or_404(User, username=username)
        follow_exist = author.id in (request.
                                     user.
                                     follower.
                                     all().
                                     values_list('author', flat=True))

        if author != request.user and not follow_exist:
            Follow.objects.create(user=request.user, author=author)
        return redirect('posts:profile', username=username)


class FollowIndexView(LoginRequiredMixin, ListView):
    model = Post
    allow_empty: bool = True
    template_name: str = 'posts/follow.html'
    paginate_by: int = 10

    def get_queryset(self):
        return (Post.
                objects.
                filter(author__following__user=self.request.user))


class UnfollowView(LoginRequiredMixin, View):
    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        follows = Follow.objects.filter(user=request.user, author=author)
        follows.delete()
        return redirect('posts:profile', username=author)
