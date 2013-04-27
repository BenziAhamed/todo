import alfred
import config
from uuid import uuid4
import config_keys as ck
import datetime
import re
import sys


def apply_integration(feedback_items, todo, query):
    if config.get(ck.KEY_FEATURE_EGGTIMER) == True:
        feedback_items.append(alfred.Item(
            attributes={
                'uid': uuid4(),
                'arg': "_integration:eggtimer:"+query,
                'valid': 'yes' if eggtimer_valid(query) else 'no',
                'autocomplete': eggtimer_autocomplete(query)
            },
            title="EggTimer alarm at " + ((query + " for '" + todo[
                                           'title'] + "'") if eggtimer_valid(query) else "'...'"),
            subtitle="Enter a time, or keep pressing Tab",
            icon="todo_edit.png"
        ))


# EggTimer
def eggtimer_autocomplete(query):
    m = re.match(r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})', query)
    if m:
        hour = int(m.group('hour'))
        minute = int(m.group('minute'))
    else:
        t = datetime.datetime.now()
        hour = t.hour
        minute = t.minute
    minute = "30" if minute < 30 else "00"
    if minute == "00":
        hour = (hour+1) % 24
    return str(hour)+":"+minute


def eggtimer_valid(query):
    m = re.match(r'^(?P<hour>\d{1,2}):(?P<minute>\d{1,2})$', query)
    return m is not None

if __name__ == "__main__":
    print eggtimer_autocomplete(sys.argv[1])
