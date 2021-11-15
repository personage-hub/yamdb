from django.contrib import admin
from django.conf import settings

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    'role')
    empty_value_display = settings.VOID
