from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Comment, Post
from .forms import CommentForm, PostForm


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
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})
    

"""Create/Delete posts mixins"""


class CreateDeletePostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})
    

class CreateUpdateDeleteCommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})
