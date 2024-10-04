from django.contrib import admin

from organisations.models import Organisation


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
	"""Admin Organization"""
	list_filter = ('country__name',)
	list_display = (
		'name', 'white_label', 'remote_code', 'sync_db', 'show_partial_report', 'show_customer_phone_number',
		'show_customer_total', 'show_customer_highest', 'push_data_manually', 'state', 'date_modified', 'date_created')
	search_fields = ('name',)
	fieldsets = (
		('General Details', {
			'fields': (
				'name', 'country', 'remote_code', 'white_label', 'contact_email', 'push_data_manually', 'show_partial_report',
				'show_customer_phone_number', 'show_customer_total', 'show_customer_highest', 'is_digital_advisor',
				'billing_plan', 'is_billable', 'billable_effective', 'wallet_minimum_balance_amount', 'amount_charged_per_statement',
				'notification_email_on_wallet_balance', 'with_overdraft', 'maximum_overdraft', 'query_no', 'sync_db', 'detailed_till_report',
				'state'
			)
		}),
		('Email Settings', {
			'fields': ('statement_email', 'statement_email_pass')
		}),
		('Feedback API Settings', {
			'fields': (
				'api_feedback_enabled', 'webhook_url', 'api_push_success_report', 'webhook_auth_enabled',
				'api_push_auth_method', 'api_basic_auth_password', 'api_basic_auth_username',
				'special_callback_enabled', 'special_callback_method')
		}),
		('Filter Scoring', {
			'fields': (
				'indebtedness_score', 'impact_score', 'activity_level_score', 'income_score',
				'bs_income_score')
		}),
	)