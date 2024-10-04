from django.contrib import admin

from systems.models import System


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'date_modified', 'date_created')
	search_fields = ('name',)

