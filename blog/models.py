from django.db import models
from django import forms
from django.contrib import messages
from django.shortcuts import redirect, render

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ClusterableModel

from taggit.models import Tag, TaggedItemBase

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.search import index

from .blocks import BaseStreamBlock
from wagtail.snippets.edit_handlers import SnippetChooserPanel
import uuid
from django.template.defaultfilters import slugify

"""
    BLOG MODELS
"""


class BlogIndex(RoutablePageMixin, Page):
    introduction = models.TextField(
        help_text='Text to describe the page',
        blank=True
    )

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode; horizontal width between 1000px and 3000px.'
    )

    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname='full'),
        ImageChooserPanel('image'),
    ]

    subpage_types = ['Post']

    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request):
        context = super(BlogIndex, self).get_context(request)
        posts = Post.objects.descendant_of(
            self).live().order_by('-date_published')
        context['posts'] = posts

        return context

    @route(r'^tags/$', name='tag_archive')
    @route(r'^tags/([\w-]+)/$', name='tag_archive')
    def tag_archive(self, request, tag=None):
        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no blog post tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {
            'tag': tag,
            'posts': posts
        }
        return render(request, 'blog/blog_index.html', context)

    @route(r'^categories/$', name='category_archive')
    @route(r'^categories/([\w-]+)/$', name='category_archive')
    def category_archive(self, request, category=None):
        try:
            category = Category.objects.get(slug=category)
        except Category.DoesNotExist:
            if category:
                msg = 'There are no blog post with category "{}"'.format(
                    category)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(category=category)
        context = {
            'category': category,
            'posts': posts
        }
        return render(request, 'blog/blog_index.html', context)

    def serve_preview(self, request, mode_name):
        return self.serve(request)

    def get_posts(self, tag=None, category=None):
        posts = Post.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        if category:
            posts = posts.filter(categories=category)
        return posts

    def get_child_tags(self):
        tags = []
        for post in self.get_posts():
            tags += post.get_tags
        tags = sorted(set(tags))
        return tags

    def get_child_categories(self):
        categories = []
        for post in self.get_posts():
            categories += post.get_categories
        categories = set(categories)
        return categories


class Post(Page):
    introduction = models.TextField(
        help_text='Text to describe the post',
        blank=True
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.'
    )
    body = StreamField(
        BaseStreamBlock(),
        verbose_name="Page body",
        blank=True
    )
    subtitle = models.CharField(max_length=255)
    tags = ClusterTaggableManager(through='PostTag', blank=True)
    date_published = models.DateField(
        "Date article published",
        blank=True,
        null=True
    )
    categories = ParentalManyToManyField('blog.Category', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle', classname='full'),
        FieldPanel('introduction', classname='full'),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        FieldPanel('date_published'),
        InlinePanel(
            'post_author_relationship',
            label="Author(s)",
            panels=None,
            min_num=1
        ),
        MultiFieldPanel([
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
            FieldPanel('tags'),
        ], heading="Blog information"),
    ]

    search_field = Page.search_fields + [
        index.SearchField('body'),
    ]

    def authors(self):
        authors = [
            n.author for n in self.post_author_relationship.all()
        ]
        return authors

    @property
    def get_tags(self):
        tags = self.tags.all()
        for tag in tags:
            tag.url = '/' + '/'.join(s.strip('/') for s in [
                self.get_parent().url,
                'tags',
                tag.slug
            ])
        return tags

    @property
    def get_categories(self):
        categories = self.categories.all()
        for category in categories:
            category.url = '/' + '/'.join(s.strip('/') for s in [
                self.get_parent().url,
                'categories',
                category.slug
            ])
        return categories

    parent_page_types = ['BlogIndex']

    subpage_types = []


class PostTag(TaggedItemBase):
    content_object = ParentalKey(
        'Post',
        related_name="tagged_items",
        on_delete=models.CASCADE
    )


@register_snippet
class Category(models.Model):
    name = models.CharField(unique=True, max_length=255)
    slug = models.SlugField(unique=True, default=uuid.uuid4)
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        ImageChooserPanel('thumbnail'),
    ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


@register_snippet
class Author(index.Indexed, ClusterableModel):
    nick_name = models.CharField("Nickname", max_length=254)
    job_title = models.CharField(
        "Job title",
        max_length=254,
        null=True,
        blank=True,
    )

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('nick_name'),
        FieldPanel('job_title'),
        ImageChooserPanel('image')
    ]

    search_fields = [
        index.SearchField('nick_name'),
    ]

    @property
    def thumb_image(self):
        try:
            return self.image.get_rendition('fill-50x50').img_tag()
        except:
            return ''

    def __str__(self):
        return self.nick_name

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'


class PostAuthorRelationship(Orderable, models.Model):
    page = ParentalKey(
        'Post',
        related_name='post_author_relationship',
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        'Author',
        related_name='author_person_relationship',
        on_delete=models.CASCADE,
    )

    panels = [
        SnippetChooserPanel('author')
    ]
