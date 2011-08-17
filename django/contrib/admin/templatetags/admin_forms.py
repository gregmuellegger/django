from django import forms
from django.template import Library


register = Library()


@register.filter
def is_checkbox(bound_field):
    if bound_field is None:
        return False
    return isinstance(bound_field.field.widget, forms.CheckboxInput)
