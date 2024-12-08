from rest_framework import serializers


class FtFileField(serializers.FileField):
    def to_representation(self, value):
        if not value:
            return None
        return value.url
