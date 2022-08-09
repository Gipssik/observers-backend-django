from django.contrib import admin

from forum.models import Notification, Tag, Question, Comment

admin.site.register(Notification)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Comment)
