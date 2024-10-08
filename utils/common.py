import logging
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.utils import timezone as tz

from pytz import timezone

lgr = logging.getLogger(__name__)
lgr.propagate = False


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_password(length=6):
    """
    This function generates the random passwords for users.
    @param length: The number of characters the password should have. Defaults to 6.
    @type length: int
    @return: The generated password.
    @rtype: str
    """
    import string
    groups = [
        string.ascii_uppercase.replace('O', '').replace('I', ''), string.digits,
        string.ascii_lowercase.replace('o', '').replace('i', '').replace('l', ''), '!#%&+:;?@[]_{}']
    cln = [random.choice(groups[n]) for n in range(4)]
    for m in range(length):
        if len(cln) >= length:
            break
        cln.append(random.choice(groups[int(random.choice('0123'))]))
    random.shuffle(cln)
    return ''.join(cln)

def json_super_serializer(obj):
    """
    Automatic serializer for objects not serializable by default by the JSON serializer.
    Includes datetime, date, Decimal
    @param obj: The object to convert.
    @return: String of the data converted.
    @rtype: str
    """
    if isinstance(obj, datetime):
        # noinspection PyBroadException
        try:
            return obj.strftime('%d/%m/%Y %I:%M:%S %p')
        except Exception:
            return str(obj)
    elif isinstance(obj, date):
        # noinspection PyBroadException
        try:
            return obj.strftime('%d/%m/%Y')
        except Exception:
            return str(obj)
    elif isinstance(obj, (Decimal, float)):
        return str("{:,}".format(round(Decimal(obj), 2)))
    elif isinstance(obj, timedelta):
        return obj.days
    return str(obj)

def entity_timezone_aware(time_stamp, entity_timezone='Africa/Nairobi'):
    """
	Convert datetime to owner timezone
	@param time_stamp: The timestamp we are converting to timezone aware.
	@type time_stamp: datetime
	@param entity_timezone: The timezone for the entity to make aware.
	@type entity_timezone: str
	@return: The passed in timestamp converted to the respective timezone of the entity.
	@rtype: datetime
	"""
    try:
        return time_stamp.astimezone(timezone(entity_timezone))
    except Exception as e:
        lgr.exception('entity_timezone_aware Exception: %s', e)
    return time_stamp

def create_notification_detail(message_code, message_type, message, destination):
    right_now = entity_timezone_aware(tz.now())
    t = right_now.strftime("%Y-%m-%d %H:%M:%S")
    notification_detail = [{
        "destination": destination, "message_type": message_type,
        "lang": "en", "message_code": message_code,
        "replace_tags": {"message": message, 'date': 'Generated', 'time': t}
    }]
    return notification_detail