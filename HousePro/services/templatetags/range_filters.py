from django import template

register = template.Library()

@register.filter
def range_filter(value):
    return range(value) if value else []