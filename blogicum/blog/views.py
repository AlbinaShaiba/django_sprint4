from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  ListView, UpdateView)
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .utils import count_comments, paginate_queryset
from .models import Category, Comment, Post
from .forms import CommentForm, PostForm
from .mixins import CreateDeletePostMixin, CreateUpdateDeleteCommentMixin, OnlyAuthorMixin


User = get_user_model()


"User-model related CBV-s"


class ProfileDetailView(DetailView):
    """Profile detail"""

    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(User,
                                 username=self.kwargs['username'])

    def get_queryset(self):
        if self.request.user == self.get_object():
            page_obj = count_comments(
                Post.objects.filter(
                    author=self.get_object().id).order_by('-pub_date'))
        else:
            page_obj = count_comments(Post.published_ordered_obj.all().filter(
                    author=self.get_object().id))

        return paginate_queryset(self.request,
                                page_obj,
                                settings.PAGINATION_PER_PAGE)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        context['page_obj'] = self.get_queryset()
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """CBV to update profile"""

    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.get_object()})


"Post-model related CBV-s"


class PostListView(ListView):
    """CBV class to display homepage with published posts"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    def get_queryset(self):
        return count_comments(Post.published_ordered_obj.all())

class CreatePostView(LoginRequiredMixin, CreateDeletePostMixin, CreateView):
    """CBV for creating posts"""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdatePostView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """CBV for updating posts"""

    pk_url_kwarg = 'post_id'
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class DeletePostView(LoginRequiredMixin, CreateDeletePostMixin, 
                     OnlyAuthorMixin, DeleteView):
    """CBV for deleting post"""
    
    pk_url_kwarg = 'post_id'

    
class PostDetailView(DetailView):
    """CBV to display post details"""

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'
    

    def get_object(self):
        post_for_user = get_object_or_404(Post, id=self.kwargs['post_id'])
        if self.request.user == post_for_user.author:
            post = post_for_user
        else:
            post = get_object_or_404(Post.published_ordered_obj.all(),
                                    id=self.kwargs['post_id'])
        return post

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm(self.request.POST or None)
        context['comments'] = self.get_object().comments.order_by('created_at')
        return context


class CategoryPostsView(ListView):
    """CBV displays published posts for a given category"""

    model = Post
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'

    def get_object(self):
        category = get_object_or_404(Category,
                                 slug=self.kwargs['category_slug'],
                                 is_published=True)
        return category
    
    def get_queryset(self):
        page_obj = count_comments(Post.published_ordered_obj.all()
            .select_related('category', 'location')
            .filter(category__slug=self.kwargs['category_slug'])
            )
        page_obj = paginate_queryset(self.request,
                                 page_obj,
                                 settings.PAGINATION_PER_PAGE)
        
        return page_obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        context['page_obj'] = self.get_queryset()
        return context
    

"Comment-model related CBV-s"


class CommentCreateView(LoginRequiredMixin, CreateUpdateDeleteCommentMixin, CreateView):
    """CBV class to create comment"""

    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post,
                                               pk=self.kwargs['post_id'])
        return super().form_valid(form)


class UpdateCommentView(LoginRequiredMixin, CreateUpdateDeleteCommentMixin, 
                        OnlyAuthorMixin, UpdateView):
    """CBV for updating comments"""

    pk_url_kwarg = 'comment_id'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post,
                                            pk=self.kwargs['post_id'])
        context['comment'] = get_object_or_404(Comment,
                                               pk=self.kwargs['comment_id'])
        return context


class DeleteCommentView(LoginRequiredMixin, CreateUpdateDeleteCommentMixin, 
                        OnlyAuthorMixin, DeleteView):
    """CBV for deleting comments"""

    pk_url_kwarg = 'comment_id'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])
