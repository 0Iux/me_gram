from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.conf import settings
from .models import Group, Post, User, Follow
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .forms import CommentForm, PostForm


def pagination(request, post_list):
    paginator = Paginator(post_list, settings.QUANTITY_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20)
def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = pagination(request, post_list)
    return render(request, 'posts/index.html', {
        'page_obj': page_obj,
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pagination(request, post_list)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': page_obj,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = pagination(request, post_list)
    if request.user.is_authenticated:
        if not Follow.objects.filter(
            user=request.user, author=author
        ):
            following = False
        else:
            following = True
    else:
        following = False
    return render(request, 'posts/profile.html', {
        'author': author,
        'following': following,
        'page_obj': page_obj,
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None,)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': form,
        'comments': post.comments.all()
    })


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    following = Follow.objects.filter(user=user)
    following_authors = [f.author for f in following]
    post_list = Post.objects.filter(author__in=following_authors)
    page_obj = pagination(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author:
        if not Follow.objects.filter(user=user, author=author):
            Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = Follow.objects.filter(user=user, author=author)
    if follow:
        follow.delete()
    return redirect('posts:profile', username=author.username)
