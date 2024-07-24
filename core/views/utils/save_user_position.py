from core.models.user import User
from django.contrib.gis.geos import Point


def save_user_position(user: User, last_position: Point):
    user.last_position = last_position
    user.save()
