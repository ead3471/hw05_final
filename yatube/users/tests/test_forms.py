from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersFormsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()

    def test_new_user_creation(self):
        form_data = {
            'first_name': 'new_user_first_name',
            'last_name': 'new_user_last_name',
            'username': 'new_user_username',
            'email': 'new@new.com',
            'password1': 'Cegthfdhjkm123.',
            'password2': 'Cegthfdhjkm123.'
        }

        users_count = User.objects.count()

        response = UsersFormsTest.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertEquals(users_count + 1, User.objects.count())

        self.assertRedirects(response, reverse('posts:index'))

        new_user = User.objects.filter(
            username=form_data['username'],
            first_name=form_data['first_name'],
            last_name=form_data['last_name'],
            email=form_data['email'],
        )

        self.assertTrue(new_user.exists())
