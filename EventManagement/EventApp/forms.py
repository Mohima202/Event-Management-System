from django import forms
from .models import Participation, SNACK_ITEMS, FULL_MEAL_ITEMS, LOCATION_CHOICES

CATERING_TYPES = [
    ('none', 'None'),
    ('snacks', 'Snacks'),
    ('full', 'Full Meal'),
]

# venue mapping — update names as you like
VENUE_OPTIONS = {
    "agrabad": ["Classic world convention Hall", "Hotel Agrabad", "Abdullah convention Hall", "VIP Banquet", 
                "The Green Shadow Rasturant", "The village Rasturant", "Bir Bangali Rasturant", "Hotel Rahman & Rasturant"],
    "bohoddarhat": ["Ahad Convention Hall", "AK convention Hall", "RB convention Hall", "Hall-7 Convention center", 
                "Din Mohammad Convention Hall", "Handi Rasturant", "Barcode Food Junction", "Hotel Zaman & Rasturant"],
    "chawkbazar": ["Al-Razzaque Convention Hall", "New Shapla Banquet Hall", "City View Banquet Hall", "Blue Ocean Banquet Hall", 
            "The Food Court Rasturant", "The Tasty Treat Rasturant", "Spicy Villa Rasturant", "Hotel Sea Crown & Rasturant"],
    "gec": ["K & K Convention Hall", "Royal Garden Banquet Hall", "Grand Plaza Banquet Hall", "Sky View Banquet Hall", 
            "The Royal Feast Rasturant", "The Grand Treat Rasturant", "Spicey Treat Rasturant", "Hotel Alif & Rasturant"],
    "jamal_khan": ["JK Convention Hall", "City Heart Banquet Hall", "Sunset Banquet Hall", "Dawaat Rasturant", 
            "Royal Feast Rasturant", "Tasty Treat Rasturant", "Food Villa Rasturant", "Hotel Imperial & Rasturant"],
    "new_market": ["Elite Banquet Hall", "Majestic Banquet Hall", "Food Court Rasturant", 
            "The Royal Dine Rasturant", "Yummy Treat Rasturant", "Gourmet Villa Rasturant", "Hotel Crown & Rasturant"],
}

class ParticipationForm(forms.ModelForm):
    # Basic info (you can omit these if you want ModelForm to render them automatically)
    name = forms.CharField(max_length=100)
    email = forms.EmailField()

    # Event idea
    idea_title = forms.CharField(max_length=200, label="Event Idea Title")
    description = forms.CharField(widget=forms.Textarea)

    # Category/type (you already have choices in model, but explicit is OK)
    # Category choices remain driven by model; this is optional
    # Budget
    budget_estimate = forms.IntegerField(min_value=0, label="Budget Estimate")

    # Preferred date — optional so model null/blank works
    preferred_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    # Catering
    catering_type = forms.ChoiceField(choices=CATERING_TYPES, label="Catering Type")
    snack_items = forms.MultipleChoiceField(
        choices=SNACK_ITEMS,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Select Snack Items"
    )
    fullmeal_items = forms.MultipleChoiceField(
        choices=FULL_MEAL_ITEMS,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Select Full Meal Items"
    )

    # Location & venue
    location = forms.ChoiceField(choices=LOCATION_CHOICES, label="Location")
    venue = forms.ChoiceField(choices=[], required=False, label="Venue")

    # File upload
    file = forms.FileField(required=False)

    # Consent
    consent = forms.BooleanField(required=True, label="I agree to share my idea")

    class Meta:
        model = Participation
        # we exclude catering_items because we'll set it ourselves from snack/fullmeal
        fields = [
            'name', 'email', 'idea_title', 'description', 'category',
            'budget_estimate', 'preferred_date',
            'catering_type', 'location', 'venue',
            'file', 'consent'
        ]

    def __init__(self, *args, **kwargs):
        # allow passing an initial location so venue list is pre-populated
        super().__init__(*args, **kwargs)
        # initial venue options (based on POST or instance)
        loc = None
        if self.is_bound:
            loc = self.data.get('location')
        elif self.instance and self.instance.location:
            loc = self.instance.location

        # populate venue choices if location is known
        if loc and loc in VENUE_OPTIONS:
            self.fields['venue'].choices = [(v, v) for v in VENUE_OPTIONS[loc]]
        else:
            # keep venue optional and empty options so validation won't fail
            self.fields['venue'].choices = [('', '--- Select a Location first ---')]

    def clean(self):
        cleaned = super().clean()
        catering_type = cleaned.get("catering_type")

        snack_items = cleaned.get("snack_items") or []
        fullmeal_items = cleaned.get("fullmeal_items") or []

        if catering_type == "snacks" and not snack_items:
            raise forms.ValidationError("Select at least one snack item.")
        if catering_type == "full" and not fullmeal_items:
            raise forms.ValidationError("Select at least one full meal item.")

        # merge chosen items into a single list that will be saved into JSONField
        if catering_type == "snacks":
            cleaned["catering_items"] = snack_items
        elif catering_type == "full":
            cleaned["catering_items"] = fullmeal_items
        else:
            cleaned["catering_items"] = []

        return cleaned

    def save(self, commit=True):
      instance = super().save(commit=False)

    # Save catering items properly
      cleaned = self.cleaned_data
      instance.catering_items = cleaned.get("catering_items", [])

      if commit:
        instance.save()

      return instance

