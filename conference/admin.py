from django.contrib import admin
from conference.models import Event, Paper, Profile, Review, Reviewer, Author, PC_Member, Chair

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'event_status', 'create_date')

class PaperAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'event', 'submited_by', 'status', 'submit_date')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'paper', 'event', 'reviewer', 'rate', 'comment', 'review_date')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class ProfileAdmin(UserAdmin):
    inlines = (ProfileInline, )

class ReviewerAdmin(admin.ModelAdmin):
	list_display = ('user', 'paper')

class AuthorAdmin(admin.ModelAdmin):
	list_display = ('user', 'paper')

class ChairAdmin(admin.ModelAdmin):
	list_display = ('user', 'event')

class PC_MemberAdmin(admin.ModelAdmin):
	list_display = ('user', 'event')

admin.site.register(Event, EventAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), ProfileAdmin)
admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Chair, ChairAdmin)
admin.site.register(PC_Member, PC_MemberAdmin)
