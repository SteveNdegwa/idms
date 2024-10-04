from django.contrib import admin

from base.models import State, Country


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'date_modified', 'date_created')
	search_fields = ('name',)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'code', 'state', 'date_modified', 'date_created')
	search_fields = ('name', 'code')
