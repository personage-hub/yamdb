from django.db import models
from django.contrib.auth.models import AbstractUser

USER_ROLES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Админ'),)


class User(AbstractUser):
    username = models.CharField('Логин', max_length=150, unique=True,)
    first_name = models.CharField('Имя', max_length=150, blank=True,)
    last_name = models.CharField('Фамилия', max_length=150, blank=True,)
    email = models.EmailField(
        'Почта',
        max_length=254,
        blank=False,
        unique=True,)
    bio = models.TextField('Биография', blank=True,)
    role = models.CharField(
        max_length=50,
        choices=USER_ROLES,
        blank=True,
        default='user')
    confirmation_code = models.TextField(
        'Код доступа',
        max_length=6,
        blank=True)

    def __str__(self):
        return f'{(self.username)}'

    class Meta:
        ordering = ('-id',)
