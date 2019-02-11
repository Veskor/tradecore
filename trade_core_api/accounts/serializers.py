from django.conf import settings

from rest_framework import serializers

from pyhunter import PyHunter
import clearbit

from accounts.models import User

from accounts.models import User, USER_TYPES, SALES, \
                            ADMIN, MANAGER, SUPER_ADMIN

clearbit.key = settings.CLEARBIT_KEY
hunter = PyHunter(settings.HUNTER)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',)


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('id','username', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        """
        Create the object.

        :param validated_data: string
        """

        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError('Email already in use, please use a different email address.')

        response = hunter.email_verifier(validated_data['email'])

        if not response['smtp_server'] or not response['smtp_check']:
            raise serializers.ValidationError('Email is not verified by hunter.io, please use a different email address.')

        enrichment = clearbit.Enrichment.find(email=validated_data['email'], stream=True)

        validated_data['enrichment'] = enrichment
        validated_data['user_type'] = 'admin'

        user = User.objects.create(**validated_data)

        user.set_password(validated_data['password'])

        return user

class CreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES)
    user_type = serializers.ChoiceField(choices=USER_TYPES)

    class Meta:
        model = User
        fields = ('email','first_name','last_name','username','gender','user_type')

    def create(self, data):
        if(data['user_type'] == SALES):
            user = User.objects.create_user(email=data['email'],
                                            first_name=data['first_name'],
                                            last_name=data['last_name'],
                                            username=data['username'],
                                            gender=data['gender'],
                                            password='')
            saved = user.save()

        elif(data['user_type'] == ADMIN):
            user = User.objects.create_admin(email=data['email'],
                                            first_name=data['first_name'],
                                            last_name=data['last_name'],
                                            username=data['username'],
                                            gender=data['gender'],
                                            password='')

            saved = user.save()

        elif(data['user_type'] == MANAGER):
            user = User.objects.create_manager(email=data['email'],
                                            first_name=data['first_name'],
                                            last_name=data['last_name'],
                                            username=data['username'],
                                            gender=data['gender'],
                                            password='')

            saved = user.save()

        elif(data['user_type'] == SUPER_ADMIN):

            user = User.objects.create_superuser(email=data['email'],
                                            first_name=data['first_name'],
                                            last_name=data['last_name'],
                                            username=data['username'],
                                            gender=data['gender'],
                                            password='')
            saved = user.save()

        # send email with activation_key
        return data

class PasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('password1','password2')

    def validate(self,data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        else:
            return data

    def save(self,obj):
        obj.set_password(self.validated_data['password1'])
        obj.save()
