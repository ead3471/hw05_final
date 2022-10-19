from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post, Comment
from django.urls import reverse

User = get_user_model()


class PostTestForms(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.new_group = Group.objects.create(
            slug="new_group_slug",
            description="new_group_description",
            title="new_group_title"
        )

        cls.post_author = User.objects.create_user("post_author")
        cls.post_author_client = Client()
        cls.post_author_client.force_login(cls.post_author)

        cls.not_post_author = User.objects.create_user('not_post_author')
        cls.not_post_author_client = Client()
        cls.not_post_author_client.force_login(cls.not_post_author)

        cls.guest_client = Client()

        cls.new_post = Post.objects.create(
            text="New post",
            author=cls.post_author
        )

    def test_post_create_with_and_without_group(self):
        forms = [
            {
                "text": "Post with group",
                "group": PostTestForms.new_group.id
            },
            {
                "text": "Post without group"
            }
        ]

        for form in forms:
            posts_count = Post.objects.count()

            response = (PostTestForms
                        .post_author_client
                        .post(reverse('posts:post_create'),
                              data=form,
                              follow=True))

            self.assertRedirects(
                response,
                reverse(
                    'posts:profile',
                    args=(PostTestForms.post_author.username,)))

            self.assertEquals(posts_count + 1, Post.objects.count())

            created_objects = (Post
                               .objects
                               .filter(text=form["text"],
                                       author=PostTestForms.post_author)
                               )

            if "group" in form.keys():
                created_objects = created_objects.filter(group=form["group"])

            self.assertTrue(created_objects.exists())

    def test_post_create_by_unauth_client(self):
        posts_count = Post.objects.count()

        form = {"text": "Post created by anauth user",
                "group": PostTestForms.new_group.id}

        response = (PostTestForms
                    .guest_client
                    .post(reverse('posts:post_create'),
                          data=form,
                          follow=True))

        self.assertRedirects(response, '/auth/login/?next=/create/')

        self.assertEquals(posts_count, Post.objects.count())

        created_objects = (Post
                           .objects
                           .filter(text=form["text"],
                                   group=form["group"])
                           )

        self.assertFalse(created_objects.exists())

    def test_post_edit_by_author(self):
        edit_post_data = {
            "text": "new_text",
            "group": PostTestForms.new_group.id,
        }
        response = (PostTestForms
                    .post_author_client
                    .post(
                        reverse('posts:post_edit',
                                args=(PostTestForms.new_post.id,)),
                        data=edit_post_data,
                        follow=True))

        self.assertRedirects(
            response,
            reverse("posts:post_detail",
                    args=(PostTestForms.new_post.id,)))

        edited_post = Post.objects.filter(
            id=PostTestForms.new_post.id,
            text=edit_post_data["text"],
            group=PostTestForms.new_group.id,
        )
        self.assertTrue(edited_post.exists())

    def test_post_edit_by_guest(self):
        edit_post_data = {
            "text": "new_text",
            "group": PostTestForms.new_group.id,
        }
        response = (PostTestForms
                    .guest_client
                    .post(
                        reverse('posts:post_edit',
                                args=(PostTestForms.new_post.id,)),
                        data=edit_post_data,
                        follow=True))

        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{PostTestForms.new_post.id}/edit/')

        edited_post = Post.objects.filter(
            id=PostTestForms.new_post.id,
            text=edit_post_data["text"],
            group=PostTestForms.new_group.id,
        )
        self.assertFalse(edited_post.exists())

    def test_post_edit_by_not_author(self):
        edit_post_data = {
            "text": "new_text",
            "group": PostTestForms.new_group.id,
        }
        response = (PostTestForms
                    .not_post_author_client
                    .post(
                        reverse('posts:post_edit',
                                args=(PostTestForms.new_post.id,)),
                        data=edit_post_data,
                        follow=True))

        self.assertRedirects(
            response,
            f'/posts/{PostTestForms.new_post.id}/')

        edited_post = Post.objects.filter(
            id=PostTestForms.new_post.id,
            text=edit_post_data["text"],
            group=PostTestForms.new_group.id,
        )
        self.assertFalse(edited_post.exists())

    def test_comment_add_by_auth_user(self):
        form = {"text": "New comment from auth user"}
        comments_count = Comment.objects.count()

        response = PostTestForms.post_author_client.post(
            reverse('posts:add_comment', args=(PostTestForms.new_post.id,)),
            data=form,
            follow=True)

        # 1.Check comment is created
        self.assertEquals(comments_count + 1, Comment.objects.count())

        # 1. Check redirect to post detail page
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(PostTestForms.new_post.id,)))

        # 2. Check Comment is created with right values
        created_comments = Comment.objects.filter(
            post=PostTestForms.new_post,
            author=PostTestForms.post_author,
            text=form["text"]
        )

        self.assertEquals(len(created_comments), 1)

    def test_comment_add_by_unauth_user(self):
        form = {"text": "New comment from auth user"}
        comments_count = Comment.objects.count()

        response = PostTestForms.guest_client.post(
            reverse('posts:add_comment', args=(PostTestForms.new_post.id,)),
            data=form,
            follow=True)

        # 1.Check comment is not created
        self.assertEquals(comments_count, Comment.objects.count())

        # 1. Check redirect to login page
        self.assertRedirects(
            response,
            '/auth/login/?next=/posts/1/comment/')
