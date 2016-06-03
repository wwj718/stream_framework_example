# encoding: utf-8

from django.db import models
from django.conf import settings
from django.utils.timezone import make_naive
import pytz


class BaseModel(models.Model):

    class Meta:
        abstract = True


class Item(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL) # setting里没有 AUTH_USER_MODEL，不会报错？
    image = models.ImageField(upload_to='items')
    source_url = models.TextField()
    message = models.TextField(blank=True, null=True)
    pin_count = models.IntegerField(default=0)

    # class Meta:
    #    db_table = 'pinterest_example_item'


class Board(BaseModel): #公告板
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField()


class Pin(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    item = models.ForeignKey(Item)
    board = models.ForeignKey(Board)
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='influenced_pins')  # 影响者 
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def create_activity(self):
        from stream_framework.activity import Activity # 这是核心所在,消息存储在redis中
        from core.verbs import Pin as PinVerb
        activity = Activity(
            self.user_id,  # user_id是啥
            PinVerb,
            self.id,
            self.influencer_id,
            time=make_naive(self.created_at, pytz.utc),
            extra_context=dict(item_id=self.item_id)
        ) #这个东西会做什么
        return activity


class Follow(BaseModel):

    '''
    A simple table mapping who a user is following. 
    For example, if user is Kyle and Kyle is following Alex,
    the target would be Alex.
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='following_set')  # 外键是以user_id被存储
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='follower_set')
    created_at = models.DateTimeField(auto_now_add=True)


from core import verbs
