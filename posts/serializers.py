from rest_framework import serializers
from .models import Post, Like, Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True) 

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    likes = LikeSerializer(many=True, read_only=True)  
    comments = CommentSerializer(many=True, read_only=True)  
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = ['id', 'mentor', 'caption', 'image', 'video', 'created_at', 'like_count', 'comment_count', 'likes', 'comments']


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['mentor', 'caption', 'image', 'video']  

    def create(self, validated_data):
        post = Post.objects.create(
            mentor=self.context['request'].user,
            **validated_data
        )
        return post
