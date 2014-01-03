from django.template import Library

register = Library()

@register.filter(name="range")
def _range(value):
  return range(value)