from django.conf import settings
from django.db import models

from base.models import GenericBaseModel, Country, State


class Organisation(GenericBaseModel):
    BILLING_PLANS = [
        ('Postpaid', 'Postpaid'),
        ('Prepaid', 'Prepaid'),
    ]
    DEFAULT_PLAN = "Prepaid"

    FEEDBACK_SUCCESS_REPORTS = [
        ('SCORES_ONLY', 'SCORES_ONLY'),
        ('FULL_JSON_SUMMARY', 'FULL_JSON_SUMMARY'),
        ('FILLING_PDF_REPORT', 'FILLING_PDF_REPORT'),
    ]
    DEFAULT_SUCCESS_REPORT = "FULL_JSON_SUMMARY"

    API_PUSH_AUTH_METHODS = [
        ('BASIC_AUTH', 'BASIC_AUTH'),
    ]
    API_PUSH_AUTH_DEFAULT = "BASIC_AUTH"

    """ Organization model"""
    country = models.ForeignKey(Country, blank=True, null=True, default=Country.default_country, on_delete=models.CASCADE)
    remote_code = models.TextField(max_length=40, blank=False, null=False, unique=True)
    white_label = models.CharField(max_length=40, null=True, blank=True)
    contact_email = models.EmailField(max_length=100, null=True, blank=True)
    push_data_manually = models.BooleanField(default=False)

    show_partial_report = models.BooleanField(default=False)
    show_customer_phone_number = models.BooleanField(default=False)
    show_customer_total = models.BooleanField(default=False)
    show_customer_highest = models.BooleanField(default=False)

    is_digital_advisor = models.BooleanField(default=False)
    billing_plan = models.CharField(max_length=8, default=DEFAULT_PLAN, blank=False, null=False, choices=BILLING_PLANS)
    is_billable = models.BooleanField(default=True)
    billable_effective = models.DateField(null=True, blank=True)
    wallet_minimum_balance_amount = models.DecimalField(max_digits=15, default=settings.MINIMUM_WALLET_AMOUNT,
                                                        decimal_places=2)
    notification_email_on_wallet_balance = models.EmailField(max_length=254, null=True, blank=True)
    amount_charged_per_statement = models.DecimalField(
        max_digits=10, default=settings.DEFAULT_STATEMENT_CHARGE, decimal_places=2)
    with_overdraft = models.BooleanField(default=False)
    maximum_overdraft = models.DecimalField(max_digits=15, default=settings.DEFAULT_MAXIMUM_OVERDRAFT, decimal_places=2)
    statement_email = models.EmailField(max_length=100, null=True, blank=True)
    statement_email_pass = models.CharField(max_length=50, null=True, blank=True)
    query_no = models.IntegerField(default=1)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    sync_db = models.BooleanField(default=False)
    detailed_till_report = models.BooleanField(default=False)

    """Analysis Submission on API"""
    api_feedback_enabled = models.BooleanField(default=False, help_text='Enable submission of results through webhook')
    webhook_url = models.CharField(max_length=200, null=True, blank=True)
    api_push_success_report = models.CharField(
        max_length=50, default=DEFAULT_SUCCESS_REPORT, blank=True, null=True, choices=FEEDBACK_SUCCESS_REPORTS)
    webhook_auth_enabled = models.BooleanField(default=False, help_text='Authenticate on submission')
    api_push_auth_method = models.CharField(
        max_length=50, default=API_PUSH_AUTH_DEFAULT, blank=True, null=True, choices=API_PUSH_AUTH_METHODS)
    api_basic_auth_username = models.CharField(max_length=100, null=True, blank=True)
    api_basic_auth_password = models.CharField(max_length=100, null=True, blank=True)
    special_callback_enabled = models.BooleanField(default=False, help_text='For special usecases')
    special_callback_method = models.CharField(max_length=100, null=True, blank=True)

    """Scores"""
    indebtedness_score = models.BooleanField(default=True)
    impact_score = models.BooleanField(default=True)
    activity_level_score = models.BooleanField(default=True)
    income_score = models.BooleanField(default=True)
    bs_income_score = models.BooleanField(default=True)

    SYNC_MODEL = False

    def __str__(self):
        return '%s' % self.name

    class Meta(GenericBaseModel.Meta):
        ordering = ('-date_created',)