import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image as PILImage

PDF_BYTES = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n'


def png_bytes():
    buffer = io.BytesIO()
    PILImage.new('RGB', (2, 2), color='red').save(buffer, format='PNG')
    return buffer.getvalue()


def png_upload(name='foto.png'):
    return SimpleUploadedFile(name, png_bytes(), content_type='image/png')


def pdf_upload(name='doc.pdf'):
    return SimpleUploadedFile(name, PDF_BYTES, content_type='application/pdf')


class TempMediaMixin:
    """Grava os uploads dos testes num diretório temporário."""

    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)
