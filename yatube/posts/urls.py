from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.IndexPageView.as_view(), name='index'),
    #path("group/<slug:slug>/", views.group_posts, name='group_list'),
    path("group/<slug:slug>/", views.GroupPageView.as_view(), name='group_list'),
    
    # Профайл пользователя
    #path("profile/<str:username>/", views.profile, name='profile'),
    path("profile/<str:username>/",
         views.ProfilePageView.as_view(),
         name='profile'),

    # Просмотр записи
    #path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    # Добавление записи
    #path('create/', views.post_create, name='post_create'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    # Редактирование записи
    #path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/edit/', views.PostEditView.as_view(), name='post_edit'),
    # Добавление поста
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'),
    # Страница постов из подписок
    path('follow/',
         views.follow_index,
         name='follow_index'),
    # Зарегестрировать подписку на автора
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    # Отписаться от автора
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),

]
