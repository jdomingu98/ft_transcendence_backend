from rest_framework import serializers
from django.db import models
from .file_field import FtFileField


class FtModelSerializer(serializers.ModelSerializer):
    # Modify serializer_field_mapping to change the default file field to FileField
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        **{models.FileField: FtFileField}
    }
