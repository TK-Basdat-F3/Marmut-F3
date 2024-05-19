from django import template
from biru.views import format_durasi  # Gantilah `your_app_name` dengan nama aplikasi Anda

register = template.Library()

@register.filter
def durasi_format(value):
    return format_durasi(value)
