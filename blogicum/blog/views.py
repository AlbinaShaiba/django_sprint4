from django.conf import settings

from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from django.views.generic import (CreateView, DeleteView, DetailView,
                                  ListView, UpdateView)

from django.shortcuts import get_object_or_404, render, redirect

from django.urls import reverse_lazy

from .utils import count_comments, get_published_posts, paginate_queryset

from .models import Category, Comment, Post

from .forms import CommentForm, PostForm, UserForm


User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    """Only logged in users can edit/delete
    Without authentication redirect to blog:post_detail
    """

    pk_url_kwarg = 'post_id'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs['post_id'])

    def get_success_url(self):
        return redirect('blog:post_detail', self.kwargs['post_id'])


"User-model related view-functions and CBV-s"


class ProfileDetailView(DetailView):
    """Profile detail"""

    model = User
    template_name = 'blog/profile.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User,
                                 username=self.kwargs['username'])

    def get_queryset(self, queryset=None):
        if self.request.user == self.get_object():
            page_obj = count_comments(
                Post.objects.filter(
                    author=self.get_object().id).order_by('-pub_date'))
        else:
            page_obj = count_comments(get_published_posts(
                Post.objects.filter(
                    author=self.get_object().id).order_by('-pub_date')))

        page_obj = paginate_queryset(self.request,
                                     page_obj,
                                     settings.PAGINATION_PER_PAGE)
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        context['page_obj'] = self.get_queryset()
        context['user'] = self.request.user
        return context


@login_required
def edit_profile(request):
    """View_function to edit profile"""
    username = request.user.username
    instance = get_object_or_404(User, username=username)
    form = UserForm(request.POST or None, instance=instance)
    author = request.user
    if form.is_valid():
        form = form.save(commit=False)
        form.save()
        return redirect('blog:profile', author)
    return render(request, 'blog/user.html', {'form': form})



"Post-model related view-functions and CBV-s"


class PostListView(ListView):
    """CBV class to display homepage with published posts"""

    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        page_obj = count_comments(get_published_posts(
            Post.objects.order_by('-pub_date')))

        return paginate_queryset(self.request,
                                 page_obj,
                                 settings.PAGINATION_PER_PAGE)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = self.get_queryset()
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    """CBV for creating posts"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class UpdatePostView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """CBV for updating posts"""

    pk_url_kwarg = 'post_id'
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class DeletePostView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """CBV for deleting post"""

    model = Post
    pk_url_kwarg = 'post_id'
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


def post_detail(request, post_id):
    """View-function to display post details and comments"""

    post_for_user = get_object_or_404(Post, id=post_id)
    if request.user.username == post_for_user.author.username:
        post = post_for_user
    else:
        post = get_object_or_404(get_published_posts(
            Post.objects),
            id=post_id)
    comments = (Comment.objects.filter(post=post).
                order_by('created_at'))
    form = CommentForm(request.POST or None)
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """View-function to display all posts for a given category"""
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    page_obj = count_comments(get_published_posts(
        Post.objects).select_related('category', 'location').
                              filter(category__slug=category_slug).
                              order_by('-pub_date'))
    page_obj = paginate_queryset(request,
                                 page_obj,
                                 settings.PAGINATION_PER_PAGE)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


"Comment-model related view-functions and CBV-s"


class CommentCreateView(LoginRequiredMixin, CreateView):
    """CBV class to create comment"""

    pk_url_kwarg = 'post_id'
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post,
                                               pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class UpdateCommentView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """CBV for updating comments"""

    pk_url_kwarg = 'comment_id'
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'


    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post,
                                            pk=self.kwargs['post_id'])
        context['comment'] = get_object_or_404(Comment,
                                               pk=self.kwargs['comment_id'])
        return context


class DeleteCommentView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """CBV for deleting comments"""

    pk_url_kwarg = 'comment_id'
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = Comment.objects.get(pk=self.kwargs['comment_id'])
        return context
