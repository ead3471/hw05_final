from multiprocessing import get_context
from django.shortcuts import redirect, render, get_object_or_404
from .models import Follow, Post, Group, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .utils import get_page
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.views.generic import View
from django.views.generic.edit import BaseCreateView
from django.urls import reverse

User = get_user_model()


# def index(request):
#     POSTS_PER_PAGE = 10
#     template = 'posts/index.html'
#     posts = Post.objects.all()
#     context = {
#         'page_obj': get_page(request, posts, POSTS_PER_PAGE)
#     }

#     return render(request, template, context)


class IndexPageView(ListView):
    model = Post
    allow_empty: bool = True
    template_name: str = 'posts/index.html'
    paginate_by: int = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = get_page(self.request,
                                       Post.objects.all(),
                                       10)
        return context


# def group_posts(request, slug):
#     POSTS_PER_PAGE = 10
#     template = 'posts/group_list.html'
#     group = get_object_or_404(Group, slug=slug)
#     title = f'Записи сообщества {group.title}'
#     posts = group.posts.all()
#     context = {
#         'title': title,
#         'group': group,
#         'page_obj': get_page(request, posts, POSTS_PER_PAGE)
#     }

#     return render(request, template, context)


class GroupPageView(ListView):
    model = Post
    allow_empty: bool = True
    template_name: str = 'posts/group_list.html'
    paginate_by: int = 10
    context_object_name = 'object_list'

    def get_queryset(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])
        group_posts = self.group.posts.all()
        return group_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


# def profile(request, username):
#     POSTS_PER_PAGE = 10
#     profile_user = get_object_or_404(User, username=username)
#     posts = profile_user.posts.all()

#     profile_user_is_in_followings = (Follow.
#                                      objects.
#                                      filter(user__id=request.user.id).
#                                      filter(author=profile_user).exists())

#     context = {
#         'author': profile_user,
#         'page_obj': get_page(request, posts, POSTS_PER_PAGE),
#         'following': profile_user_is_in_followings
#     }
#     return render(request, 'posts/profile.html', context)


class ProfilePageView(ListView):
    model = Post
    allow_empty: bool = True
    template_name: str = 'posts/profile.html'
    paginate_by: int = 10
    context_object_name = 'page_obj'

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
        context['following']: profile_user_is_in_followings
        context['page_obj'] = get_page(self.request,
                                       context['page_obj'],
                                       self.paginate_by)
        return context



# def post_detail(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     context = {
#         'post': post,
#         'comments': post.comments.all(),
#         'form': CommentForm()
#     }

#     return render(request, 'posts/post_detail.html', context)

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
        post.created = timezone.now()
        post.author = self.request.user
        post.save()
        return redirect('posts:profile', username=self.request.user.username)



# @login_required
# def post_create(request):
#     form = PostForm(request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.created = timezone.now()
#             post.author = request.user
#             post.save()
#             return redirect('posts:profile', username=request.user.username)

#     return render(request,
#                   'posts/create_post.html',
#                   {'form': form})

class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'posts/create_post.html'
    fields = ['text','image','group']

    def get_success_url(self):
        return reverse('posts:post_detail', args=(self.get_object().pk,))

    def get(self,request,pk):
        if self.get_object().author != request.user:
            return redirect('posts:post_detail', post_id=self.get_object().pk)
        return super().get(request,pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        if self.get_object().author != self.request.user:
            return redirect('posts:post_detail', post_id=self.get_object().pk)

        form.save()
        return redirect('posts:post_detail', post_id=self.get_object().pk)

# @login_required
# def post_edit(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     if post.author != request.user:
#         return redirect('posts:post_detail', post_id=post.pk)

#     form = PostForm(request.POST or None,
#                     files=request.FILES or None,
#                     instance=post)
#     if request.method == "POST":
#         if form.is_valid():
#             form.save()
#             return redirect('posts:post_detail', post_id=post.pk)

#     return render(request,
#                   'posts/create_post.html',
#                   {'form': form,
#                    'is_edit': True})


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)  # type: Comment
            comment.author = request.user
            comment.created = timezone.now()
            comment.post = post
            comment.save()
            return redirect('posts:post_detail', post_id=post.pk)


class AddCommentView(LoginRequiredMixin, BaseCreateView):
    model = Comment
    fields = ['text']
    form_class: CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment = form.save(commit=False)  # type: Comment
        comment.author = self.request.user
        comment.created = timezone.now()
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post.pk)



@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow_exist = request.user.id in (author.
                                       following
                                       .all()
                                       .values_list('user', flat=True))
    if author != request.user and not follow_exist:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=author)

# @login_required
# def follow_index(request):
#     POSTS_PER_PAGE = 10
#     user_follows_authors_ids = (request.
#                                 user.
#                                 follower.
#                                 values_list("author__id", flat=True))

#     following_authors_posts = (Post.
#                                objects.
#                                filter(
#                                    author__id__in=user_follows_authors_ids))

#     context = {
#         'page_obj': get_page(request,
#                              following_authors_posts,
#                              POSTS_PER_PAGE)
#     }
#     return render(request, 'posts/follow.html', context)


class FollowIndexView(LoginRequiredMixin, ListView):
    model = Post
    allow_empty: bool = True
    template_name: str = 'posts/follow.html'
    paginate_by: int = 10
    context_object_name = 'page_obj'

    def get_queryset(self):
        user_following_ids = (self.
                              request.
                              user.
                              follower.
                              values_list("author__id", flat=True))

        following_authors_posts = (Post.
                                   objects.
                                   filter(author__id__in=user_following_ids))

        return following_authors_posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_object_name] = get_page(self.request,
                                                     context
                                                     [self.
                                                      context_object_name],
                                                     self.paginate_by)
        return context

#class FollowView(LoginRequiredMixin, View):


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(user=request.user, author=author)
    follows.delete()
    return redirect('posts:profile', username=author)
