from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import Role, Permission, User, RolePermission, Profile

admin.site.unregister(Group)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'state', 'date_modified', 'date_created')
	search_fields = ('name',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'state', 'date_modified', 'date_created')
	search_fields = ('name',)

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
	list_display = ('role', 'permission', 'state', 'date_modified', 'date_created')
	search_fields = ('role__name', 'permission__name')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = (
		'id_no', 'other_phone_number', 'country', 'occupation', 'employment_type', 'net_salary', 'physical_work_address',
		'country_of_work' ,'work_place_grants_or_allowance', 'income_from_investments', 'currency', 'state',
		'date_modified', 'date_created')
	search_fields = (
		'id_no', 'other_phone_number', 'country__name', 'occupation', 'employment_type', 'country_of_work__name',
		'currency', 'state')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = (
		'username', 'first_name', 'last_name', 'other_name', 'gender', 'phone_number', 'email', 'is_superuser', 'role',
		'terms_and_conditions_accepted', 'language_code', 'last_activity', 'state', 'date_modified', 'date_created')
	list_filter = ('systems', 'organisation', 'is_superuser', 'role', 'date_created')
	search_fields = (
		'username', 'first_name', 'last_name', 'other_name', 'gender', 'phone_number', 'email','systems__name',
		'organisation__name', 'state__name')
	fieldsets = (
		(
			'User Details', {
				'fields': (('username', 'phone_number', 'email'), 'systems', 'organisation', 'role')
			}),
		('Other Info', {'fields': ('first_name', 'last_name', 'other_name', 'language_code')}),
		('Status', {'fields': ('state', ('is_superuser', 'is_staff', 'is_active'), 'terms_and_conditions_accepted')}),
	)


