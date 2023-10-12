import os

import boto3
from celery import shared_task
from django.core.files.uploadedfile import SimpleUploadedFile
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from .models import Videos, UsersActiveVideo
from study.settings import AWS_S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_ENDPOINT_URL


@shared_task
def save_short_video(video_id, start_time, end_time):
    video_object = Videos.objects.get(id=video_id)
    if not video_object.short_video: #if video_object.short_video is None:
        video = f"{video_object.video}"
        video_name = video.rstrip('.mp4') + '_short.mp4'
        s3 = boto3.client('s3', endpoint_url=AWS_S3_ENDPOINT_URL, aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        video_data = s3.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=video)['Body'].read()
        video_file = SimpleUploadedFile(video, video_data)
        print(f'---------->>>{os.path}')
        #print(f'---------->>>{video_object.video.path}')
        with open(video, 'wb') as f:
            f.write(video_file.read())
        ffmpeg_extract_subclip(video, start_time, end_time, targetname=video_name)
        s3.upload_file(video_name, AWS_S3_BUCKET_NAME, video_name, ExtraArgs={'ContentType': 'video/mp4'})

        video_object.short_video = video_name
        video_object.save()
        os.remove(video_name)
        os.remove(video)


@shared_task
def active_video(video_id):
    video_object = Videos.objects.get(id=video_id)
    if video_object.number == 1:
        UsersActiveVideo.objects.create(video=video_object, active=True)
