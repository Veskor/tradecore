# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route

from .serializers import PostSerializer, CreatePostSerializer, DefaultSerializer
from .models import Post
from .pagination import LargeResultsSetPagination

from uuid import UUID
import json

# Create your views here.

class PostViewSet(viewsets.ModelViewSet):

    serializer_class = PostSerializer
    queryset = serializer_class.Meta.model.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = LargeResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'like' or self.action == 'unlike':
            return DefaultSerializer
        elif self.request == 'GET':
            return PostSerializer
        return CreatePostSerializer

    def list(self, request):
        posts = Post.objects.all().exclude(owner=self.request.user)
        posts = PostSerializer(posts,many=True)
        return Response(posts.data)

    def retrieve(self, request, pk=None):
        try:
            post = Post.objects.get(id=pk)
        except:
            res = Response('404 not found')
            res.status_code = 404
            return res

        post = PostSerializer(post)
        return Response(post.data)

    def create(self, request):

        post = CreatePostSerializer(data=request.POST, context={'user': request.user})

        if post.is_valid():
            post.save()
            return Response(post.data)
        else:
            return Response(post.errors)


    @detail_route(methods=['put',])
    def like(self, request, pk=None):
        try:
            post = Post.objects.get(id=pk)
            likes = json.loads(post.likes)
        except:
            post = None


        if not post:
            res = Response('404 not found')
            res.status_code = 404
            return res

        user_id = str(self.request.user.id)

        if user_id not in likes['keys']:

            likes['count'] += 1

            likes['keys'].append(user_id)

            likes = json.dumps(likes)

            post.likes = likes

            post.save()

            return Response('Post liked')
        else:
            return Response('You allready like this post')

    @detail_route(methods=['put',])
    def unlike(self, request, pk=None):
        try:
            post = Post.objects.get(id=pk)
            likes = json.loads(post.likes)
        except:
            post = None

        if not post:
            res = Response('404 not found')
            res.status_code = 404
            return res

        user_id = str(self.request.user.id)

        if user_id in likes['keys']:

            likes['count'] -= 1

            likes['keys'].remove(user_id)

            likes = json.dumps(likes)

            post.likes = likes

            post.save()

            return Response('Post unliked')
        else:
            return Response('You can\'t unlike this post')
