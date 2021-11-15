from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (AuthenticationViewSet,
                    CommentViewSet,
                    ReviewViewSet,
                    admin_putch_get_delete_users,
                    user_putch_get_user,
                    CategoryViewSet,
                    GenreViewSet,
                    LoginView,
                    TitleViewSet,
                    UserViewSet)

URL_VERSION = 'v1/'
URL_REVIEW = r'titles/(?P<title_id>\d+)/reviews'
URL_COMMENT = r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments'

router_v1 = DefaultRouter()
router_v1.register('v1/auth/signup',
                   AuthenticationViewSet,
                   basename='autentication')
router_v1.register('v1/users', UserViewSet, basename='users')
router_v1.register('v1/titles', TitleViewSet, basename='Title')
router_v1.register('v1/genres', GenreViewSet, basename='Genre')
router_v1.register('v1/categories', CategoryViewSet, basename='Category')

router_v1.register(URL_VERSION + URL_REVIEW, ReviewViewSet, basename='reviews')
router_v1.register(
    URL_VERSION + URL_COMMENT,
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/users/me/', user_putch_get_user, name='me'),
    path(
        'v1/users/<slug:username>/',
        admin_putch_get_delete_users,
        name='username'),
    path('v1/auth/token/',
         LoginView.as_view(),
         name='token_obtain_pair'),
    path('', include(router_v1.urls)),
]
