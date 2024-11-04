from django.contrib import admin

from api.models import APIUser


@admin.register(APIUser)
class APIUserAdmin(admin.ModelAdmin):
	list_display = ('system', 'username', 'state', 'last_activity', 'date_modified', 'date_created')
	search_fields = ('id', 'system__name', 'username', 'state__name')
	exclude = ('password',)