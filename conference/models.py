from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.conf import settings

from datetime import datetime

# def content_file_name(instance, filename):
#     return 'papers/user_id_{0}/{1}'.format(instance.author.id, filename)

def content_file_name(instance, filename):
    return 'papers/{0}'.format(filename)

class Event(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    acronym = models.CharField(max_length=50, unique=True)
    # description = models.TextField(max_length=500)
    create_date = models.DateTimeField(auto_now_add=True)

    chairs = models.ManyToManyField(User, through='Chair', related_name='chairs')
    pc_members = models.ManyToManyField(User, through='PC_Member', related_name='pc_members')

    OPEN, CLOSED = range(2)
    EVENT_CHOICES = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
    )
    event_status = models.IntegerField(choices=EVENT_CHOICES, default=OPEN)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)[0:99]
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("event_detail", kwargs={"pk": str(self.id), "slug": self.slug})

    @property
    def is_open(self):
        return self.event_status == 0

    def close(self):
        self.event_status = 1
        self.save()

    def reopen(self):
        self.event_status = 0
        self.save()

class Paper(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    abstract = models.TextField(max_length=500)
    event = models.ForeignKey(Event)
    submited_by = models.ForeignKey(User, related_name="submited_by")
    decided_by = models.ForeignKey(User, null=True, blank=True, related_name="decided_by")
    decided_at = models.DateTimeField(null=True, editable=False)
    locked = models.BooleanField(default=False)

    authors = models.ManyToManyField(User, through='Author', related_name='authors')
    reviewers = models.ManyToManyField(User, through='Reviewer', related_name='reviewers')

    paper_file = models.FileField(upload_to=content_file_name, blank=False)

    submit_date = models.DateTimeField(auto_now_add=True, editable=False)

    UNDER_REVIEW, AWAITING_DECISION, ACCEPTED, REJECTED = range(4)
    STATUS_CHOICES = (
        (UNDER_REVIEW, 'Under Review'),
        (AWAITING_DECISION, 'Awaiting Decision'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNDER_REVIEW)

    def __str__(self):
        return "%s submitted for: %s" %(self.title, self.event)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Paper, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("paper_detail", kwargs={"pk": str(self.id), "slug": self.slug})

    def set_under_review(self):
        self.status = 0
        self.decided_at = None
        self.locked = False

    def wait_for_decision(self):
        self.status = 1
        self.decided_at = None
        self.locked = False

    def set_accepted(self):
        self.status = 2
        self.decided_at = datetime.now()
        self.locked = True

    def set_rejected(self):
        self.status = 3
        self.decided_at = datetime.now()
        self.locked = True

    def get_reviewers(self):
        return self.reviewers.all()

class Review(models.Model):
    paper = models.ForeignKey(Paper)
    event = models.ForeignKey(Event)

    NOTSURE, ACCEPT, REJECT = range(3)
    DECISION_CHOICES = (
        (NOTSURE, 'Not Sure'),
        (ACCEPT, 'Accept'),
        (REJECT, 'Reject'),
    )
    NONE, STAR1, STAR2, STAR3, STAR4, STAR5 = range(6)
    RATE_CHOICES = (
        (NONE, 'None'),
        (STAR1, 'Awful'),
        (STAR2, 'Bad'),
        (STAR3, 'Medium'),
        (STAR4, 'Good'),
        (STAR5, 'Awesome'),
    )

    decision = models.IntegerField(choices=DECISION_CHOICES, default=NOTSURE)
    rate = models.IntegerField(choices=RATE_CHOICES, default=STAR3)

    comment = models.CharField(max_length=500)
    reviewer = models.ForeignKey(User)
    review_date = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "%s's review on %s" % (self.reviewer, self.paper)


class Author(models.Model):
    user = models.ForeignKey(User)
    paper = models.ForeignKey(Paper)

class Reviewer(models.Model):
    user = models.ForeignKey(User)
    paper = models.ForeignKey(Paper)

class Chair(models.Model):
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)

class PC_Member(models.Model):
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    class Meta:
        verbose_name = 'PC Member'
        verbose_name_plural = 'PC Members'

class Profile(models.Model):
    user = models.OneToOneField(User, unique=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)

    NONE, FEMALE, MALE = range(3)
    SEX_CHOICES = (
        (NONE,'None'),
        (FEMALE,'Female'),
        (MALE,'Male'),
    )

    # AUTHOR, REVIEWER, CHAIR, HEAD = range(4)
    # TYPE_CHOICES = (
    #     (AUTHOR, 'Author'),
    #     (REVIEWER, 'Reviewer'),
    #     (CHAIR, 'Chair'),
    #     (HEAD, 'Head'),
    # )
    sex = models.IntegerField(choices=SEX_CHOICES, default=NONE)
    # user_type = models.IntegerField(choices=TYPE_CHOICES, default=AUTHOR)

    def __unicode__(self):
        return "%s's Profile" % self.user

def create_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Profile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User)
