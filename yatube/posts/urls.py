from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Последние обновления
    path('', views.IndexPageView.as_view(), name='index'),

    # Посты группы
    path("group/<slug:slug>/",
         views.GroupPageView.as_view(),
         name='group_list'),

    # Профайл пользователя
    path("profile/<str:username>/",
         views.ProfilePageView.as_view(),
         name='profile'),

    # Просмотр записи
    path('posts/<int:post_id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),

    # Добавление записи
    path('create/', views.PostCreateView.as_view(), name='post_create'),

    # Редактирование записи
    path('posts/<int:pk>/edit/',
         views.PostEditView.as_view(),
         name='post_edit'),

    # Добавление поста
    path(
        'posts/<int:post_id>/comment/',
        views.AddCommentView.as_view(),
        name='add_comment'),

    # Страница постов из подписок
    path('follow/',
         views.FollowIndexView.as_view(),
         name='follow_index'),

    # Зарегестрировать подписку на автора
    path(
        'profile/<str:username>/follow/',
        views.FollowView.as_view(),
        name='profile_follow'
    ),

    # Отписаться от автора
    path(
        'profile/<str:username>/unfollow/',
        views.UnfollowView.as_view(),
        name='profile_unfollow'
    ),

]
