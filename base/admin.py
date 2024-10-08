from django.contrib import admin

from base.models import State, Country, TransactionType, Transaction, NotificationType, Notification


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'date_modified', 'date_created')
	search_fields = ('name',)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'code', 'state', 'date_modified', 'date_created')
	search_fields = ('name', 'code')

@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'date_modified', 'date_created')
	search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = (
		'transaction_type', 'source_ip', 'request', 'response', 'notification_response', 'state', 'date_modified',
		'date_created')
	search_fields = ('transaction_type__name', 'source_ip', 'state')

@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'date_modified', 'date_created')
	search_fields = ('name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = (
		'notification_type', 'title', 'message', 'destination', 'state', 'date_modified', 'date_created')
	search_fields = ('notification_type__name', 'title', 'message', 'destination', 'state')