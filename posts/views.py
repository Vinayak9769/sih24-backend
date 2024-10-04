from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Like, Post, Comment
from .serializers import PostSerializer, CommentSerializer, CreatePostSerializer
from rest_framework import status


@api_view(['GET'])
def post_list(request):
    """
    Retrieves and returns a list of all posts.

    The posts are ordered by their creation date in descending order (most recent first).

    Returns:
        Response: A JSON response containing the serialized list of posts and a 200 OK status.
    """
    posts = Post.objects.all().order_by('-created_at')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    """
    Likes a post.

    If the post exists and the user hasn't already liked it, a new like is created.
    If the user has already liked the post, an error message is returned.

    Args:
        request: The HTTP request containing the user's authentication.
        post_id: The ID of the post to be liked.

    Returns:
        Response:
        - Success message with a 200 OK status if the post is liked successfully.
        - Error message with a 404 status if the post is not found.
        - Error message with a 400 status if the post has already been liked by the user.
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        return Response({'message': 'You have already liked this post.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Post liked successfully.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_post(request, post_id):
    """
    Adds a comment to a post.

    If the post exists, a new comment is created with the content provided by the user.
    If the content is empty or if the post doesn't exist, appropriate error messages are returned.

    Args:
        request: The HTTP request containing the user's authentication and comment content.
        post_id: The ID of the post to comment on.

    Returns:
        Response:
        - Success message and the serialized comment data with a 201 Created status if the comment is added successfully.
        - Error message with a 404 status if the post is not found.
        - Error message with a 400 status if the comment content is blank.
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    content = request.data.get('content')
    if not content:
        return Response({"content": ["This field may not be blank."]}, status=status.HTTP_400_BAD_REQUEST)

    comment = Comment.objects.create(post=post, user=request.user, content=content)
    return Response({'message': 'Comment added successfully.', 'comment': CommentSerializer(comment).data},
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    """
    Creates a new post.

    The post is created using the data provided in the request. If the data is valid,
    the post is saved and returned in the response. If there are validation errors,
    they are returned in the response.

    Args:
        request: The HTTP request containing the user's authentication and post data.

    Returns:
        Response:
        - Serialized post data with a 201 Created status if the post is created successfully.
        - Error message with a 400 status if the provided data is invalid.
    """
    serializer = CreatePostSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
