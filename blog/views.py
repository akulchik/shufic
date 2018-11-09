from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .forms import CommentForm
from .models import Video, Comment
from django.template.context_processors import csrf
from django.contrib import auth
import json


def show_latest_videos(request):
    latest_videos_list = Video.objects.order_by('-date')
    paginator = Paginator(latest_videos_list, 12)
    page = request.GET.get('page')
    latest_videos = paginator.get_page(page)
    context = {
        'latest_videos': latest_videos,
    }
    return render(request, 'home.html', context)


def show_video(request, video_id):
    context = {'video': get_object_or_404(Video, id=video_id),
               'comments': Comment.objects.filter(videoparent_id=video_id),
               'username': auth.get_user(request).username,
               'form': CommentForm, }
    context.update(csrf(request))
    return render(request, 'video.html', context)


def show_bio(request):
    return render(request, 'bio.html', {})


def like_video(request):
    video_id = request.GET['video_id']
    video = Video.objects.get(id=video_id)
    video.rating += 1
    video.save()
    return HttpResponse(video.rating)


def dislike_video(request):
    video_id = request.GET['video_id']
    video = Video.objects.get(id=video_id)
    video.rating -= 1
    video.save()
    return HttpResponse(video.rating)


'''def leave_comment(request, video_id):
    if request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.videoparent = Video.objects.get(id=video_id)
            form.save()
    return redirect('/video/' + str(video_id) + '/')'''


def leave_comment(request):
    if request.POST:
        videoparent = Video.objects.get(id=request.POST.get('video_id'))
        text = request.POST.get('text')
        comment = Comment(videoparent=videoparent, text=text)
        comment.save()
        response_data = {
            'text': comment.text,
            'rating': comment.rating,
        }
        return HttpResponse(json.dumps(response_data), content_type='application/json')
