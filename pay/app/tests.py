import jwt
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import *


class ProductSearchViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='a@A.com', phone='010-9876-5432',
                                             password='testpass')
        self.product1 = PRODUCT.objects.create(name='Test product 1', user=self.user)
        self.product2 = PRODUCT.objects.create(name='Test product 2', user=self.user)
        self.product3 = PRODUCT.objects.create(name='Other product', user=self.user)

        jwt_token = jwt.encode({'username': 'testuser'}, settings.SECRET_KEY, algorithm='HS256')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_token}')

    def test_product_search(self):
        url = reverse('product-search')

        response = self.client.get(url, {'query': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(response.data['data']), 2)
        self.assertEqual(response.data['data'][0]['name'], 'Test product 2')
        self.assertEqual(response.data['data'][1]['name'], 'Test product 1')

        response = self.client.get(url, {'query': 'Other'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Other product')

    def test_invalid_token(self):
        url = reverse('product-search')
        response = self.client.get(url, {'query': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['meta']['message'], '잘못된 토큰 입니다..')
        self.assertIsNone(response.data['data'])
