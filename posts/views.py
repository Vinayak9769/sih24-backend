from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Like, Post, Comment
from .serializers import PostSerializer, CommentSerializer, CreatePostSerializer
from rest_framework import status


# Create your views here.
@api_view(['GET'])
def post_list():
    posts = Post.objects.all().order_by('-created_at')
    serializer = PostSerializer(posts, many=True)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        return Response({'message': 'You have already liked this post.'}, status=400)
    return Response({'message': 'Post liked successfully.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_post(request, post_id):
    post = Post.objects.get(id=post_id)
    content = request.data.get('content')
    comment = Comment.objects.create(post=post, user=request.user, content=content)
    return Response({'message': 'Comment added successfully.', 'comment': CommentSerializer(comment).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    serializer = CreatePostSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

