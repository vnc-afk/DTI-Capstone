from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string



class FormSubmissionMixin:
    def form_invalid(self, form):
        print("=== FORM_INVALID CALLED ===")
        print(f"All form errors: {form.errors}")

        # Add error messages to Django messages
        for field, error_list in form.errors.items():
            for error in error_list:
                if field == '__all__':
                    messages.error(self.request, f"{error}")
                else:
                    field_name = field.replace('_', ' ').title()
                    messages.error(self.request, f"{field_name}: {error}")

        # ✅ If AJAX, return rendered HTML for the alerts container
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages_html = render_to_string(
                "documents/partials/alerts_container.html",
                {"messages": messages.get_messages(self.request)},
                request=self.request
            )
            return JsonResponse({'success': False, 'messages_html': messages_html}, status=400)

        # Fallback for normal requests
        return super().form_invalid(form)
