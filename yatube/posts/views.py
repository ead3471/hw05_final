from django.shortcuts import redirect, render, get_object_or_404
from .models import Follow, Post, Group, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .utils import get_page
from django.utils import timezone
from django.views.decorators.cache import cache_page


User = get_user_model()


@cache_page(20, key_prefix="index_page")
def index(request):
    POSTS_PER_PAGE = 10
    template = 'posts/index.html'
    posts = Post.objects.all()
    context = {
        'page_obj': get_page(request, posts, POSTS_PER_PAGE)
    }

    return render(request, template, context)


def group_posts(request, slug):
    POSTS_PER_PAGE = 10
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group.title}'
    posts = group.posts.all()
    context = {
        'title': title,
        'group': group,
        'page_obj': get_page(request, posts, POSTS_PER_PAGE)
    }

    return render(request, template, context)


def profile(request, username):
    POSTS_PER_PAGE = 10
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.all()

    profile_user_is_in_followings = (Follow.
                                     objects.
                                     filter(user__id=request.user.id).
                                     filter(author=profile_user).exists())

    context = {
        'author': profile_user,
        'page_obj': get_page(request, posts, POSTS_PER_PAGE),
        'following': profile_user_is_in_followings
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'comments': post.comments.all()
    }

    if request.user.is_authenticated:
        context['form'] = CommentForm()

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.pub_date = timezone.now()
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user.username)

    return render(request,
                  'posts/create_post.html',
                  {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.pk)

    return render(request,
                  'posts/create_post.html',
                  {'form': form,
                   'is_edit': True})


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


@login_required
def follow_index(request):
    POSTS_PER_PAGE = 10
    user_follows_authors_ids = (Follow.
                                objects.
                                filter(user=request.user).
                                values_list("author__id", flat=True))

    user_follow_authors_posts = (Post.
                                 objects.
                                 filter(
                                     author__id__in=user_follows_authors_ids))

    context = {
        'page_obj': get_page(request,
                             user_follow_authors_posts,
                             POSTS_PER_PAGE)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.create(user=request.user,
                          author=author)

    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()

    return redirect('posts:profile', username=author)
