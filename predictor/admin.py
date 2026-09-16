from django.contrib import admin
from .models import SignupRequest
from django.utils.html import format_html

@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_approved', 'approve_button')

    def approve_button(self, obj):
        if not obj.is_approved:
            return format_html(
                '<a style="color:green; font-weight:bold;" href="/approve/{}/">Approve</a>',
                obj.id
            )
        return "✅ Approved"