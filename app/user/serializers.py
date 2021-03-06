# import django user model and auth 
from django.contrib.auth import get_user_model, authenticate
# from django.test.testcases import SerializeMixin
# import translation in case we work with different languages
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        # remove the password and return it. 
        # if the user did not provided a password - keep it none
        password = validated_data.pop('password', None)
        # call the function again with the data remain 
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
        

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')   
        password = attrs.get('password')

        # authenticate the user and access the context of the request
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        # if auth failed - add the _ for extra languages translation 
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        # set our user in attributes and return the values  
        attrs['user'] = user
        return attrs