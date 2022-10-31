'''
Tests for the tags API.
'''

from core.models import Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list')


def create_user(email='user@example.com', password='testpass123'):
    '''Create and return a user.'''
    return get_user_model(). \
        objects.create_user(email, password)  # type: ignore


class PublicTagsAPITest(TestCase):
    '''Test unauthenticated API requests.'''

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        '''Test Auth is required for retrieving tags.'''
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    '''Test authenticated API requests.'''

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        '''Test retrieving a list of tags.'''
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # res = self.client.get(path=TAGS_URL)
        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_tags_limited_to_user(self):
        '''Test list of tags is limited to authenticated user.'''
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # type: ignore
        self.assertEqual(res.data[0]['name'], tag.name)  # type: ignore
        self.assertEqual(res.data[0]['id'], tag.id)  # type: ignore