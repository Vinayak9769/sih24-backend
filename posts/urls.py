from django.urls import path
from .views import comment_post, like_post, post_list, create_post

urlpatterns =[
    path('posts/', post_list, name='post_list'),
    path('posts/<int:post_id>/like/', like_post, name='like_post'),
    path('posts/<int:post_id>/comment/', comment_post, name='comment_post'),
    path('posts/create/', create_post, name='create_post'),
]