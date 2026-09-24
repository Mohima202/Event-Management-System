from django.db import models
from django.utils import timezone

CATEGORY_CHOICES = [
    ('none', 'None'),
    ('wedding', 'Marriage / Wedding'),
    ('birthday', 'Birthday Party'),
    ('anniversary', 'Anniversary Celebration'),
    ('corporate', 'Corporate Event / Office Party'),
    ('engagement', 'Engagement Ceremony'),
    ('baby_shower', 'Baby Shower'),
    ('graduation', 'Graduation Party'),
    ('housewarming', 'Housewarming / Griha Pravesh'),
    ('festival', 'Festival Event (Eid, Pohela Boishakh, Christmas, etc.)'),
    ('concert', 'Concert / Music Event'),
    ('fashion_show', 'Fashion Show / Exhibition'),
    ('workshop', 'Workshop / Seminar'),
    ('sports', 'Sports Event / Tournament'),
    ('charity', 'Charity / Fundraising Event'),
    ('farewell', 'Farewell / Welcome Party'),
]


CATERING_CHOICES = [
    ('none', 'None'),
    ('snacks', 'Snacks'),
    ('full', 'Full Meal'),
]

SNACK_ITEMS = [
    ('samosa', 'Samosa'),
    ('pakora', 'Pakora'),
    ('chotpoti', 'Chotpoti'),
    ('fuchka', 'Fuchka'),
    ('momo', 'Momo'),
    ('nacchos', 'Nachos'),
    ('chowmein', 'Chowmein'),
    ('spring roll', 'Spring Roll'),
    ('burger', 'Burger'),
    ('pizza', 'Pizza'), 
    ('shwarma', 'Shwarma'),
    ('sandwich', 'Sandwich'),
    ('french fries', 'French Fries'),
    ('chips', 'Chips'),
    ('soft drinks', 'Soft Drinks'),
    ('juice', 'Juice'),
    ('jalebi', 'Jalebi'),
    ('cake', 'Cake'),
    ('cupcake', 'Cupcake'),

]

FULL_MEAL_ITEMS = [
    ('beef biriyani', 'Beef Biriyani'),
    ('chicken biriyani', 'Chicken Biriyani'),
    ('mutton biriyani', 'Mutton Biriyani'),
    ('hyderabadi biriyani', 'Hyderabadi Biriyani'),

    ('polao', 'Polao'),
    ('kacchi', 'Kacchi'),
    ('kichuri', 'Kichuri'),
    ('fried_rice', 'Fried Rice'),
    ('mexican rice', 'Mexican Rice'),

    ('beef curry', 'Beef Curry'),
    ('beef korma', 'Beef Korma'),
    ('beef kala bhuna', 'Beef Kala Bhuna'),
    ('mutton curry', 'Mutton Curry'),
    ('mutton korma', 'Mutton Korma'),
    ('chicken curry', 'Chicken Curry'),
    ('chicken korma', 'Chicken Korma'),
    ('chicken roast', 'Chicken Roast'),

    ('rupchanda fry', 'Rupchanda Fry'),
    ('hilsha bhuna', 'Hilsha Bhuna'),
    ('lobster', 'Lobster'),
    ('prawn curry', 'Prawn Curry'),
    ('chinese vegetable', 'Chinese Vegetable'),
    ('salad', 'Salad'),

    ('soft_drinks', 'Soft Drinks'),
    ('borhani', 'Borhani'),
    ('juice', 'Juice'),
    ('dessert', 'Dessert'),
]

LOCATION_CHOICES = [
    ('none', 'None'),
    ('agrabad', 'Agrabad'),
    ('bohoddarhat', 'Bohoddarhat'),
    ('chawkbazar', 'Chawkbazar'),
    ('gec', 'GEC'),
    ('jamal_khan', 'Jamal Khan'),
    ('new_market', 'New Market'),
]

# For future dynamic venue expansion
# Each location will have multiple venue names
class Participation(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    idea_title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    budget_estimate = models.CharField(max_length=50)
    preferred_date = models.DateField()
    catering_type = models.CharField(max_length=50, blank=True, null=True)
    snack_items = models.TextField(blank=True, null=True)
    fullmeal_items = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100)
    venue = models.CharField(max_length=100)
    file = models.FileField(upload_to="participation_files/", blank=True, null=True)
    consent = models.BooleanField(default=False)

    # ===== New fields for organizer selection =====
    selected_event = models.CharField(max_length=100, blank=True, null=True)
    date_selected = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.idea_title} - {self.name}"
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# ------------------------------
# Custom User Model
# ------------------------------
class UserAccount(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('participant', 'Participant'),
    ]
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed password
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    last_login = models.DateTimeField(null=True, blank=True)
    is_logged_in = models.BooleanField(default=False)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email

# ------------------------------
# OrganizerEvent model
# ------------------------------
# models.py

class OrganizerEvent(models.Model):
    organizer_email = models.EmailField(default='unknown@example.com')  # ✅ default add
    participant_name = models.CharField(max_length=100, default='Unknown')
    participant_email = models.EmailField(default='unknown@example.com')
    category = models.CharField(max_length=50, default='none')
    idea_title = models.CharField(max_length=200, default='Untitled Idea')
    budget_estimate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    preferred_date = models.DateField(default='2026-01-01')
    location = models.CharField(max_length=100, default='Unknown')
    venue = models.CharField(max_length=100, default='Unknown')
    file = models.FileField(upload_to='organizer_files/', blank=True, null=True)
    selected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant_name} - {self.idea_title}"





from django.db import models
from .models import UserAccount

class LoginHistory(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    email = models.EmailField()
    login_time = models.DateTimeField(auto_now_add=True)  # automatically current time

    def __str__(self):
        return f"{self.email} logged in at {self.login_time}"