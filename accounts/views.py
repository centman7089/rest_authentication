from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import UserRegisterSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework import status
from .utils import send_code_to_user
from .models import OneTimePassword
from rest_framework.permissions import IsAuthenticated


# Create your views here.

class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer
    
    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        
        if serializer.is_valid(raise_exception=True):
            # serializer.save() returns the User instance
            user = serializer.save()
            
            # Send email using the instance's email
            send_code_to_user(user.email)
            
            return Response({
                'data': serializer.data,  # The serialized representation
                'message': f'Hi {user.first_name}, thanks for signing up! A passcode has been sent to your email.'
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
        

class VerifyUserEmail(GenericAPIView):
    def post(self,request):
        otp_code  = request.data.get("otp")
        try:
            user_code_obj = OneTimePassword.objects.get(code=otp_code)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message': 'account email verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({
                'message': 'code is invali, user already verified'
            }, status=status.HTTP_204_NO_CONTENT)
            
        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'passcode not provided or expired '
            }, status=status.HTTP_404_NOT_FOUND)
            

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# lets test this token create a simple protected endpoint that require a user to login to access
class TestAuthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        data = {
            'message': 'its works'
        }
        return Response(data, status=status.HTTP_200_OK)