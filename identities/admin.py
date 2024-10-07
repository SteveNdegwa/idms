from django.contrib import admin

from identities.models import Identity


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
	list_display = (
        'token', 'user', 'expires_at', 'source_ip', 'totp_key', 'totp_time_value', 'state', 'date_modified',
        'date_created')
	search_fields = ('token', 'user__username', 'user__id', 'user__first_name', 'state__name')