from rest_framework import serializers
from .models import Navigation,FullTour,DisplayVideo
from education.bunnycdn_utils import BunnyCDNUploader
from django.conf import settings

# Initialize BunnyCDN uploader
bunny_cdn = BunnyCDNUploader(
    api_key=settings.BUNNY_API_KEY,
    storage_zone=settings.BUNNY_CDN_STORAGE_ZONE,
    base_url=settings.BUNNY_CDN_URL,
)

class NavigationSerializer(serializers.ModelSerializer):
    # Accept file uploads for image & video
    image = serializers.FileField(write_only=True, required=False)
    video = serializers.FileField(write_only=True, required=False)

    # Return URLs as "image" and "video" in the response
    image = serializers.SerializerMethodField(read_only=True)
    video = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Navigation
        fields = [
            "id", "name", "description", "name1", "robot", "navigation_id",
            "image", "video"
        ]

    def get_image(self, obj):
        return obj.image if obj.image else None

    def get_video(self, obj):
        return obj.video if obj.video else None

    def create(self, validated_data):
        image_file = self.context["request"].FILES.get("image")
        video_file = self.context["request"].FILES.get("video")

        navigation = Navigation.objects.create(**validated_data)

        if image_file:
            uploaded_image_url = bunny_cdn.upload_file(image_file)
            if uploaded_image_url:
                navigation.image = uploaded_image_url

        if video_file:
            uploaded_video_url = bunny_cdn.upload_file(video_file)
            if uploaded_video_url:
                navigation.video = uploaded_video_url

        navigation.save()
        return navigation

    def update(self, instance, validated_data):
        image_file = self.context["request"].FILES.get("image")
        video_file = self.context["request"].FILES.get("video")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image_file:
            uploaded_image_url = bunny_cdn.upload_file(image_file)
            if uploaded_image_url:
                instance.image = uploaded_image_url

        if video_file:
            uploaded_video_url = bunny_cdn.upload_file(video_file)
            if uploaded_video_url:
                instance.video = uploaded_video_url

        instance.save()
        return instance




class FullTourSerializer(serializers.ModelSerializer):
    navigations = serializers.SerializerMethodField()

    class Meta:
        model = FullTour
        fields = ['id', 'robot', 'navigations']

    def get_navigations(self, obj):
        navigations = {nav.id: nav for nav in Navigation.objects.filter(id__in=obj.navigations)}
        ordered_navigations = [navigations[nav_id] for nav_id in obj.navigations if nav_id in navigations]
        return NavigationSerializer(ordered_navigations, many=True).data
    



class DisplayVideoSerializer(serializers.ModelSerializer):
    # Accept file upload
    video = serializers.FileField(write_only=True, required=False)

    # Return URL
    video = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DisplayVideo
        fields = ["id", "robot", "video"]

    def get_video(self, obj):
        return obj.video if obj.video else None

    def create(self, validated_data):
        video_file = self.context["request"].FILES.get("video")

        display_video = DisplayVideo.objects.create(**validated_data)

        if video_file:
            uploaded_video_url = bunny_cdn.upload_file(video_file)
            if uploaded_video_url:
                display_video.video = uploaded_video_url

        display_video.save()
        return display_video

    def update(self, instance, validated_data):
        video_file = self.context["request"].FILES.get("video")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if video_file:
            uploaded_video_url = bunny_cdn.upload_file(video_file)
            if uploaded_video_url:
                instance.video = uploaded_video_url

        instance.save()
        return instance
    

