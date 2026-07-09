import os
import django
import json
from django.test import Client
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_backend.settings')
django.setup()

from library.models import Student
from django.contrib.auth.models import User

def test_barcode_login():
    client = Client()
    
    # Create a test student
    username = "test_student_barcode_v2"
    roll_no = "CH.SC.U4CSE24125"
    
    try:
        user, _ = User.objects.get_or_create(username=username)
        student, _ = Student.objects.get_or_create(
            user=user,
            roll_no=roll_no,
            defaults={'name': 'Test Student', 'email': 'test2@example.com'}
        )
        
        print(f"Testing Barcode Login for roll number: {roll_no}")
        
        # Test successful login
        payload = {"roll_number": roll_no}
        response = client.post('/api/barcode-login/', data=json.dumps(payload), content_type='application/json')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Token received.")
            student.refresh_from_db()
            print(f"Login Method: {student.login_method}")
            print(f"Last Login: {student.last_id_card_login}")
            
            if student.login_method == Student.LOGIN_METHOD_ID_CARD and student.last_id_card_login:
                print("✅ Student model fields updated correctly.")
        else:
            print(f"❌ Failed! Status Code: {response.status_code}")
            print(response.content.decode())

        # Test failure (invalid roll number)
        payload = {"roll_number": "INVALID.ROLL"}
        response = client.post('/api/barcode-login/', data=json.dumps(payload), content_type='application/json')
        if response.status_code == 404:
            print("✅ Correctly rejected invalid roll number (404).")
        else:
            print(f"❌ Error handling failed for invalid roll number. Status: {response.status_code}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_barcode_login()
