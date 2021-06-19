from django.test import TestCase
import unittest
from django.test import Client

class MainPageGetTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        response_analysis = self.client.get('/analysis/')
        # Check that the response is 200 OK.
        self.assertEqual(response_analysis.status_code, 200)