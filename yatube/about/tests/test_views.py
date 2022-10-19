from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from test_utils.utils import (check_responses_of_given_urls,
                              check_status_code,
                              check_template)


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        names = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK
        }

        check_responses_of_given_urls(self,
                                      self.guest_client,
                                      check_status_code,
                                      names)

    def test_about_pages_uses_correct_template(self):
        template_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

        check_responses_of_given_urls(self,
                                      self.guest_client,
                                      check_template,
                                      template_pages_names)
