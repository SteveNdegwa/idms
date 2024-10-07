import base64
import binascii
import os
from datetime import datetime, timedelta
from django.conf import settings


def generate_token():
	"""
	Generates a standard token to be used for ABC + etc.
	@return:
	"""
	try:
		# return base64.b64encode(binascii.hexlify(os.urandom(15)).decode())
		data_string = binascii.hexlify(os.urandom(15)).decode()
		data_bytes = data_string.encode("utf-8")
		return base64.b64encode(data_bytes)
	except Exception as e:
		print('generate_token Exception: %s', e)
	return None


def token_expiry():
	"""
	callable functions for generating an expiry time for an access_token
	:return: current invoke_time + expiry_time in seconds: expiry_seconds is defined in the settings
	:rtype: datetime
	"""
	from django.utils import timezone as django_tz
	return django_tz.now() + timedelta(seconds=settings.TOKEN_EXPIRY_SECONDS)


def system_token_expiry():
	"""
	callable functions for generating an expiry time for an access_token
	:return: current invoke_time + expiry_time in seconds: expiry_seconds is defined in the settings
	:rtype: datetime
	"""
	from django.utils import timezone as django_tz
	return django_tz.now() + timedelta(seconds=settings.SYSTEM_TOKEN_EXPIRY_SECONDS)








