# File: accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model, returns basic user info."""
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role')


class LoginSerializer(serializers.Serializer):
    """Serializer to handle login requests."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "non_field_errors": ["Invalid email or password"]
            })

        if not user.check_password(password):
            raise serializers.ValidationError({
                "non_field_errors": ["Invalid email or password"]
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "non_field_errors": ["Your account is inactive"]
            })

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return {
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
