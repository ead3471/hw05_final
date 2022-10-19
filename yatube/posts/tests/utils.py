from django.test import TestCase
from typing import Iterable, List
from django.utils.crypto import get_random_string
from django.db.models import Max
from ..models import Group, Post
from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models

User = get_user_model()


def create_image(image_name=None) -> SimpleUploadedFile:
    small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                 b'\x01\x00\x80\x00\x00\x00\x00\x00'
                 b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                 b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                 b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                 b'\x0A\x00\x3B'
                 )

    result_image = SimpleUploadedFile(
        name=f'small_{image_name or get_random_string(7)}.gif',
        content=small_gif,
        content_type='image/gif'
    )
    return result_image


def compare_model_objects_list(test_case: TestCase,
                               testing_objects: Iterable[models.Model],
                               expected_objects: Iterable[models.Model],
                               model_attributes: List[str] = None):
    """Sequentely compares all given attributes from
    testing_objects list with attributes from expected_objects list.
    If model_attributes is None method will checkk all attributes"""

    test_case.assertEquals(len(testing_objects), len(expected_objects))
    if len(testing_objects) == 0:
        return

    if not model_attributes:
        model_class = testing_objects[0].__class__
        model_attributes = [
            field.name for field in model_class._meta.get_fields()]

    for testing_object, expected_object in zip(testing_objects,
                                               expected_objects):
        with test_case.subTest(testing_object=testing_object,
                               expected_object=expected_object):
            for model_attribute in model_attributes:
                with test_case.subTest(model_attrilbute=model_attribute):
                    test_case.assertEquals(
                        testing_object.__getattribute__(model_attribute),
                        expected_object.__getattribute__(model_attribute))


def check_posts_fields(test_case: TestCase,
                       posts_from_page: Iterable[Post],
                       expected_posts: Iterable[Post]):
    """Sequentely compares all the post objects from
    posts_from_page with posts from expected_posts"""

    compare_model_objects_list(test_case,
                               testing_objects=posts_from_page,
                               expected_objects=expected_posts)


def check_page_contains_post_on_first_position(test_case: TestCase,
                                               posts: Page,
                                               expected_post: Post):
    test_case.assertGreater(len(posts), 0)
    test_case.assertEquals(posts[0].id, expected_post.id)


def get_not_used_group_slug() -> str:
    random_slug = get_random_string(7)
    while random_slug in Group.objects.values_list("slug"):
        random_slug = get_random_string(7)
    return random_slug


def get_not_used_post_id() -> int:
    return Post.objects.all().aggregate(Max("id"))["id__max"] + 1


def get_not_used_username() -> str:
    random_username = get_random_string(7)
    while random_username in User.objects.values_list("username"):
        random_username = get_random_string(7)
    return random_username
