from datetime import timezone, timedelta
from random import randrange
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from otp.models import User
from otp.serializer import AnonymousMobileVerificationSerializer
from otp.tasks import send_verification_sms


# ---------------------------------------------------------------------------------------------------------------------
# SEND CODE Mobile      SMS
# ---------------------------------------------------------------------------------------------------------------------
class VerifyMobileNumber(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AnonymousMobileVerificationSerializer # send to AnonymousMobile

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user = User.objects.filter(mobile=mobile).first()

            if not user:
                return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

            user.verify_mobile_generic_code = str(randrange(100000, 999999))
            user.verify_mobile_generic_code_expire_at = timezone.now() + timedelta(
                seconds=settings.MOBILE_VERIFICATION_EXPIRE + 10)
            user.save()

            send_verification_sms({
                'mobile': mobile,
                'code': user.verify_mobile_generic_code
            })
            return Response({
                #  ToDo:  WARNING: remove this line
                'code': user.verify_mobile_generic_code,
                'timeout': settings.MOBILE_VERIFICATION_EXPIRE
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

