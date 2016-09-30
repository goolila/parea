from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from conference.models import Event, Paper, Profile, Reviewer, Chair, Review, PC_Member
from conference.forms import EventForm, PaperForm, UserProfileForm, ReviewForm
from annotation.models import Annotation
from wsgiref.util import FileWrapper
from utils import import_users_from_json, import_events_from_json, close_event_jsonify

from lxml import etree as et

import os

class StaticMixin(object):
       def get_context_data(self, **kwargs):
           context = super(StaticMixin, self).get_context_data(**kwargs)
           context['papers'] = Paper.objects.all()[:20]
           context['users'] = Profile.objects.all()
           return context

class HomeListView(StaticMixin, ListView):
    model = Event
    queryset = Event.objects.filter(event_status__exact=0)
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        context['closed_events'] = Event.objects.filter(event_status__exact=1)
        return context

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "conference/event_form.html"

    def form_valid(self, form):
        f = form.save(commit=False)
        f.save()
        return super(EventCreateView, self).form_valid(form)

class EventDetailView(DetailView):
    model = Event
    success_url = reverse_lazy('event_detail')

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        # which users should be available to be chosen as Chair?
        context['users'] = Profile.objects.all().order_by('id')
        event = Event.objects.get(pk=self.object.pk)
        context['chairs'] = event.chairs.all()
        context['pc_members'] = event.pc_members.all()
        context['papers'] = Paper.objects.filter(event=self.object)
        for paper in context['papers']:
            numberof_paper_reviewers = paper.get_reviewers().count()
            number_review_for_paper = Review.objects.filter(paper__exact=paper).count()
            if numberof_paper_reviewers > 0 :
                if number_review_for_paper == numberof_paper_reviewers and not paper.status == 2 and not paper.status == 3:
                    paper.wait_for_decision()
                    paper.save()
                    # print number_review_for_paper, numberof_paper_reviewers
                    # print("%s is ready for decision making process" %paper)
                else:
                    pass
                    # print("%s is NOT ready for decision making process" %paper)
        for paper in context['papers']:
            if paper.locked:
                context['ready_to_be_closed'] = True
            else:
                context['ready_to_be_closed'] = False
                break
        context['general_reviews'] = Review.objects.filter(event__exact=event)
        return context

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm

class PaperCreateView(CreateView):
    model = Paper
    form_class = PaperForm
    template_name = "conference/paper_form.html"

    def form_valid(self, form):
        f = form.save(commit=False)
        f.slug = slugify(f.title)
        f.submited_by = self.request.user
        f.save()
        return super(PaperCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PaperCreateView, self).get_context_data(**kwargs)
        context['events'] = Event.objects.filter(event_status__exact=0)
        return context

class PaperDetailView(FormMixin, DetailView):
    model = Paper
    success_url = reverse_lazy('event_detail')

    form_class = ReviewForm

    def get_success_url(self):
        return reverse('paper_detail', kwargs={'pk': self.object.pk, 'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(PaperDetailView, self).get_context_data(**kwargs)
        paper = Paper.objects.get(pk=self.object.pk)
        event = paper.event

        context['reviewers'] = paper.reviewers.all()
        context['chairs'] = event.chairs.all()
        context['pcmembers'] = event.pc_members.all()
        context['general_reviews'] = Review.objects.filter(paper__exact=paper)
        did_general_review = False
        try:
            if self.request.user.is_authenticated():
                general_review = Review.objects.get(paper=paper, reviewer=self.request.user)
                did_general_review = True
        except ObjectDoesNotExist:
            did_general_review = False
        context['did_general_review'] = did_general_review

        # change in production!
        uri = "http://127.0.0.1:8000/review/paper/%s/" %self.object.pk
        context['annotations'] = Annotation.objects.filter(uri=uri)
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        paper = get_object_or_404(Paper, pk=self.object.pk)
        f = form.save(commit=False)
        f.reviewer = self.request.user
        f.paper = paper
        f.event = paper.event
        f.save()
        return super(PaperDetailView, self).form_valid(form)

def RemoveGeneralReview(request, pk, paper_id):
    review = get_object_or_404(Review, pk=pk)
    paper = get_object_or_404(Paper, pk=paper_id)
    next = get_next(request, paper)
    review.delete()
    return HttpResponseRedirect(next)

def SetPaperStatus(request, pk, status):
    paper = get_object_or_404(Paper, pk=pk)
    event = paper.event
    user = request.user

    if user in event.chairs.all():
        is_chair = True
    else:
        raise PermissionDenied

    next_redirect = get_next(request, event)

    if is_chair:
        if status == "2":
            paper.set_accepted()
            paper.decided_by = request.user
        elif status == "3":
            paper.set_rejected()
            paper.decided_by = request.user
        elif status == "0":
            paper.set_under_review()
            paper.decided_by = None
        paper.save()
    return HttpResponseRedirect(next_redirect)

def PaperReview(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    # paper_file = open(paper.paper_file.path)
    # parsed = paper_file.read()
    # html = bs4.BeautifulSoup(parsed, "html.parser")
    # body = html.find('body')
    # paper_file.close()

    htmlparser = et.HTMLParser()
    tree = et.parse(paper.paper_file.path, htmlparser)
    body = tree.xpath("body")
    parsed = et.tostring(body[0], method="html", pretty_print=True)

    chairs = paper.event.chairs.all()
    reviewers = paper.reviewers.all()
    context = {'body':body, 'paper':paper, 'parsed':parsed, 'chairs': chairs, 'reviewers':reviewers}

    return render(request, 'conference/paper_review.html', context)

class ProfileDetailView(DetailView):
    model = get_user_model()
    slug_field = "username"
    template_name = "user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        context['papers'] = Paper.objects.filter(authors__exact=self.object)
        context['chair_of'] = Chair.objects.filter(user=self.object)
        context['reviewer_of'] = Reviewer.objects.filter(user=self.object)
        return context

class UserProfileEditView(UpdateView):
    model 		= Profile
    form_class 	= UserProfileForm
    template_name = "profile/profile_edit.html"

    def get_object(self, queryset=None):
        return Profile.objects.get_or_create(user=self.request.user)[0]

    def get_success_url(self):
        return reverse("profile", kwargs={'slug': self.request.user})

def AddRevView(request, pk, user_id):
    paper = get_object_or_404(Paper, pk=pk)
    user = get_object_or_404(Profile, pk=user_id).user
    next = get_next(request, paper)

    if user in paper.reviewers.all():
        is_reviewer = True
    else:
        raise PermissionDenied

    if not is_reviewer:
        m = Reviewer(user=user, paper=paper)
        m.save()
    else:
        print "is already a reviewer of this paper!"
    return HttpResponseRedirect(next)

def RemoveRevView(request, pk, user_id):
    paper = get_object_or_404(Paper, pk=pk)
    user = get_object_or_404(Profile, pk=user_id).user
    next = get_next(request, paper)

    if user in paper.reviewers.all():
        is_reviewer = True
    else:
        raise PermissionDenied

    if is_reviewer:
        m = Reviewer.objects.get(user=user, paper=paper)
        m.delete()
    return HttpResponseRedirect(next)

def AddChair(request, pk, user_id):
    event = get_object_or_404(Event, pk=pk)
    user = get_object_or_404(Profile, pk=user_id).user
    next = get_next(request, event)

    if request.user.is_staff:
        if not user in event.chairs.all():
            m = Chair(user=user, event=event)
            m.save()
            messages.success(request, "You've added a chair to this event!")
        return HttpResponseRedirect(next)
    else:
        raise PermissionDenied


def RemoveChair(request, pk, user_id):
    event = get_object_or_404(Event, pk=pk)
    user = get_object_or_404(Profile, pk=user_id).user
    next = get_next(request, event)

    if request.user.is_staff:
        if user in event.chairs.all():
            m = Chair.objects.get(user=user, event=event)
            m.delete()
            messages.warning(request, "You've removed a chair from this event!")
        return HttpResponseRedirect(next)
    else:
        raise PermissionDenied

def AddPCMember(request, pk, user_id):
    event = get_object_or_404(Event, pk=pk)
    user = get_object_or_404(Profile, pk=user_id).user
    next = get_next(request, event)

    if request.user.is_staff:
        if not user in event.pc_members.all():
            m = PC_Member(user=user, event=event)
            m.save()
            messages.success(request, "You've added a PC Member to this event!")
        return HttpResponseRedirect(next)
    else:
        raise PermissionDenied

def RemovePCMember(request, pk, user_id):
    event = get_object_or_404(Event, pk=pk)
    user = get_object_or_404(Profile, pk=user_id).user
    next = get_next(request, event)

    if request.user.is_staff:
        if user in event.pc_members.all():
            m = PC_Member.objects.get(user=user, event=event)
            m.delete()
            messages.warning(request, "You've removed a PC Member to this event!")
        return HttpResponseRedirect(next)
    else:
        raise PermissionDenied

def CloseEventView(request, pk):
    event = get_object_or_404(Event, pk=pk)
    next = get_next(request, event)

    if request.user in event.chairs.all() or request.user.is_staff:
        event.close()
        close_event_jsonify(event.id)
        messages.warning(request, "You've just closed this event! Only a PAREA staff can reopen it now.")
        return HttpResponseRedirect(next)
    else:
        raise PermissionDenied

def ReopenEventView(request, pk):
    event = get_object_or_404(Event, pk=pk)
    next = get_next(request, event)

    if request.user.is_staff:
        event.reopen()
        messages.success(request, "You've successfully reopened this event!")

        return HttpResponseRedirect(next)
    else:
        raise PermissionDenied

def DownloadEventZippedView(request, pk):
    event = get_object_or_404(Event, pk=pk)
    next = get_next(request, event)

    if request.user in event.chairs.all() or request.user.is_staff:
        is_chair_or_head = True
    else:
        is_chair_or_head = False

    if is_chair_or_head:
        event_path = os.path.join(settings.MEDIA_ROOT, event.acronym)
        event_zip_path = os.path.join(event_path, event.acronym)
        zip_file = os.path.join(event_zip_path + ".tar")
        print event_path
        print event_zip_path
        print zip_file
        opened_zip = open(zip_file, 'rb')
        resp = HttpResponse(opened_zip, content_type="application/tar")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_file
        opened_zip.close()

        return resp
    else:
        return HttpResponseForbidden()

def ImportUsersView(request):
    import_users_from_json()
    return redirect('home')

def ImportEventsView(request):
    import_events_from_json()
    return redirect('home')

def get_next(request, item):
    if 'next' in request.GET:
        next = request.GET['next']
    elif hasattr(item, 'get_absolute_url'):
        if callable(getattr(item, 'get_absolute_url')):
            next = item.get_absolute_url()
        else:
            next = item.get_absolute_url
    else:
        raise AttributeError('Define get_absolute_url')
    return next

def EventsView(request):
    events = Event.objects.all()
    open_events = Event.objects.filter(event_status__exact=0)
    closed_events = Event.objects.filter(event_status__exact=1)
    context = {'events':events, 'open_events':open_events, 'closed_events':closed_events}
    return render(request, 'conference/events.html', context)

def custom_login(request):
    if request.user.is_authenticated():
        messages.warning(request, "You're already logged in.")
        return HttpResponseRedirect('home')
    else:
        return login(request)
