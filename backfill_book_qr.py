# -*- coding: utf-8 -*-
import os, django, uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_backend.settings')
django.setup()

from library.models import Book

books = Book.objects.all()
for b in books:
    b.qr_uid = uuid.uuid4()
    b.qr_image = None # Force image generation
    b.save()
print(f"Done backfilling QR UIDs for {books.count()} books.")
