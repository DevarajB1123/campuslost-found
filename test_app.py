import unittest
from app import app
from database import get_db

class CampusLostAndFoundTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Campus', response.data)
        self.assertIn(b'Lost', response.data)

    def test_browse_page(self):
        response = self.client.get('/browse')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Directory', response.data)

    def test_item_detail(self):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM items LIMIT 1")
        row = cur.fetchone()
        conn.close()
        item_id = row['id'] if row else 1
        response = self.client.get(f'/item/{item_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Report #', response.data)
        self.assertIn(b'Category', response.data)

    def test_campus_map(self):
        response = self.client.get('/map')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Central Library', response.data)

    def test_duplicate_check_api(self):
        response = self.client.post('/api/check-duplicates', json={
            'title': 'Hydro Flask Water Bottle',
            'category': 'Bottles & Tumblers',
            'type': 'LOST',
            'location': 'Main Canteen / Food Court'
        })
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('duplicates', json_data)
        self.assertTrue(len(json_data['duplicates']) > 0)

    def test_user_login_and_smart_matches(self):
        # Quick login as student Alex Chen
        response = self.client.get('/quick-login/alex', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Smart matches
        match_res = self.client.get('/matches')
        self.assertEqual(match_res.status_code, 200)
        self.assertIn(b'Smart Item Matching Radar', match_res.data)

        # Claims hub
        claims_res = self.client.get('/claims')
        self.assertEqual(claims_res.status_code, 200)

    def test_admin_dashboard(self):
        # Quick login as admin
        response = self.client.get('/quick-login/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Admin panel
        admin_res = self.client.get('/admin')
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn(b'Platform Moderation', admin_res.data)

    def test_google_maps_api_endpoints(self):
        # Test map markers endpoint
        res = self.client.get('/api/map-markers')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('center', data)
        self.assertIn('buildings', data)
        self.assertIn('items', data)
        self.assertTrue(len(data['buildings']) > 0)
        self.assertTrue(len(data['items']) > 0)

        # Test set maps key endpoint
        key_res = self.client.post('/api/set-maps-key', json={'api_key': 'AIzaSyDemoTestKey123'})
        self.assertEqual(key_res.status_code, 200)
        self.assertTrue(key_res.get_json()['success'])

if __name__ == '__main__':
    unittest.main()
