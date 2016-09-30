from django.conf.urls import include, url
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.decorators import login_required as auth
from django.contrib.auth.views import login, logout_then_login
from conference.views import ProfileDetailView, UserProfileEditView, HomeListView
from conference.views import EventCreateView, EventDetailView, EventUpdateView, EventsView
from conference.views import CloseEventView, ReopenEventView, DownloadEventZippedView
from conference.views import PaperCreateView, PaperDetailView, PaperReview
from conference.views import AddReviewerView, RemoveReviewerView
from conference.views import AddChair, RemoveChair, AddPCMember, RemovePCMember
from conference.views import RemoveGeneralReview, custom_login
from conference.views import SetPaperStatus, ImportUsersView, ImportEventsView

from django.contrib.flatpages import views

from annotation.views import DemoView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/$', auth(HomeListView.as_view()), name='home'),
    url(r'^$', custom_login, name="login"),

    url(r"^", include("annotation.urls")),
    url(r'^demo/', DemoView.as_view(), name="demo"),

    url(r'^accounts/', include('registration.backends.simple.urls')),
    # url(r'^login/', login, {"template_name": "login.html"}, name="login"),
    url(r'^logout/', logout_then_login, name="logout"),
    url(r'^profile/(?P<slug>[-\w.\d\_]+)/$', ProfileDetailView.as_view(), name="profile"),
    url(r'^profile/(?P<slug>[-\w.\d\_]+)/edit/$', auth(UserProfileEditView.as_view()), name="edit_profile"),

    url(r'^event/create/$', auth(EventCreateView.as_view()), name='event_create'),
    url(r'^event/(?P<pk>\d+)/(?P<slug>[-\w\d\_]+)/$', EventDetailView.as_view(), name='event_detail'),
    url(r'^event/update/(?P<pk>\d+)/$', auth(EventUpdateView.as_view()), name='event_update'),
    url(r'^event/close/(?P<pk>\d+)/$', CloseEventView, name='event_close'),
    url(r'^event/reopen/(?P<pk>\d+)/$', ReopenEventView, name='event_reopen'),
    url(r'^event/download/(?P<pk>\d+)/$', DownloadEventZippedView, name='event_download'),
    url(r'^events/$', auth(EventsView), name='events'),

    url(r'^paper/submit/$', auth(PaperCreateView.as_view()), name='paper_create'),
    url(r'^paper/(?P<pk>\d+)/(?P<slug>[-\w\d\_]+)/$', PaperDetailView.as_view(), name='paper_detail'),
    url(r'^review/paper/(?P<pk>\d+)/$', PaperReview, name='paper_review'),

    url(r'^event/addchair/(?P<pk>\d+)/(?P<user_id>\d+)/$', AddChair, name='add_chair'),
    url(r'^event/removechair/(?P<pk>\d+)/(?P<user_id>\d+)/$', RemoveChair, name='remove_chair'),

    url(r'^event/addpcmember/(?P<pk>\d+)/(?P<user_id>\d+)/$', AddPCMember, name='add_pc_member'),
    url(r'^event/removepcmember/(?P<pk>\d+)/(?P<user_id>\d+)/$', RemovePCMember, name='remove_pc_member'),

    url(r'^paper/addreviewer/(?P<pk>\d+)/(?P<user_id>\d+)/$', AddReviewerView, name='add_reviewer'),
    url(r'^paper/removereviewer/(?P<pk>\d+)/(?P<user_id>\d+)/$', RemoveReviewerView, name='remove_reviewer'),

    url(r'^general-review/remove/(?P<pk>\d+)/(?P<paper_id>\d+)/$', RemoveGeneralReview, name='remove_general_review'),
    url(r'^set-status/paper/(?P<pk>\d+)/(?P<status>\d+)/$', SetPaperStatus, name='set_paper_status'),

    url(r'^import-users/$', ImportUsersView, name='import_users'),
    url(r'^import-events/$', ImportEventsView, name='import_events'),

    url(r'^about-us/$', views.flatpage, {'url': '/about-us/'}, name='about'),
    url(r'^help/$', views.flatpage, {'url': '/help/'}, name='help'),

    # url(r'^paper/update/(?P<pk>\d+)/$', auth(EventUpdateView.as_view()), name='event_update'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
