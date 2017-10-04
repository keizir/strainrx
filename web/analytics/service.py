from web.analytics.models import Event
from web.users.models import User

class Analytics():
    @staticmethod
    def track(event=None, user=None, entity_id=None, properties={}):
        ev = Event()

        ev.event = event

        if user is not None and user.id != None:
            ev.user = user

        if entity_id is not None:
            ev.entity_id = entity_id

        if properties is not None:
            ev.properties = properties

        print("TRACKING....", ev)
        print(event)
        print(properties)

        ev.save()

