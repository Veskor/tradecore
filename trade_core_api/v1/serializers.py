from rest_framework import serializers

from .models import Post

import json

class PostSerializer(serializers.ModelSerializer):
    data = serializers.JSONField()
    likes = serializers.JSONField(required=False)

    class Meta:
        model = Post
        fields = ('id','data','likes',)

class DefaultSerializer(serializers.Serializer):
    class Meta:
        fields = ()

class CreatePostSerializer(serializers.ModelSerializer):
    data = serializers.JSONField()

    class Meta:
        model = Post
        fields = ('id','data')

    def create(self, validated_data):
        likes = {
            'count': 0,
            'keys': [],
        }

        likes = json.dumps(likes)
        validated_data['likes'] = likes
        validated_data['owner'] = self.context.get('user')

        post = Post.objects.create(**validated_data)

        return post
