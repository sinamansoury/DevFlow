from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "وارد کردن رمز عبور الزامی است.",
        }
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=' این ایمیل قبلاً ثبت شده است.',
            )
        ],
        error_messages={

            "blank": "وارد کردن ایمیل الزامی است.",
            "invalid": "فرمت ایمیل صحیح نیست.",
        }
    )

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'phone'
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
        ]
