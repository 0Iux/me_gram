import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_2',
            description='Тестовое описание 2',
        )
        cls.post = [Post(
            text=f'post {i}',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        ) for i in range(1, 12)]
        Post.objects.bulk_create(cls.post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_fields = {
            'text': forms.fields.CharField,
            # 'group': forms.fields.SlugField,
        }
        self.templates_pages_names = {
            'posts/index.html': ('posts:index', 0),
            'posts/group_list.html': (
                'posts:group_list', {'slug': self.group.slug}
            ),
            'posts/post_detail.html': (
                'posts:post_detail', {'post_id': Post.objects.last().pk}
            ),
            'posts/profile.html': (
                'posts:profile', {'username': self.user.username}
            ),
            'posts/create_post.html': (
                'posts:post_edit', {'post_id': Post.objects.last().pk}
            ),
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse(reverse_name[0], kwargs=reverse_name[1])
                )
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_context(self):
        """URL-адрес использует соответствующий контекст."""
        for name, wargs in self.templates_pages_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(
                    reverse(wargs[0], kwargs=wargs[1])
                )
                if response.context.get('form'):
                    for value, expected in self.form_fields.items():
                        with self.subTest(value=value):
                            form_field = response.context.get(
                                'form').fields.get(value)
                            self.assertIsInstance(form_field, expected)
                if response.context.get('page_obj'):
                    first_object = response.context['page_obj'][0]
                    self.assertEqual(
                        first_object.text, Post.objects.first().text
                    )
                    self.assertEqual(
                        first_object.image, Post.objects.first().image
                    )
                    self.assertEqual(first_object.id, Post.objects.first().pk)
                    self.assertEqual(
                        first_object.group.title, self.group.title
                    )
                if response.context.get('post'):
                    obj = response.context['post']
                    self.assertEqual(obj.text, Post.objects.last().text)
                    self.assertEqual(obj.image, Post.objects.last().image)
                if response.context.get('author'):
                    self.assertEqual(
                        response.context['page_obj'][0].text,
                        Post.objects.filter(author=self.user).first().text
                    )
                    self.assertEqual(
                        response.context['author'].username, self.user.username
                    )

    def test_contains_records(self):
        for wargs in self.templates_pages_names.values():
            cache.clear()
            with self.subTest(name=wargs[0]):
                response = self.authorized_client.get(
                    reverse(wargs[0], kwargs=wargs[1])
                )
                if response.context.get('page_obj'):
                    self.assertEqual(
                        len(response.context['page_obj']), 10
                    )
                    response = self.authorized_client.get(
                        reverse('posts:index') + '?page=2'
                    )
                    self.assertEqual(
                        len(response.context['page_obj']), 1
                    )

    def test_group_without_posts(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PostsCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.post = [Post(
            text=f'post {i}',
            author=cls.user,
        ) for i in range(1, 5)]
        Post.objects.bulk_create(cls.post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=self.user,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)
