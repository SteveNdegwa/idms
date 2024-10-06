from django.contrib import admin

from users.models import Role, Permission, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'state', 'date_modified', 'date_created')
	search_fields = ('name',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'state', 'date_modified', 'date_created')
	search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = (
		'username', 'first_name', 'last_name', 'other_name', 'phone_number', 'email', 'is_superuser', 'role',
		'terms_and_conditions_accepted', 'language_code', 'last_activity', 'state', 'date_modified', 'date_created')
	list_filter = ('systems', 'organisation', 'is_superuser', 'role', 'date_created')
	search_fields = (
		'username', 'first_name', 'last_name', 'other_name', 'phone_number', 'email','systems__name',
		'organisation__name', 'state__name')
	fieldsets = (
		(
			'Useral Details', {
				'fields': (('username', 'phone_number', 'email'), 'systems', 'organisation', 'role')
			}),
		('Other Info', {'fields': ('first_name', 'last_name', 'other_name', 'language_code')}),
		('Status', {'fields': ('state', ('is_superuser', 'is_staff', 'is_active'), 'terms_and_conditions_accepted')}),
	)


