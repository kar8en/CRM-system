from django import forms

class CustomClearableFileInput(forms.ClearableFileInput):
    template_with_initial = (
        '%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a> '
        '%(input_text)s: %(input)s'
    )

    template_with_clear = '' 

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['initial'] = value if value else ''  # Имя файла
        return context
