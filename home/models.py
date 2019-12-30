
from django.db import models
from django.http import HttpResponseRedirect

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel

from blog.models import Post, Category

"""
HOME --- MODELS
"""


class HomeIndex(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]
    """
    def get_context(self, request):
        context= super(HomeIndex, self).get_context(request)
        posts = Post.objects.descendant_of(
            self).live().order_by('-date_published')[:6]
        context = {
            'posts': posts,
        }
        return context
    """

    def serve(self, request):
        return HttpResponseRedirect('/blog/')


