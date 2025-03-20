from rest_framework import serializers

from otp.models import User


class AnonymousMobileVerificationSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(max_length=11, min_length=11, required=True)

    class Meta:
        model = User
        fields = ('mobile',)

    def validate_mobile(self, value):
        if not value.isdigit():
            raise serializers.ValidationError({"mobile": 'Mobile number can only be numerical'})
        if value[:2] != '09':
            raise serializers.ValidationError({"mobile": 'mobile no must start with "09"'})
        return value
