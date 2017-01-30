from django.test import TestCase
from django.test.client import RequestFactory
from django.db import models
from . import settings

import django_filters

from ..filters import DefaultFilterSet, TagFilter, SearchFilter


class MockQuerySet(object):

    def __init__(self):
        self.filters = {}

    def all(self):
        return self

    def distinct(self):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def none(self):
        return self

    def filter(self, *args, **kwargs):
        self.filters.update(kwargs)
        for arg in args:
            for i in arg.children:
                if isinstance(i, tuple):
                    self.filters[i[0]] = i[1]
        return self


class MockModel(models.Model):
    name = models.CharField(max_length=128)
    status = models.CharField(max_length=16)
    
    class Meta:
        app_label = 'test'


class TestFilterSet(DefaultFilterSet):
    search = SearchFilter(['name__icontains', 'status__startswith'])
    tags = TagFilter()
    status = django_filters.MultipleChoiceFilter(choices=[
        ('active', 'active'),
        ('paused', 'paused'),
        ('archived', 'archived')
    ])

    class Meta:
        model = MockModel
        fields = [
            'search',
            'status',
            'tags'
        ]
        order_by = [
            'name',
            'status'
        ]
        defaults = {
            'status': ['active', 'paused'],
            'tags': 'foo'
        }


class DefaultFilterSetTestCase(TestCase):

    def test_default_filter(self):
        """
        The default filter should only include ACTIVE and PAUSED
        models. So the resulting dataset should have 2 items.
        """
        request = RequestFactory().get('/?foo=bar')
        qs = MockQuerySet()
        filter = TestFilterSet(request.GET, qs)
        self.assertEquals(filter.data.getlist('status'), ['active', 'paused'])
        self.assertEquals(filter.data.getlist('tags'), ['foo'])
        self.assertEquals(filter.data.getlist('foo'), ['bar'])

    def test_explicit_filter(self):
        """
        This tests that if explicit filters set they will override the defaults
        """
        request = RequestFactory().get('/?status=archived')
        qs = MockQuerySet()
        filter = TestFilterSet(request.GET, qs)
        self.assertEquals(filter.data.getlist('status'), ['archived'])


class TagFilterTestCase(TestCase):

    def test_no_op(self):
        """
        Tests that filters are applied for tags
        """
        request = RequestFactory().get('/?tags=')
        qs = MockQuerySet()
        filter = TestFilterSet(request.GET, qs)
        self.assertNotIn('tags__slug__in', filter.qs.filters)

    def test_single_value(self):
        """
        Tests that filters are applied for tags
        """
        qs = MockQuerySet()
        filter = TestFilterSet({'tags': 'foo'}, qs)
        self.assertEquals(filter.qs.filters['tags__slug__in'], ['foo'])

    def test_tag_filter(self):
        """
        Tests that filters are applied for tags
        """
        request = RequestFactory().get('/?tags=foo&tags=bar')
        qs = MockQuerySet()
        filter = TestFilterSet(request.GET, qs)
        self.assertEquals(filter.qs.filters['tags__slug__in'], ['foo', 'bar'])


class SearchFilterTestCase(TestCase):

    def test_no_op(self):
        """
        Tests that filters are applied for tags
        """
        request = RequestFactory().get('/?search=&tags=&status=')
        qs = MockQuerySet()
        filter = TestFilterSet(request.GET, qs)
        self.assertEquals(filter.qs.filters, {})

    def test_single_value(self):
        """
        Tests that filters are applied for tags
        """
        qs = MockQuerySet()
        filter = TestFilterSet({'search': 'foo'}, qs)
        self.assertEquals(filter.qs.filters['name__icontains'], 'foo')
        self.assertEquals(filter.qs.filters['status__startswith'], 'foo')

    def test_tag_filter(self):
        """
        Tests that filters are applied for tags
        """
        request = RequestFactory().get('/?search=foobar')
        qs = MockQuerySet()
        filter = TestFilterSet(request.GET, qs)
        self.assertEquals(filter.qs.filters['name__icontains'], 'foobar')
        self.assertEquals(filter.qs.filters['status__startswith'], 'foobar')

    def test_word_search(self):

        class TestFilterSet(DefaultFilterSet):
            search = SearchFilter(['name__icontains', 'status__startswith'], exact=False)

            class Meta:
                model = MockModel
                fields = [
                    'search'
                ]

        request = RequestFactory().get('/?search=foo bar')
        qs = MockQuerySet()
        filter = TestFilterSet(request.GET, qs)
        self.assertEquals(filter.qs.filters['name__icontains'], 'bar')
        self.assertEquals(filter.qs.filters['status__startswith'], 'bar')
