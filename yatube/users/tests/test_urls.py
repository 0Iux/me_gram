# from django.contrib.auth import get_user_model
# from django.test import TestCase, Client

# from posts.models import Post, Group

# User = get_user_model()


# class UsersURLTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.user = User.objects.create_user(username='HasNoName')
#         cls.group = Group.objects.create(
#             title='Тестовая группа',
#             slug='test',
#             description='Тестовое описание',
#         )
#         cls.post = Post.objects.create(
#             author=cls.user,
#             text='Тестовый пост',
#         )

#     def setUp(self):
#         self.guest_client = Client()
#         self.authorized_client = Client()
#         self.authorized_client.force_login(self.user)

#     def test_users_urls_is_working_200(self):
#         page_names = (
#             '/signup/',
#             '/logout/',
#             '/login/',
#             '/password_reset/',
#         )
#         for page in page_names:
#             with self.subTest(page=page):
#                 response = self.guest_client.get(page)
#                 self.assertEqual(response.status_code, 302)
