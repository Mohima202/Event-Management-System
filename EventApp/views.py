from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import UserAccount, OrganizerEvent, LoginHistory, Participation
from .forms import ParticipationForm


# =====================================================
# HOME
# =====================================================
# =====================================================
# HOME (DASHBOARD NUMBERS FIXED)
# =====================================================
def home(request):

    # 🔢 Total selected events (Organizer approved)
    total_events = OrganizerEvent.objects.count()

    # 📅 Today date
    today = timezone.now().date()

    # ⏳ Upcoming events (future date)
    upcoming_events = OrganizerEvent.objects.filter(
        preferred_date__gt=today
    ).count()

    # ✅ Completed events (past date)
    completed_events = OrganizerEvent.objects.filter(
        preferred_date__lt=today
    ).count()

    # 🕒 Pending requests (not selected yet)
    pending_requests = Participation.objects.filter(
        selected_event__isnull=True
    ).count()

    # 🆕 Recent events (last 5 selected)
    recent_events = OrganizerEvent.objects.order_by('-selected_at')[:5]

    context = {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'completed_events': completed_events,
        'pending_requests': pending_requests,
        'recent_events': recent_events,
    }

    return render(request, "homepage.html", context)

# =====================================================
# REGISTER
# =====================================================
def register(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not email or not password or not role:
            messages.error(request, "All fields are required")
            return redirect('register')

        if UserAccount.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('login')

        user = UserAccount(email=email, role=role)
        user.set_password(password)  # hash password
        user.save()

        messages.success(request, "Registration successful")
        return redirect('login')

    return render(request, "register.html")


# =====================================================
# LOGIN
# =====================================================
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')

        try:
            user = UserAccount.objects.get(email=email)

            if user.check_password(password):
                # session store
                request.session['user_id'] = user.id
                request.session['role'] = user.role

                # update LoginHistory
                LoginHistory.objects.create(
                    user=user,
                    email=email
                )

                # update last login
                user.last_login = timezone.now()
                user.is_logged_in = True
                user.save()

                # redirect based on role
                if user.role == 'organizer':
                    return redirect('organizer')
                elif user.role == 'participant':
                    return redirect('p_event')
                else:
                    return redirect('home')

            else:
                messages.error(request, "Invalid email or password")

        except UserAccount.DoesNotExist:
            messages.error(request, "Invalid email or password")

        return redirect('login')

    return render(request, "login.html")
# =====================================================
# LOGOUT
# =====================================================
def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('login')


# =====================================================
# ORGANIZER PAGE (SELECT SUBMISSIONS)
# =====================================================
def organizer(request):
    if not request.session.get('user_id'):
        return redirect('login')

    if request.session.get('role') != 'organizer':
        messages.error(request, "Access denied")
        return redirect('login')

    participations = Participation.objects.filter(selected_event__isnull=True).order_by('-id')

    if request.method == "POST":
        participation_id = request.POST.get("participation_id")
        participation = get_object_or_404(Participation, id=participation_id)

        organizer_user = UserAccount.objects.get(id=request.session['user_id'])

        # Save into OrganizerEvent table
        OrganizerEvent.objects.create(
            organizer_email=organizer_user.email,  # Organizer email
            participant_name=participation.name,
            participant_email=participation.email,
            idea_title=participation.idea_title,
            category=participation.category,
            budget_estimate=participation.budget_estimate or 0.0,
            preferred_date=participation.preferred_date,
            location=participation.location,
            venue=participation.venue,
            file=participation.file
        )

        # Mark participation as selected
        participation.selected_event = participation.idea_title
        participation.date_selected = timezone.now()
        participation.save()

        messages.success(request, f"'{participation.idea_title}' selected successfully!")
        # ✅ Redirect to organizer_panel immediately
        return redirect('organizer_panel')

    return render(request, "organizer.html", {'participations': participations})



# =====================================================
# PARTICIPANT VIEW EVENTS
# =====================================================
def p_event(request):
    if not request.session.get('user_id'):
        return redirect('login')

    if request.session.get('role') != 'participant':
        messages.error(request, "Access denied")
        return redirect('login')

    events = OrganizerEvent.objects.all().order_by('-selected_at')
    return render(request, "P_Event.html", {'events': events})


# =====================================================
# PARTICIPATION FORM
# =====================================================
def participate(request):
    if request.method == "POST":
        form = ParticipationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Submission successful")
            return redirect('p_event')
    else:
        form = ParticipationForm()

    return render(request, "participate.html", {'form': form})

def organizer_panel(request):
    if not request.session.get('user_id'):
        return redirect('login')
    if request.session.get('role') != 'organizer':
        messages.error(request, "Access denied")
        return redirect('login')

    organizer_user = UserAccount.objects.get(id=request.session['user_id'])

    submissions = OrganizerEvent.objects.filter(
        organizer_email=organizer_user.email
    ).order_by('id')

    # Clean category (remove extra spaces, lowercase)
    for sub in submissions:
        if sub.category:
            sub.category_clean = sub.category.strip().lower()
        else:
            sub.category_clean = ''

    return render(request, 'organizer_panel.html', {'submissions': submissions})
