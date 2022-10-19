from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def test_model_have_correct_object_name(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(PostModelTest.post.__str__(), "Тестовый текст")


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )

    def test_model_have_correct_object_name(self):
        self.assertEqual(GroupModelTest.group.__str__(), "Тестовая группа")
