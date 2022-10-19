from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from ..models import Post, Group
from http import HTTPStatus
from test_utils.utils import (check_responses_of_given_urls,
                              check_status_code,
                              check_template,
                              check_redirect)
from .utils import (get_not_used_group_slug,
                    get_not_used_username,
                    get_not_used_post_id)
from django.core.cache import cache

User = get_user_model()


class PostUrlsTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.test_group = Group.objects.create(
            title="TestGroup",
            slug="TestGroupSlug",
            description="TestGroupdescription"
        )

        cls.post_author_1 = User.objects.create_user("post_author_1")
        cls.post_author_2 = User.objects.create_user("post_author_2")

        cls.author_1_post = Post.objects.create(
            text='Test text',
            author=cls.post_author_1,
            group=cls.test_group
        )

        cls.author_2_post = Post.objects.create(
            text='Test text',
            author=cls.post_author_2,
            group=cls.test_group
        )

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()

        self.post_author_1_client = Client()
        self.post_author_1_client.force_login(PostUrlsTests.post_author_1)

        self.post_author_2_client = Client()
        self.post_author_2_client.force_login(
            PostUrlsTests.post_author_2)
        cache.clear()

    def test_unauth_user_access(self):
        """Testing pages access for guest client"""

        urls_for_check = {
            "/": HTTPStatus.OK,

            f"/group/{PostUrlsTests.test_group.slug}/": HTTPStatus.OK,

            f"/group/{get_not_used_group_slug()}/": HTTPStatus.NOT_FOUND,

            f"/profile/{PostUrlsTests.post_author_1.username}/": HTTPStatus.OK,

            f"/profile/{get_not_used_username()}/":
                HTTPStatus.NOT_FOUND,

            f"/posts/{PostUrlsTests.author_1_post.id}/": HTTPStatus.OK,

            f"/posts/{get_not_used_post_id()}/": HTTPStatus.NOT_FOUND,

            f"/posts/{PostUrlsTests.author_1_post.id}/edit/": HTTPStatus.FOUND,

            "/create/": HTTPStatus.FOUND,

            "/follow/": HTTPStatus.FOUND,

            f"/profile/{PostUrlsTests.post_author_1.username}/follow/":
                HTTPStatus.FOUND,

            f"/profile/{PostUrlsTests.post_author_1.username}/unfollow/":
                HTTPStatus.FOUND,

            "/unexisting_page/": HTTPStatus.NOT_FOUND,

        }

        check_responses_of_given_urls(self,
                                      self.guest_client,
                                      check_status_code,
                                      urls_for_check)

    def test_logged_user_access(self):
        """Testing pages access for logged user
            and post author/not post author"""

        urls_for_check = {
            "/":
                HTTPStatus.OK,

            f"/group/{PostUrlsTests.test_group.slug}/": HTTPStatus.OK,

            f"/group/{get_not_used_group_slug()}/": HTTPStatus.NOT_FOUND,

            f"/profile/{PostUrlsTests.post_author_1.username}/":
                HTTPStatus.OK,

            (f"/profile/{get_not_used_username()}/"):
                HTTPStatus.NOT_FOUND,

            f"/posts/{PostUrlsTests.author_1_post.id}/":
                HTTPStatus.OK,

            f"/posts/{get_not_used_post_id()}/": HTTPStatus.NOT_FOUND,

            "/create/":
                HTTPStatus.OK,

            f"/posts/{PostUrlsTests.author_1_post.id}/edit/":
                HTTPStatus.OK,

            f"/posts/{PostUrlsTests.author_2_post.id}/edit/":
                HTTPStatus.FOUND,

            "/follow/": HTTPStatus.OK,

            f"/profile/{PostUrlsTests.post_author_1.username}/follow/":
                HTTPStatus.FOUND,

            f"/profile/{get_not_used_username()}/follow/":
                HTTPStatus.NOT_FOUND,

            f"/profile/{PostUrlsTests.post_author_1.username}/unfollow/":
                HTTPStatus.FOUND,

            f"/profile/{get_not_used_username}/unfollow/":
                HTTPStatus.NOT_FOUND,

            "/unexisting_page/":
                HTTPStatus.NOT_FOUND,
        }

        check_responses_of_given_urls(self,
                                      self.post_author_1_client,
                                      check_status_code,
                                      urls_for_check)

    def test_guest_client_templates(self):
        """Testing pages templates for guest"""

        urls_for_check = {
            "/": "posts/index.html",

            f"/group/{PostUrlsTests.test_group.slug}/":
                "posts/group_list.html",

            f"/group/{get_not_used_group_slug()}/":
                "core/404.html",

            f"/profile/{PostUrlsTests.post_author_1.username}/":
                "posts/profile.html",

            f"/group/{get_not_used_username()}/":
                "core/404.html",

            f"/posts/{PostUrlsTests.author_1_post.id}/":
                "posts/post_detail.html",

            f"/posts/{get_not_used_post_id()}/":
                "core/404.html",
        }

        check_responses_of_given_urls(self,
                                      self.post_author_1_client,
                                      check_template,
                                      urls_for_check)

    def test_post_author_templates(self):
        """Testing pages templates for posts author"""

        urls_for_check = {
            "/": "posts/index.html",

            "/follow/": "posts/follow.html",

            f"/group/{PostUrlsTests.test_group.slug}/":
                "posts/group_list.html",

            f"/group/{get_not_used_group_slug()}/":
                "core/404.html",

            f"/profile/{PostUrlsTests.post_author_1.username}/":
                "posts/profile.html",

            f"/group/{get_not_used_username()}/":
                "core/404.html",

            f"/posts/{PostUrlsTests.author_1_post.id}/":
                "posts/post_detail.html",

            f"/group/{get_not_used_post_id()}/":
                "core/404.html",

            "/create/":
                "posts/create_post.html",

            f"/posts/{PostUrlsTests.author_1_post.id}/edit/":
                "posts/create_post.html",
        }

        check_responses_of_given_urls(self,
                                      self.post_author_1_client,
                                      check_template,
                                      urls_for_check)

    def test_guest_user_redirect(self):
        "Test redirect target for guest user on create and edit post pages"
        urls_for_check = {
            "/create/":
            "/auth/login/?next=/create/",

            f"/posts/{PostUrlsTests.author_1_post.id}/edit/":
            f"/auth/login/?next=/posts/{PostUrlsTests.author_1_post.id}/edit/",

            "/follow/":
            "/auth/login/?next=/follow/",

            f"/profile/{PostUrlsTests.post_author_1.username}/follow/":
                (f"/auth/login/?next=/profile/"
                 f"{PostUrlsTests.post_author_1.username}/follow/"),

            f"/profile/{PostUrlsTests.post_author_1.username}/unfollow/":
                (f"/auth/login/?next=/profile/"
                 f"{PostUrlsTests.post_author_1.username}/unfollow/")
        }

        check_responses_of_given_urls(self,
                                      self.guest_client,
                                      check_redirect,
                                      urls_for_check)

    def test_not_post_author_redirect(self):
        """Test redirect target for not post author"""

        urls_for_check = {
            f"/posts/{PostUrlsTests.author_1_post.id}/edit/":
                f"/posts/{PostUrlsTests.author_1_post.id}/",

            f"/profile/{PostUrlsTests.post_author_1.username}/follow/":
                f"/profile/{PostUrlsTests.post_author_1.username}/",

            f"/profile/{PostUrlsTests.post_author_1.username}/unfollow/":
                f"/profile/{PostUrlsTests.post_author_1.username}/"
        }

        check_responses_of_given_urls(self,
                                      self.post_author_2_client,
                                      check_redirect,
                                      urls_for_check)
