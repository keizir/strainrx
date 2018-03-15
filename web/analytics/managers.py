from django.db import models


class EventQuerySet(models.QuerySet):

    def events(self, from_date, to_date, entity_id, event_type):
        query = self.filter(entity_id=entity_id, event=event_type)
        if from_date:
            query = query.filter(event_date__gte=from_date)

        if to_date:
            query = query.filter(event_date__lte=to_date)

        return query \
            .extra(select={'day': 'to_char( event_date,  \'YYYY-MM-DD\' )'}) \
            .values('day') \
            .annotate(count=models.Count('event_date')) \
            .order_by('-day')


class BusinessLocationMenuUpdateRequestQuerySet(models.QuerySet):

    def events(self, from_date, to_date, entity_id):
        query = self.filter(business_location__business_id=entity_id)
        if from_date:
            query = query.filter(date_time__gte=from_date)

        if to_date:
            query = query.filter(date_time__lte=to_date)

        return query \
            .extra(select={'day': 'to_char( date_time,  \'YYYY-MM-DD\' )'}) \
            .values('day') \
            .annotate(count=models.Count('date_time')) \
            .order_by('-day')
