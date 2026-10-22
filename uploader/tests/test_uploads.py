import io

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from core.models import User
from uploader.models import Image
from uploader.tests.helpers import TempMediaMixin, pdf_upload, png_bytes, png_upload

IMAGES_URL = '/api/media/images/'
DOCUMENTS_URL = '/api/media/documents/'


class ImageUploadTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ana@example.com', 'senha-forte-123')
        self.client = APIClient()

    def test_anonymous_upload_is_rejected(self):
        response = self.client.post(IMAGES_URL, {'file': png_upload()}, format='multipart')

        self.assertEqual(response.status_code, 401)

    def test_authenticated_upload_records_owner(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(IMAGES_URL, {'file': png_upload()}, format='multipart')

        self.assertEqual(response.status_code, 201)
        image = Image.objects.get(attachment_key=response.data['attachment_key'])
        self.assertEqual(image.uploaded_by, self.user)
        self.assertTrue(image.file.name.endswith('.png'))

    def test_listing_images_is_not_allowed(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(IMAGES_URL)

        self.assertEqual(response.status_code, 405)

    def test_spoofed_content_type_is_rejected(self):
        self.client.force_authenticate(self.user)
        fake = SimpleUploadedFile('foto.png', png_bytes()[:8] + b'nao sou uma imagem', content_type='image/png')

        response = self.client.post(IMAGES_URL, {'file': fake}, format='multipart')

        self.assertEqual(response.status_code, 400)

    def test_pdf_disguised_as_png_is_rejected(self):
        self.client.force_authenticate(self.user)
        upload = pdf_upload('foto.png')
        upload.content_type = 'image/png'

        response = self.client.post(IMAGES_URL, {'file': upload}, format='multipart')

        self.assertEqual(response.status_code, 400)

    @override_settings(MAX_UPLOAD_SIZE=10)
    def test_oversized_image_is_rejected(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(IMAGES_URL, {'file': png_upload()}, format='multipart')

        self.assertEqual(response.status_code, 400)


class ImageModelTests(TempMediaMixin, TestCase):
    def test_image_can_be_created_from_plain_file(self):
        image = Image.objects.create(file=File(io.BytesIO(png_bytes()), name='foto.png'))

        self.assertTrue(image.file.name.endswith('.png'))


class DocumentUploadTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ana@example.com', 'senha-forte-123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_pdf_upload_records_owner(self):
        response = self.client.post(DOCUMENTS_URL, {'file': pdf_upload()}, format='multipart')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user.documents.count(), 1)

    def test_listing_documents_is_not_allowed(self):
        response = self.client.get(DOCUMENTS_URL)

        self.assertEqual(response.status_code, 405)

    @override_settings(MAX_UPLOAD_SIZE=10)
    def test_oversized_document_is_rejected(self):
        response = self.client.post(DOCUMENTS_URL, {'file': pdf_upload()}, format='multipart')

        self.assertEqual(response.status_code, 400)
