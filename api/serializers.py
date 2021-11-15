from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

MESS_VAL_LOG = 'Поле {} отсутствует или оно некорректно'
SINGLE_REVIEW = 'Можно оставить только один отзыв'


class AuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, *args, **kwargs):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'], )
        user.save()
        return user

    def validate(self, data):
        if data['username'] in ('me', 'Me'):
            raise ValidationError(MESS_VAL_LOG.format('username'))
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role',)
        model = User


class LoginSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields['confirmation_code'] = serializers.CharField(max_length=6)
        del self.fields['password']

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'token': str(refresh.access_token)}

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if data['confirmation_code'] != user.confirmation_code:
            raise ValidationError(MESS_VAL_LOG.format('confirmation_code'))
        return self.get_tokens_for_user(user)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        exclude = ('title',)
        read_only_fields = ('id', 'author', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if author.reviews.filter(title=title).exists():
            raise serializers.ValidationError(SINGLE_REVIEW)
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        exclude = ('review',)
        read_only_fields = ('id', 'pub_date')


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating'
        )
