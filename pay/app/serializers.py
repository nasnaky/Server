from django.contrib.auth import get_user_model
from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from app.models import PRODUCT

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'phone', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            phone=validated_data['phone'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()
    user = serializers.IntegerField()

    class Meta:
        model = PRODUCT
        fields = ['tags', 'money', 'cost', 'name', 'content', 'barcode', 'max_data', 'size', 'user']
        read_only_fields = ['user']
        depth = 1


class ProductListSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = PRODUCT
        fields = ['id', 'tags', 'money', 'name', 'max_data', 'size']
        depth = 1
