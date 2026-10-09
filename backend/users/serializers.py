from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User

class NormalizedEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return value.strip().lower()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "وارد کردن رمز عبور الزامی است.",
        }
    )
    def validate(self, attrs):
        password = attrs.get("password")

        user = User(
            email=attrs.get("email"),
            first_name=attrs.get("first_name", ""),
            last_name=attrs.get("last_name", ""),
        )

        validate_password(password, user=user)

        return attrs

    email =NormalizedEmailField(
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

    phone = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        error_messages={
            "required": "وارد کردن شماره موبایل الزامی است.",
            "blank": "شماره موبایل نمی‌تواند خالی باشد.",
            "null": "شماره موبایل نمی‌تواند null باشد.",
        },
    )

    def validate_phone(self, value):
        if value.startswith("+98"):
            value = "0" + value[3:]

        if (
                not value.isdigit()
                or len(value) != 11
                or not value.startswith("09")
        ):
            raise serializers.ValidationError(
                "شماره موبایل باید با 09 یا +98 شروع شود و فرمت معتبری داشته باشد."
            )
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "این شماره موبایل قبلاً ثبت شده است."
            )

        return value


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
