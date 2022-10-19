from django.test import TestCase, Client
from http import HTTPStatus
from test_utils.utils import (check_responses_of_given_urls,
                              check_status_code,
                              check_template)


class AboutUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guest_client = Client()
        super().setUpClass()

    def test_http_statuses(self):
        urls_for_check = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK
        }

        check_responses_of_given_urls(self,
                                      AboutUrlsTest.guest_client,
                                      check_status_code,
                                      urls_for_check)

    def test_templates(self):
        urls_for_check = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

        check_responses_of_given_urls(self,
                                      AboutUrlsTest.guest_client,
                                      check_template,
                                      urls_for_check)
