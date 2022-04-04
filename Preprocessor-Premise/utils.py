from datetime import datetime
from datetime import timezone


# convert datetime object to timestamp in UTC
# DateTime -> Timestamp
def datetime_timestamp_utc(dt_object):
    timestamp = int(dt_object.replace(tzinfo=timezone.utc).timestamp())
    return timestamp


# convert timestamp to datetime in UTC
# Timestamp -> DateTime
def timestamp_to_datetime_utc(timestamp):
    dt_object = datetime.utcfromtimestamp(timestamp)
    return dt_object