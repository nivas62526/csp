import unittest
import json
from app import app
from database import init_db

class ADConnectCleanTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        init_db(clean=True)

    def setUp(self):
        self.client = app.test_client()

    def test_1_homepage_clean(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ADCONNECT', response.data)
        self.assertIn(b'Hire Elite Creators', response.data)

    def test_2_customer_registration_and_login(self):
        # Register customer
        cust_payload = {
            'full_name': 'Sarah Brand Lead',
            'email': 'sarah.client@brand.com',
            'password': 'password123',
            'role': 'customer',
            'company_name': 'Apex Energy Ltd',
            'location': 'New York, USA'
        }
        res_reg = self.client.post('/register', data=cust_payload, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)
        self.assertIn(b'Customer Dashboard', res_reg.data)
        self.assertIn(b'Sarah Brand Lead', res_reg.data)

        # Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)

        # Login back
        res_login = self.client.post('/login', data={
            'email': 'sarah.client@brand.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Sarah Brand Lead', res_login.data)

    def test_3_creator_registration_and_workflow(self):
        # Register creator
        creat_payload = {
            'full_name': 'David Motion 3D',
            'email': 'david.creator@motion.io',
            'password': 'creatorpass123',
            'role': 'creator',
            'company_name': 'David VFX Studios',
            'location': 'London, UK'
        }
        res_reg = self.client.post('/register', data=creat_payload, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)
        self.assertIn(b'Creator Studio', res_reg.data)

        # Upload portfolio video
        vid_payload = {
            'action': 'add',
            'title': 'Cyber Car Reveal - 3D Commercial',
            'category': '3D Animation',
            'description': 'Full CGI sports car launch commercial.',
            'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
            'duration': '0:30'
        }
        res_vid = self.client.post('/creator/portfolio', data=vid_payload, follow_redirects=True)
        self.assertEqual(res_vid.status_code, 200)
        self.assertIn(b'Cyber Car Reveal', res_vid.data)

    def test_4_admin_login(self):
        res_admin = self.client.post('/login', data={
            'email': 'admin@adconnect.com',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn(b'Admin Panel', res_admin.data)
        self.assertIn(b'Total Customers', res_admin.data)

if __name__ == '__main__':
    unittest.main()
