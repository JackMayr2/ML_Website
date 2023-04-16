from django.urls import path, reverse_lazy
from . import views

app_name = 'learnings'
urlpatterns = [
    path('', views.LearningListView.as_view(), name='all'),
    path('learnings/<int:pk>', views.LearningDetailView.as_view(), name='learning_detail'),
    path('learning/create',
         views.LearningCreateView.as_view(success_url=reverse_lazy('learnings:all')), name='learning_create'),
    path('learnings/<int:pk>/update',
         views.LearningUpdateView.as_view(success_url=reverse_lazy('learnings:all')), name='learning_update'),
    path('learnings/<int:pk>/delete',
         views.LearningDeleteView.as_view(success_url=reverse_lazy('learnings:all')), name='learning_delete'),
    path('learning_picture/<int:pk>', views.stream_file, name='learning_picture'),
    path('learning/<int:pk>/comment',
         views.CommentCreateView.as_view(), name='learning_comment_create'),
    path('comment/<int:pk>/delete',
         views.CommentDeleteView.as_view(success_url=reverse_lazy('learnings')), name='learning_comment_delete'),
    path('learning/<int:pk>/favorite',
         views.AddFavoriteView.as_view(), name='learning_favorite'),
    path('learning/<int:pk>/unfavorite',
         views.DeleteFavoriteView.as_view(), name='learning_unfavorite'),
]
