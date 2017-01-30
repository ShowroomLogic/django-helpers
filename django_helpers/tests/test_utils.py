from django.test import TestCase
from django.test.client import RequestFactory
from . import settings

from ..utils import paginate, redirect_or_next


class PaginateTestCase(TestCase):

    def setUp(self):
        self.items = list(range(1, 21))

    def test_paginate_default(self):
        request = RequestFactory().get('/')
        page = paginate(request, self.items, 10)
        self.assertEquals(page[0], 1)

    def test_paginate_page_2(self):
        request = RequestFactory().get('/', {'page': 2})
        page = paginate(request, self.items, 10)
        self.assertEquals(page[0], 11)

    def test_paginate_empty_page(self):
        request = RequestFactory().get('/', {'page': 3})
        page = paginate(request, self.items, 10)
        self.assertEquals(page[0], 11)


class RedirectOrNextTestCase(TestCase):

    def test_next(self):
        request = RequestFactory().get('/', {'next': 'http://www.google.com'})
        redirect = redirect_or_next(request, 'http://www.ebay.com')
        self.assertEquals(redirect.url, 'http://www.google.com')

    def test_redirect(self):
        request = RequestFactory().get('/', {})
        redirect = redirect_or_next(request, 'http://www.ebay.com')
        self.assertEquals(redirect.url, 'http://www.ebay.com')
