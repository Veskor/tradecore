from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from accounts.models import User
from accounts.serializers import UserRegistrationSerializer, UserSerializer,\
                                 CreateSerializer, PasswordSerializer

# create every type of user
# login with jwt (obtain jwt)

from rest_framework import serializers

class UserMeView(viewsets.ViewSet):
    serializer_class = UserRegistrationSerializer

    def get(self, request):
        user = self.serializer_class(request.user)
        return Response({'user':user.data,'key':request.user.activation_key})

class UserCreationView(viewsets.ViewSet):
    serializer_class = UserRegistrationSerializer
    queryset = serializer_class.Meta.model.objects.all()

    def list(self, request):
        return Response('Post to register an account')

    def create(self,request):

        data = self.serializer_class(data=request.data)

        if not data.is_valid():
            res = Response(data.errors)
            res.status_code = 400
            return res

        data.save()

        user_created = data.data

        return Response({'user':user_created})

class ConfrmUser(viewsets.ViewSet):
    serializer_class = PasswordSerializer

    @detail_route(methods=['post'])
    def SetPassword(self, request, slug):

        user = User.objects.filter(activation_key=slug)

        data = {'password1':request.data['password1'],
                'password2':request.data['password2']}

        data = self.serializer_class(data=data)
        data.is_valid()

        data.save(obj=user[0])

        return Response("Password Updated")
