from django.contrib import admin
from .models import Participation, OrganizerEvent, UserAccount,LoginHistory

# ---------------- OrganizerEvent Admin ----------------
@admin.register(OrganizerEvent)
class OrganizerEventAdmin(admin.ModelAdmin):
    list_display = (
        'participant_name',
        'participant_email',
        'category',
        'idea_title',
        'budget_estimate',
        'preferred_date',
        'location',
        'venue',
        'organizer_email',  # Correct field name
        'selected_at'
    )
    list_filter = (
        'category',
        'preferred_date',
        'organizer_email',  # Correct field name
    )
    search_fields = ('participant_name', 'idea_title', 'organizer_email')

# ❌ Remove this line: admin.site.register(OrganizerEvent, OrganizerEventAdmin)


# UserAccount admin
@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'password')  # password hash dekhabe
    readonly_fields = ('password',)  # plain text edit hobena
    search_fields = ('email', 'role')
    list_filter = ('role',)

    def save_model(self, request, obj, form, change):
        if not change:  # new user
            obj.set_password(obj.password)
        else:  # existing user edited
            old_obj = UserAccount.objects.get(pk=obj.pk)
            if old_obj.password != obj.password:
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

# LoginHistory admin
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'login_time', 'get_hashed_password')
    search_fields = ('email', 'user__email')
    list_filter = ('login_time',)

    def get_hashed_password(self, obj):
        return obj.user.password  # hashed password show korbe
    get_hashed_password.short_description = "Hashed Password"


# ---------------- Participation Admin ----------------
@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('idea_title', 'name', 'email', 'category', 'preferred_date')
    search_fields = ('idea_title', 'name', 'email', 'category')
    list_filter = ('category', 'preferred_date')
