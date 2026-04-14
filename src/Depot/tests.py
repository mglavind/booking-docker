from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from organization.models import Team, Volunteer
from .models import DepotItem, DepotBooking


class DepotItemTestCase(TestCase):
    """Test cases for DepotItem model."""

    def setUp(self):
        """Set up test data."""
        self.item = DepotItem.objects.create(
            name="Test Item",
            description="Test Description",
            quantity=10
        )

    def test_item_creation(self):
        """Test that a DepotItem can be created."""
        self.assertEqual(self.item.name, "Test Item")
        self.assertEqual(self.item.quantity, 10)
        self.assertIsNotNone(self.item.created)

    def test_item_str(self):
        """Test the string representation of DepotItem."""
        self.assertEqual(str(self.item), "Test Item")

    def test_available_quantity_no_bookings(self):
        """Test available quantity with no bookings."""
        available = self.item.available_quantity()
        self.assertEqual(available, 10)

    def test_available_quantity_with_approved_booking(self):
        """Test available quantity with an approved booking."""
        volunteer = Volunteer.objects.create_user(username='testuser', first_name='Test', last_name='Volunteer', email='test@example.com')
        team = Team.objects.create(name='Test Team')

        now = timezone.now()
        booking = DepotBooking.objects.create(
            item=self.item,
            team=team,
            team_contact=volunteer,
            quantity=3,
            start=now,
            end=now + timedelta(days=1),
            status='Approved'
        )

        available = self.item.available_quantity(now, now + timedelta(days=1))
        self.assertEqual(available, 7)

    def test_available_quantity_with_pending_booking(self):
        """Test available quantity considers pending bookings."""
        volunteer = Volunteer.objects.create_user(username='testuser', first_name='Test', last_name='Volunteer', email='test@example.com')
        team = Team.objects.create(name='Test Team')

        now = timezone.now()
        booking = DepotBooking.objects.create(
            item=self.item,
            team=team,
            team_contact=volunteer,
            quantity=4,
            start=now,
            end=now + timedelta(days=1),
            status='Pending'
        )

        available = self.item.available_quantity(now, now + timedelta(days=1))
        self.assertEqual(available, 6)

    def test_available_quantity_ignores_rejected_bookings(self):
        """Test that rejected bookings don't affect available quantity."""
        volunteer = Volunteer.objects.create_user(username='testuser', first_name='Test', last_name='Volunteer', email='test@example.com')
        team = Team.objects.create(name='Test Team')

        now = timezone.now()
        booking = DepotBooking.objects.create(
            item=self.item,
            team=team,
            team_contact=volunteer,
            quantity=5,
            start=now,
            end=now + timedelta(days=1),
            status='Rejected'
        )

        available = self.item.available_quantity(now, now + timedelta(days=1))
        self.assertEqual(available, 10)


class DepotBookingTestCase(TestCase):
    """Test cases for DepotBooking model."""

    def setUp(self):
        """Set up test data."""
        self.volunteer = Volunteer.objects.create_user(username='testuser', first_name='Test', last_name='Volunteer', email='test@example.com')
        self.team = Team.objects.create(name='Test Team')
        self.item = DepotItem.objects.create(
            name="Test Item",
            quantity=10
        )
        self.now = timezone.now()

    def test_booking_creation(self):
        """Test that a DepotBooking can be created."""
        booking = DepotBooking.objects.create(
            item=self.item,
            team=self.team,
            team_contact=self.volunteer,
            quantity=5,
            start=self.now,
            end=self.now + timedelta(days=1),
            status='Pending'
        )
        self.assertEqual(booking.quantity, 5)
        self.assertEqual(booking.status, 'Pending')

    def test_booking_str(self):
        """Test the string representation of DepotBooking."""
        booking = DepotBooking.objects.create(
            item=self.item,
            team=self.team,
            team_contact=self.volunteer,
            quantity=5,
            start=self.now,
            end=self.now + timedelta(days=1),
            status='Pending'
        )
        expected_str = f"{self.item.name} - {self.team.name} (Pending)"
        self.assertEqual(str(booking), expected_str)

    def test_booking_status_color(self):
        """Test status color mapping."""
        booking = DepotBooking.objects.create(
            item=self.item,
            team=self.team,
            team_contact=self.volunteer,
            quantity=5,
            start=self.now,
            end=self.now + timedelta(days=1),
            status='Approved'
        )
        self.assertEqual(booking.get_status_display_color(), 'success')

    def test_is_overbooked(self):
        """Test overbooking detection."""
        # Create a booking that takes 8 units
        booking1 = DepotBooking.objects.create(
            item=self.item,
            team=self.team,
            team_contact=self.volunteer,
            quantity=8,
            start=self.now,
            end=self.now + timedelta(days=1),
            status='Approved'
        )

        # Create a second booking that overlaps and would take 5 units
        # This should be overbooked (8 + 5 = 13 > 10)
        booking2 = DepotBooking.objects.create(
            item=self.item,
            team=self.team,
            team_contact=self.volunteer,
            quantity=5,
            start=self.now + timedelta(hours=6),
            end=self.now + timedelta(hours=12),
            status='Pending'
        )

        self.assertTrue(booking2.is_overbooked())

