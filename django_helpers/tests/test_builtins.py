from django.test import TestCase
from django.test.utils import override_settings
from django.conf.urls import url, include
from django.views.generic.base import View
from django.test.client import RequestFactory
from django.http import QueryDict
from django.template import Template, RequestContext

from ..builtins import (
    active_path,
    active_query,
    query,
    query_toggle,
    percentage,
    currency,
    intcurrency,
    humanize_time,
    active_query_by_key,
    query_by_key,
    query_toggle_by_key,
    to_json
)

nested_patterns = [
    url(r'^$', View.as_view(), name="view"),
    url(r'^bar/$', View.as_view(), name="sub-view"),
    url(r'^baz/$', View.as_view(), name="sub-view-2"),
    url(r'^baz/(?P<id>[0-9]+)/$', View.as_view(), name="sub-view-id")
]

urlpatterns = [
    url(r'^foo/', include(nested_patterns, namespace="namespace"))
]


@override_settings(ROOT_URLCONF=__name__)
class ActivePathTestCase(TestCase):
    """
    TODO: These tests need some documentation
    """

    def setUp(self):
        request = RequestFactory().get('/foo/bar/')
        self.context = {
            'request': request
        }

    def test_exact_path_match(self):
        output = active_path(self.context, '/foo/bar/', exact=True)
        self.assertEquals(output, 'active')

    def test_exact_path_no_match(self):
        output = active_path(self.context, '/foo/', exact=True)
        self.assertEquals(output, '')

    def test_partial_path_match(self):
        output = active_path(self.context, '/foo/')
        self.assertEquals(output, 'active')

    def test_partial_path_no_match(self):
        output = active_path(self.context, '/baz/')
        self.assertEquals(output, '')

    def test_url_match(self):
        output = active_path(self.context, 'namespace:sub-view')
        self.assertEquals(output, 'active')

    def test_url_params_match(self):
        request = RequestFactory().get('/foo/baz/10/')
        context = {
            'request': request
        }
        output = active_path(context, 'namespace:sub-view-id', id=10)
        self.assertEquals(output, 'active')

    def test_url_params_no_match(self):
        request = RequestFactory().get('/foo/baz/10/')
        context = {
            'request': request
        }
        output = active_path(context, 'namespace:sub-view-id', id=5)
        self.assertEquals(output, '')

    def test_url_no_match(self):
        output = active_path(self.context, 'namespace:does-not-exist')
        self.assertEquals(output, '')

    def test_url_namespace_match(self):
        self.context['request'].path = '/foo/baz/'
        output = active_path(self.context, 'namespace:')
        self.assertEquals(output, 'active')

    def test_url_namespace_no_match(self):
        output = active_path(self.context, 'does-not-exist:')
        self.assertEquals(output, '')

    def test_bad_path(self):
        self.context['request'].path = '/this/does/not/exist/'
        output = active_path(self.context, 'namespace:sub-view')
        self.assertEquals(output, '')

    def test_custom_active_class(self):
        output = active_path(self.context, 'namespace:sub-view', active_class='my-active-class')
        self.assertEquals(output, 'my-active-class')


@override_settings(ROOT_URLCONF=__name__)
class ActiveQueryTestCase(TestCase):
    """
    TODO: These tests need some documentation.
    """

    def setUp(self):
        request = RequestFactory().get('/foo/bar/?foo=bar&status=active&status=archived')
        self.context = {
            'request': request
        }

    def test_match_single_param(self):
        output = active_query(self.context, foo='bar')
        self.assertEquals(output, 'active')

    def test_match_multiple_params(self):
        output = active_query(self.context, foo='bar', status='archived')
        self.assertEquals(output, 'active')

    def test_no_match_multiple_params(self):
        output = active_query(self.context, foo='bar', status='asleep')
        self.assertEquals(output, '')

    def test_match_duplicate_keys(self):
        output = active_query(self.context, status='active')
        self.assertEquals(output, 'active')

    def test_no_match(self):
        output = active_query(self.context, foo='biz')
        self.assertEquals(output, '')

    def test_none_existant_query(self):
        output = active_query(self.context, fiz='biz')
        self.assertEquals(output, '')

    def test_active_query_by_key(self):
        output = active_query_by_key(self.context, 'status', 'archived')
        self.assertEquals(output, 'active')

    def test_active_query_by_key_no_match(self):
        output = active_query_by_key(self.context, 'status', 'paused')
        self.assertEquals(output, '')


@override_settings(ROOT_URLCONF=__name__)
class QueryTestCase(TestCase):
    """
    TODO: These tests need some documentation.
    """

    def setUp(self):
        request = RequestFactory().get('/foo/bar/?search=my+search+string&foo=bar')
        self.context = {
            'request': request
        }

    def test_no_changes(self):
        query_string = query(self.context)
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertEquals(GET['foo'], 'bar')

    def test_add_param(self):
        query_string = query(self.context, bar='baz')
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertEquals(GET['foo'], 'bar')
        self.assertEquals(GET['bar'], 'baz')

    def test_override_param(self):
        query_string = query(self.context, foo='baz')
        GET = QueryDict(query_string)
        self.assertEquals(GET['foo'], 'baz')
        self.assertEquals(GET['search'], 'my search string')

    def test_remove_param(self):
        query_string = query(self.context, foo=None)
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertNotIn('foo', GET)

    def test_query_by_key(self):
        query_string = query_by_key(self.context, 'bar', 'baz')
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertEquals(GET['foo'], 'bar')
        self.assertEquals(GET['bar'], 'baz')


@override_settings(ROOT_URLCONF=__name__)
class QueryToggleTestCase(TestCase):
    """
    TODO: These tests need some documentation.
    """

    def setUp(self):
        request = RequestFactory().get('/foo/bar/?search=my+search+string&foo=bar')
        self.context = {
            'request': request
        }

    def test_no_changes(self):
        query_string = query_toggle(self.context)
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertEquals(GET['foo'], 'bar')

    def test_add_param(self):
        query_string = query_toggle(self.context, foo='baz')
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertIn('bar', GET.getlist('foo'))
        self.assertIn('baz', GET.getlist('foo'))

    def test_add_new_param(self):
        query_string = query_toggle(self.context, fiz='biz')
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertIn('bar', GET.getlist('foo'))
        self.assertIn('biz', GET.getlist('fiz'))

    def test_remove_param(self):
        query_string = query_toggle(self.context, foo='bar')
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertNotIn('foo', GET)

    def test_query_toggle_by_key(self):
        query_string = query_toggle_by_key(self.context, 'foo', 'baz')
        GET = QueryDict(query_string)
        self.assertEquals(GET['search'], 'my search string')
        self.assertIn('bar', GET.getlist('foo'))
        self.assertIn('baz', GET.getlist('foo'))


class QueryKeyExistsTestCase(TestCase):
    def setUp(self):
        self.template = Template('{% query_key_exists "search" %}IT WORKS{% endquery_key_exists %}')

    def test_query_key_exists(self):
        request = RequestFactory().get('/foo/bar/?search=my+search+string&foo=bar')
        rendered = self.template.render(RequestContext(request))

        self.assertEquals(rendered, 'IT WORKS')

    def test_query_key_not_exists(self):
        request = RequestFactory().get('/foo/bar/?foo=bar')
        rendered = self.template.render(RequestContext(request))

        self.assertEquals(rendered, '')


@override_settings(ROOT_URLCONF=__name__)
class PercentageTestCase(TestCase):
    """
    TODO: These tests need some documentation.
    """

    def test_default_format(self):
        self.assertEquals(percentage(1), '100.00%')
        self.assertEquals(percentage(0.1), '10.00%')
        self.assertEquals(percentage(0.01), '1.00%')

    def test_decimal_places(self):
        num = 0.111
        self.assertEquals(percentage(num, decimal_places=0), '11%')
        self.assertEquals(percentage(num, decimal_places=1), '11.1%')
        self.assertEquals(percentage(num, decimal_places=2), '11.10%')
        self.assertEquals(percentage(num, decimal_places=3), '11.100%')

    def test_not_a_number(self):
        self.assertEquals(percentage(""), "")
        self.assertEquals(percentage(None), "")


@override_settings(ROOT_URLCONF=__name__)
class CurrencyTestCase(TestCase):
    """
    TODO: These tests need some documentation.
    """

    def test_positive_default_format(self):
        self.assertEquals(currency(1), '$1.00')
        self.assertEquals(currency(0.1), '$0.10')
        self.assertEquals(currency(0.01), '$0.01')

    def test_negative_default_format(self):
        self.assertEquals(currency(-1), '($1.00)')
        self.assertEquals(currency(-0.1), '($0.10)')
        self.assertEquals(currency(-0.01), '($0.01)')

    def test_negative_no_parentheses(self):
        self.assertEquals(currency(-1, use_parentheses=False), '-$1.00')
        self.assertEquals(currency(-0.1, use_parentheses=False), '-$0.10')
        self.assertEquals(currency(-0.01, use_parentheses=False), '-$0.01')

    def test_no_cents(self):
        self.assertEquals(currency(1, include_cents=False), '$1')
        self.assertEquals(currency(0.1, include_cents=False), '$0')
        self.assertEquals(currency(0.01, include_cents=False), '$0')
        self.assertEquals(currency(0.5, include_cents=False), '$1')

    def test_not_a_number(self):
        self.assertEquals(currency(""), "")
        self.assertEquals(currency(None), "")


@override_settings(ROOT_URLCONF=__name__)
class IntCurrencyTestCase(TestCase):
    """
    TODO: These tests need some documentation.
    """

    def test_default_format(self):
        self.assertEquals(intcurrency(1), '$1')
        self.assertEquals(intcurrency(0.1), '$0')
        self.assertEquals(intcurrency(0.01), '$0')
        self.assertEquals(intcurrency(0.5), '$1')

    def test_negative_default_format(self):
        self.assertEquals(intcurrency(-1), '($1)')
        self.assertEquals(intcurrency(-0.1), '($0)')
        self.assertEquals(intcurrency(-0.01), '($0)')
        self.assertEquals(intcurrency(-0.5), '($1)')

    def test_negative_no_parentheses(self):
        self.assertEquals(intcurrency(-1, use_parentheses=False), '-$1')
        self.assertEquals(intcurrency(-0.1, use_parentheses=False), '-$0')
        self.assertEquals(intcurrency(-0.01, use_parentheses=False), '-$0')
        self.assertEquals(intcurrency(-0.5, use_parentheses=False), '-$1')

    def test_not_a_number(self):
        self.assertEquals(intcurrency(""), "")
        self.assertEquals(intcurrency(None), "")


@override_settings(ROOT_URLCONF=__name__)
class HumanizeTimeTestCase(TestCase):

    def test_default_units(self):
        self.assertEquals(humanize_time(0), '')
        self.assertEquals(humanize_time(.1), 'less than a second')
        self.assertEquals(humanize_time(100), '1 minute, 40 seconds')
        self.assertEquals(humanize_time(290304001), '10 years, 1 second')
        self.assertEquals(humanize_time(29030399), '11 months, 3 weeks, 6 days, 23 hours, 59 minutes, 59 seconds')

    def test_units(self):
        self.assertEquals(humanize_time(1, 'years'), '1 year')
        self.assertEquals(humanize_time(.1, 'years'), '1 month, 5 days, 14 hours, 24 minutes')


class ToJsonTestCase(TestCase):
    def test_to_json(self):
        value = to_json({'test': 1})
        self.assertEquals(value, '{"test": 1}')
