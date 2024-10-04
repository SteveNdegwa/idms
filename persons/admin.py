from django.contrib import admin

from persons.models import Role, Permission, Person


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'state', 'date_modified', 'date_created')
	search_fields = ('name',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'state', 'date_modified', 'date_created')
	search_fields = ('name',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
	list_display = (
		'username', 'first_name', 'last_name', 'other_name', 'phone_number', 'email', 'is_superuser', 'role',
		'terms_and_conditions_accepted', 'language_code', 'last_activity', 'state', 'date_modified', 'date_created')
	list_filter = ('systems', 'organisations', 'is_superuser', 'role', 'date_created')
	search_fields = (
		'username', 'first_name', 'last_name', 'other_name', 'phone_number', 'email','systems__name',
		'organisations__name', 'state__name')
	fieldsets = (
		(
			'Personal Details', {
				'fields': (('username', 'phone_number', 'email'), 'systems', 'organisations', 'role')
			}),
		('Other Info', {'fields': ('first_name', 'last_name', 'other_name', 'language_code')}),
		('Status', {'fields': ('state', ('is_superuser', 'terms_and_conditions_accepted'))}),
	)


