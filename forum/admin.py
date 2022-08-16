from django.contrib import admin

from forum.models import Comment, Question, Tag

admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Comment)
