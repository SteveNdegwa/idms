from django.core.exceptions import ValidationError
from django.db import models

from base.models import BaseModel, State
from users.models import User
from utils.token_manager import token_expiry, generate_token


class Identity(BaseModel):
	token = models.CharField(default=generate_token, max_length=200)
	expires_at = models.DateTimeField(default=token_expiry)
	user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
	source_ip = models.GenericIPAddressField(
		max_length=50, null=True, blank=True, help_text='The originating IP Address.')
	totp_key = models.CharField(max_length=100, blank=True, null=True)
	totp_time_value = models.CharField(max_length=100, blank=True, null=True)
	state = models.ForeignKey(State, default=State.activation_pending, on_delete=models.CASCADE)

	SYNC_MODEL = False

	def _str_(self):
		return '%s - %s' % (self.user,  self.source_ip)

	class Meta(object):
		ordering = ('-date_created',)

	def clean(self):
		if self.user is None:
			raise ValidationError('The User MUST be set for the token.')
		super(Identity, self).clean()

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		if not self.user:
			raise ValidationError('The user must be set for the token.')
		super(Identity, self).save(force_insert, force_update, using, update_fields)

	def extend(self):
		"""
		Extends the access token for the model.
		@return: The model instance after saving.
		@rtype: Identity
		"""
		# noinspection PyBroadException
		try:
			self.expires_at = token_expiry()
			self.save()
		except Exception:
			pass
		return self

