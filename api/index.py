import os
import sys

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_backend.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import connection

# Ensure runtime SQLite tables exist
try:
    existing_tables = connection.introspection.table_names()
    if 'auth_user' not in existing_tables:
        call_command('migrate', interactive=False)
        
        # Seed initial admin & sample books if empty
        from django.contrib.auth.models import User
        from library.models import Student, Author, Book
        
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@amrita.edu', 'admin')
            Student.objects.create(
                user=admin_user,
                name='Central Library Admin',
                roll_no='ADMIN001',
                email='admin@amrita.edu',
                department='ADMIN',
                role=Student.ROLE_SUPER_ADMIN,
                is_active=True
            )
            
        if Book.objects.count() == 0:
            a1, _ = Author.objects.get_or_create(name="Thomas H. Cormen", defaults={"bio": "Computer Scientist"})
            a2, _ = Author.objects.get_or_create(name="Andrew S. Tanenbaum", defaults={"bio": "Operating Systems & Networking"})
            a3, _ = Author.objects.get_or_create(name="Robert C. Martin", defaults={"bio": "Software Engineering"})
            Book.objects.create(title="Introduction to Algorithms", author=a1, category="Computer Science", total_copies=5, available_copies=5, description="CLRS algorithms textbook.")
            Book.objects.create(title="Computer Networks", author=a2, category="Networking", total_copies=4, available_copies=4, description="Principles of network protocols.")
            Book.objects.create(title="Clean Code", author=a3, category="Software Engineering", total_copies=3, available_copies=3, description="A handbook of agile software craftsmanship.")
except Exception as e:
    print(f"Startup initialization note: {e}")

from library_backend.wsgi import application

app = application
