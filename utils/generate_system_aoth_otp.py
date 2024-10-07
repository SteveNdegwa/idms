# -- coding: utf-8 --
"""
OAuthHelper used in the API
"""

import base64
import os
import logging
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from cryptography.hazmat.primitives.hashes import SHA1

from django.conf import settings

lgr = logging.getLogger(__name__)


# noinspection SpellCheckingInspection, PyBroadException
class OAuthHelper(object):
	@staticmethod
	def generate_device_otp():
		""" Used to generate OneTimePassword for device verification """
		key = os.urandom(20)
		key_text = base64.b64encode(key)
		totp = TOTP(key, 6, SHA1(), settings.OTP_VALID_SECONDS, backend=default_backend())
		time_value = time.time()
		totp_value = totp.generate(time_value)
		return totp_value, key_text, time_value

	@staticmethod
	def verify_device(key_text, totp_to_verify, time_value):
		""" Used to verify OneTimePassword sent to the device """
		try:
			key_decoded = base64.b64decode(key_text)
			totp = TOTP(key_decoded, 6, SHA1(), settings.OTP_VALID_SECONDS, backend=default_backend())
			totp.verify(totp_to_verify.encode(), time_value)
			return True
		except Exception as e:
			pass
		return False