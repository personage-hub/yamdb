from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitlesFilter
from .mixins import DestroyCreateListViewSet
from .paginations import CustomUserPagination
from .permisions import (AdminUrlUserPermission,
                         AuthorModeratorAdminOrReadOnly,
                         ReadOnly)
from .serializers import (AuthenticationSerializer,
                          CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          LoginSerializer,
                          ReadOnlyTitleSerializer,
                          ReviewSerializer, TitleSerializer,
                          UserSerializer)

MESS_TOPIC_MAIL = 'Код подтверждения'
LEN_COD_CONF = 6
NOT_FOUND = 'Запрошенного объекта не существует'


class AuthenticationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AuthenticationSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, serializer.data['email'])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_200_OK,
                        headers=headers)

    def perform_create(self, serializer, email):
        confirmation_code = get_random_string(length=LEN_COD_CONF)
        serializer.save(
            confirmation_code=confirmation_code)
        self.send_message(confirmation_code, email)

    def send_message(self, confirmation_code, email):
        send_mail(
            MESS_TOPIC_MAIL,
            confirmation_code,
            settings.EMAIL_HOST_USER,
            [email])


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('=username',)
    permission_classes = (AdminUrlUserPermission,)
    pagination_class = CustomUserPagination


@api_view(['GET', 'PATCH', 'DELETE', 'PUT'])
def admin_putch_get_delete_users(request, username):
    if request.method == 'PUT':
        return Response(status=status.HTTP_403_FORBIDDEN)
    if (request.user.is_authenticated
            and (request.user.is_staff
                 or request.user.is_superuser
                 or request.user.role == 'admin')):
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'PATCH'])
def user_putch_get_user(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id=request.user.id)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if not user.is_staff or not user.is_superuser:
                    user.role = 'user'
                    user.save
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


class GenreViewSet(DestroyCreateListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ('name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)

    def get_permissions(self):
        if self.request.user.is_anonymous:
            return (ReadOnly(),)
        if (self.request.user.is_superuser
           or self.request.user.role == 'admin'):
            return (AdminUrlUserPermission(),)
        return (ReadOnly(),)


class CategoryViewSet(DestroyCreateListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ('name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)

    def get_permissions(self):
        if self.request.user.is_anonymous:
            return (ReadOnly(),)
        if (self.request.user.is_superuser
                or self.request.user.role == 'admin'):
            return (AdminUrlUserPermission(),)
        return (ReadOnly(),)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filterset_class = TitlesFilter
    filter_backends = [DjangoFilterBackend]
    pagination_class = CustomUserPagination

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyTitleSerializer
        return TitleSerializer

    def get_permissions(self):
        if self.request.user.is_anonymous:
            return (ReadOnly(),)
        if (self.request.user.is_superuser
                or self.request.user.role == 'admin'):
            return (AdminUrlUserPermission(),)
        return (ReadOnly(),)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)
    pagination_class = CustomUserPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)
    pagination_class = CustomUserPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, pk=title_id)
        review = get_object_or_404(Review, pk=review_id)
        if review in title.reviews.all():
            return review.comments.all()
        raise Http404(NOT_FOUND)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, pk=title_id)
        review = get_object_or_404(Review, pk=review_id)
        if review not in title.reviews.all():
            raise Http404(NOT_FOUND)
        serializer.save(author=self.request.user, review=review)
