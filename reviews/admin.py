from django.contrib import admin
from django.conf import settings

from reviews.models import Category, Genre, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug'
    )
    empty_value_display = settings.VOID


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug'
    )
    empty_value_display = settings.VOID


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'year',
        'description',
        'category'
    )
    empty_value_display = settings.VOID
