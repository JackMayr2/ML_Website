from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'articles'
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='all'),
    path('articles/<int:pk>', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/<int:pk>/articlecomment',
         views.ArticleCommentCreateView.as_view(), name='article_comment_create'),
    path('articlecomment/<int:pk>/delete',
         views.ArticleCommentDeleteView.as_view(success_url=reverse_lazy('articles')), name='article_comment_delete'),
    path('article/<int:pk>/articlefavorite',
         views.ArticleAddFavoriteView.as_view(), name='article_favorite'),
    path('article/<int:pk>/articleunfavorite',
         views.ArticleDeleteFavoriteView.as_view(), name='article_unfavorite'),
]