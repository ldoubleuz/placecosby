from django.core.management.base import BaseCommand, CommandError
from mainapp.models import GenImage


import datetime

ZERO = datetime.timedelta(0)

# A UTC timezone class.
class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


DELTA = datetime.timedelta(hours=3)
class Command(BaseCommand):
    help = "Cleans up any generated image models older than a fixed delta"

    def handle(self, *args, **options):
        currTime = datetime.datetime.utcnow()
        currTime = currTime.replace(tzinfo=UTC())

        cutoffTime = currTime - DELTA

        self.stdout.write(
            "clearing images generated before %s..." % cutoffTime.isoformat(), 
            ending=""
        )

        # clear all old images
        GenImage.objects.filter(createdTimestamp__lte=cutoffTime).delete()

        self.stdout.write("clearing done!")

        