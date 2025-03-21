# from django.test import TestCase, Client
# from django.urls import reverse
# from showings.models import Showing, Movie, Location

# class ShowingViewsTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         # Create test data
#         self.movie = Movie.objects.create(title="Test Movie")
#         self.location = Location.objects.create(
#             city="Test City",
#             name="Test Cinema",
#             address="Test Address"
#         )
        
#     def test_get_active_showings(self):
#         # Test with no showings
#         response = self.client.get(reverse('active'))
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("No active showings", response.content.decode())

#         # Create an active showing
#         showing = Showing.objects.create(
#             movie=self.movie,
#             location=self.location,
#             is_showing=True
#         )
        
#         # Test with active showing
#         response = self.client.get(reverse('active'))
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(self.movie.title, response.content.decode()) 