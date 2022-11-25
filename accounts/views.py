from django.shortcuts import render
import jwt
import random
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from accounts.models import User
from accounts.serializers import UserSerializers
from rest_framework import exceptions
from datetime import date
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST
)
from accounts.backends import generate_access_token, generate_refresh_token
from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Create your views here.

class RegisterAPIView(APIView):

    def post(self, request):
        """
        This api is used to register normal user.
        params:{
            "name":<name>,
            "email":<email>,
            "password":<password>,
        }
        """
        try:
            name = request.data['name']
            email = request.data['email']
            password = request.data['password']
            user_type = request.data['user_type']
            phone = request.data['phone']
            address = request.data['address']
        except Exception:
            return Response({"message": "Send all required fields."}, status=HTTP_400_BAD_REQUEST)

        test_user = User.objects.filter(email=email).exists()
        if test_user:
            return Response({"message": "User already exists."}, status=HTTP_400_BAD_REQUEST)

        serializer = UserSerializers(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            user = User.objects.create_user(
                name=name,
                email=email,
                user_type=user_type,
                password=password,
                phone = phone,
                address = address
            )
            user.save()

            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)

            response = {
                "data":
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                "message": "Account created successfully."
            }
            return Response(response, status=HTTP_200_OK)

        else:
            return Response({"message": "Invalid data"})


class LoginAPIView(APIView):

    def post(self, request):
        password = request.data.get('password', 'None')
        email = request.data.get('email', "None")
        user_type = request.data.get("user_type", "None")

        if email == "None" or password == "None" or user_type == "None":
            raise serializers.ValidationError(
                {"message": "Enter Email and password"}
            )
        else:
            user = authenticate(request, email=email, password=password)
            print(user.user_type)
            print(user_type)
            if user is None:
                raise serializers.ValidationError(
                    {"message": "A user with this email and password was not found."}
                )
            elif str(user.user_type) != str(user_type):
                raise serializers.ValidationError(
                    {"message": "You dont have permission."}
                )

            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)

            response = {
                "data":
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                "message": "loggedIn successfully."
            }
            return Response(response, status=HTTP_200_OK)

        return Response({"message": "failed! invalid data."}, status=HTTP_401_UNAUTHORIZED)
