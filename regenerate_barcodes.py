import os
import django
import uuid
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_backend.settings')
django.setup()

from library.models import Student, Book, BookCopy

def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalnum() or c in (' ', '.', '_')]).strip().replace(' ', '_')

def regenerate_student_barcodes():
    print("Regenerating Student Barcodes...")
    COD128 = barcode.get_barcode_class('code128')
    writer = ImageWriter()
    writer.set_options({'module_height': 5.0, 'font_size': 0, 'text_distance': 0})
    
    students = Student.objects.all()
    for s in students:
        if s.roll_no:
            print(f"  - Barcode for {s.name} ({s.roll_no})")
            barcode_instance = COD128(s.roll_no, writer=writer)
            buffer = BytesIO()
            barcode_instance.write(buffer)
            
            safe_name = sanitize_filename(s.name)
            filename = f"user_barcode_{safe_name}_{s.roll_no}.png"
            s.qr_image.save(filename, File(buffer), save=False)
            Student.objects.filter(pk=s.pk).update(qr_image=s.qr_image)

def regenerate_book_barcodes():
    print("Regenerating Book Barcodes...")
    COD128 = barcode.get_barcode_class('code128')
    writer = ImageWriter()
    writer.set_options({'module_height': 5.0, 'font_size': 0})
    
    books = Book.objects.all()
    for b in books:
        print(f"  - Barcode for {b.title}")
        barcode_instance = COD128(f"BOOK:{str(b.qr_uid)[:12]}", writer=writer)
        buffer = BytesIO()
        barcode_instance.write(buffer)
        
        safe_title = sanitize_filename(b.title)
        filename = f"book_barcode_{safe_title}_{str(b.qr_uid)[:8]}.png"
        b.qr_image.save(filename, File(buffer), save=False)
        Book.objects.filter(pk=b.pk).update(qr_image=b.qr_image)

def regenerate_copy_barcodes():
    print("Regenerating BookCopy Barcodes...")
    COD128 = barcode.get_barcode_class('code128')
    writer = ImageWriter()
    writer.set_options({'module_height': 5.0, 'font_size': 0})
    
    copies = BookCopy.objects.all().select_related('book')
    for c in copies:
        print(f"  - Barcode for {c.book.title} (UID: {str(c.copy_uid)[:8]})")
        barcode_instance = COD128(f"COPY:{str(c.copy_uid)[:12]}", writer=writer)
        buffer = BytesIO()
        barcode_instance.write(buffer)
        
        safe_title = sanitize_filename(c.book.title)
        filename = f"copy_barcode_{safe_title}_{str(c.copy_uid)[:8]}.png"
        c.qr_image.save(filename, File(buffer), save=False)
        BookCopy.objects.filter(pk=c.pk).update(qr_image=c.qr_image)

if __name__ == "__main__":
    regenerate_student_barcodes()
    regenerate_book_barcodes()
    regenerate_copy_barcodes()
    print("Done!")
