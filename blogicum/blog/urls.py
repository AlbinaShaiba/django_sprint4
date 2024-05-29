from django.urls import path

from . import views


app_name = 'blog'
urlpatterns = [
    path('posts/<int:post_id>/edit/', views.UpdatePostView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/', views.DeletePostView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.UpdateCommentView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.DeleteCommentView.as_view(),
         name='delete_comment'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<slug:username>/', views.ProfileDetailView.as_view(),
         name='profile'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),

    path('', views.PostListView.as_view(), name='index'),
]
