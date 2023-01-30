import shutil
import tempfile

from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.forms import PostForm
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост два',
            'slug': 'Тестовая группа',
            'image': self.uploaded
        }
        old_posts = list(Post.objects.values('pk'))
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth'}
        )
        )
        id = [x for x in list(Post.objects.values('pk')) if x not in old_posts]
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                id=id[0]['pk'],
                text=form_data['text'],
                # group=form_data['slug'],
                image='posts/small.gif',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        old_post = Post.objects.last()
        form_data = {
            'text': 'Изменено!',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': old_post.pk}
        )
        )
        new_post = get_object_or_404(Post, pk=old_post.pk)
        self.assertNotEqual(old_post.text, new_post.text)
        self.assertEqual(old_post.author, new_post.author)
        self.assertEqual(old_post.group, new_post.group)

    def test_guest_cant_add_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост два',
            'slug': 'Тестовая группа',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next=' + reverse(
                'posts:post_create'
            )
        )
        self.assertEqual(Post.objects.count(), tasks_count)


class PostCommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guests_cant_add_comments(self):
        form_data = {'text': 'commentssssssss'}
        response = self.client.get(reverse('posts:add_comment', kwargs={
            'post_id': self.post.pk,
        }),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            'users:login'
        ) + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk}
        ) + '%3Ftext%3D' + form_data['text'])
        pass

    def test_create_comments(self):
        form_data = {'text': 'commentssssssss'}
        old_posts = list(Post.objects.values('comments'))
        response = self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk}
        ),
            data=form_data,
            follow=True)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ))
        new = list(Post.objects.values('comments'))
        self.assertNotEqual(old_posts, new)
