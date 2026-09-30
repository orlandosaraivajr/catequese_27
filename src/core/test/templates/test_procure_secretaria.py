from django.test import TestCase, Client
from django.shortcuts import resolve_url as r
from http import HTTPStatus

class ProcureSecretariaGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.resp = self.client.get(r('core:procure_secretaria'))

    def test_status_code(self):
        self.assertEqual(self.resp.status_code, HTTPStatus.OK)

    def test_template_used(self):
        self.assertTemplateUsed(self.resp, 'procure_secretaria.html')
