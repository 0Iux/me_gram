from django.test import TestCase, Client
from django.core.cache import cache

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.public_url = {
            '/': 'posts/index.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
        }
        self.private_url = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }

    def test_post_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url = {**self.private_url, **self.public_url}
        for url, template in templates_url.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_urls_is_working_200(self):
        for page in self.public_url.keys():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_post_urls_is_working_302(self):
        for page in self.private_url:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 302)

    def test_post_unknown_page_404(self):
        page_name = '/lol/'
        response = self.authorized_client.get(page_name)
        self.assertEqual(response.status_code, 404)
