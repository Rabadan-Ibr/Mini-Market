from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase

from apps.products.models import Category, Product

User = get_user_model()


class ProductURLTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_admin = User.objects.create_user(
            username='TestUserAdmin',
            email='test@mail.ru',
        )
        cls.user_admin.is_superuser = True
        cls.user_admin.is_staff = True
        cls.user_admin.save()
        cls.user = User.objects.create_user(
            username='TestUser',
            email='test@mail.ru',
        )
        cls.category_1 = Category.objects.create(
            title='test1',
            slug='test1',
        )
        cls.product_1 = Product.objects.create(
            title='test',
            price=10,
            discount_price=9,
            balance=1,
            description='test',
            short_description='test',
            category=cls.category_1,
        )
        cls.urls_get = (
            (
                '/api/v1/categories/',
                {'guest': 200, 'user': 200, 'admin': 200},
            ),
            (
                f'/api/v1/categories/{cls.category_1.slug}/',
                {'guest': 200, 'user': 200, 'admin': 200},
            ),
            (
                f'/api/v1/categories/{cls.category_1.slug}/products/',
                {'guest': 200, 'user': 200, 'admin': 200},
            ),
            (
                '/api/v1/products/',
                {'guest': 200, 'user': 200, 'admin': 200},
            ),
            (
                f'/api/v1/products/{cls.product_1.id}/',
                {'guest': 200, 'user': 200, 'admin': 200},
            ),
            (
                '/api/v1/products/get_info/',
                {'guest': 200, 'user': 200, 'admin': 200},
            ),
        )
        cls.urls_post = (
            (
                '/api/v1/categories/',
                {'guest': 401, 'user': 403, 'admin': 201},
                {'title': 'test2', 'slug': 'test2'},
            ),
            (
                '/api/v1/categories/create_sub_category/',
                {'guest': 401, 'user': 403, 'admin': 201},
                {
                    'title': 'test2',
                    'slug': 'test3',
                    'parent': cls.category_1.slug,
                },
            ),
            (
                '/api/v1/products/',
                {'guest': 401, 'user': 403, 'admin': 201},
                {
                    'title': 'test1',
                    'price': 10,
                    'discount_price': 9,
                    'balance': 1,
                    'description': 'test',
                    'short_description': 'test',
                    'category': cls.category_1.slug,
                },
            ),
            (
                f'/api/v1/products/{cls.product_1.id}/to_cart/',
                {'guest': 401, 'user': 200, 'admin': 200},
                {},
            ),
        )

    def setUp(self):
        self.guest_client = APIClient()

        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(user=ProductURLTest.user)

        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=ProductURLTest.user_admin)
        cache.clear()

    def test_urls_guest(self):
        """Проверяем доступность страниц для не авторизованных по URL."""
        for path, codes in ProductURLTest.urls_get:
            with self.subTest(path=path):
                response = self.guest_client.get(path)
                self.assertEqual(
                    response.status_code,
                    codes['guest'],
                    f'Для {path} ожидается статус {codes["guest"]}, '
                    f'получено {response.status_code}'
                )

        for path, codes, data in ProductURLTest.urls_post:
            with self.subTest(path=path):
                response = self.guest_client.post(path, data=data)
                self.assertEqual(
                    response.status_code,
                    codes['guest'],
                    f'Для {path} ожидается статус {codes["guest"]}, '
                    f'получено {response.status_code}'
                )

    def test_urls_authorized_client(self):
        """Проверяем доступность страниц для авторизованных по URL."""
        for path, codes in ProductURLTest.urls_get:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertEqual(
                    response.status_code,
                    codes['user'],
                    f'Для {path} ожидается статус {codes["user"]}, '
                    f'получено {response.status_code}'
                )

        for path, codes, data in ProductURLTest.urls_post:
            with self.subTest(path=path):
                response = self.authorized_client.post(path, json=data)
                self.assertEqual(
                    response.status_code,
                    codes['user'],
                    f'Для {path} ожидается статус {codes["user"]}, '
                    f'получено {response.status_code}'
                )

    def test_urls_admin(self):
        """Проверяем доступность страниц для администраторов по URL."""
        for path, codes in ProductURLTest.urls_get:
            with self.subTest(path=path):
                response = self.admin_client.get(path)
                self.assertEqual(
                    response.status_code,
                    codes['admin'],
                    f'Для {path} ожидается статус {codes["admin"]}, '
                    f'получено {response.status_code}'
                )

        for path, codes, data in ProductURLTest.urls_post:
            with self.subTest(path=path):
                response = self.admin_client.post(path, data=data)
                self.assertEqual(
                    response.status_code,
                    codes['admin'],
                    f'Для {path} ожидается статус {codes["admin"]}, '
                    f'получено {response.status_code}'
                )

    def test_create_category(self):
        """ Создание категории """
        response = self.admin_client.post(
            '/api/v1/categories/', {'title': 'test2', 'slug': 'test2'}
        )
        self.assertEqual(
            response.status_code, 201, 'Не удалось создать категорию'
        )

        response = self.admin_client.get('/api/v1/categories/test2/')
        self.assertEqual(
            response.status_code,
            200,
            'Не удалось получить созданную категорию.',
        )

        slug = response.json().get('slug', '')
        self.assertEqual(
            slug,
            'test2',
            'Получена не верная категория.',
        )

    def test_create_sub_category(self):
        """ Создание подкатегории """
        response = self.admin_client.post(
            '/api/v1/categories/create_sub_category/',
            {
                'title': 'test2',
                'slug': 'test2',
                'parent': ProductURLTest.category_1.slug,
            },
        )
        self.assertEqual(
            response.status_code, 201, 'Не удалось создать подкатегорию'
        )

        try:
            category = Category.objects.get(slug='test2')
        except Category.DoesNotExist:
            raise AssertionError('Не удалось получить созданную подкатегорию.')

        self.assertEqual(
            category.parent.slug,
            ProductURLTest.category_1.slug,
            'Не верный родитель для подкатегории',
        )
