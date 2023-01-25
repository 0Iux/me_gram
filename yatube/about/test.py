# from django.test import TestCase, Client


# class StaticPagesURLTests(TestCase):
#     def setUp(self):
#         self.guest_client = Client()

#     def test_about_url_exists_at_desired_location(self):
#         """Проверка доступности адреса /about/."""
#         pages = ('/author/', '/tech/')
#         for page in pages:
#             with self.subTest(page=page):
#                 response = self.guest_client.get(page)
#                 self.assertEqual(response.status_code, 200)

#     def test_about_url_uses_correct_template(self):
#         """Проверка шаблона для адреса /about/."""
#         pages = {
#             '/author/': 'about/author.html',
#             '/tech/': 'about/tech.html'
#         }
#         for url, template in pages.items():
#             response = self.guest_client.get(url)
#             self.assertTemplateUsed(response, template)
