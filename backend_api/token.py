from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token
        token['user_id'] = str(user.user_id)  # UUID or int
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Optionally include user info in the response
        data.update({
            'user_id': str(self.user.user_id),
            'email': self.user.email,
        })
        return data

