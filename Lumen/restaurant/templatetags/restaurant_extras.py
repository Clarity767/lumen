from django import template

register = template.Library()

@register.filter
def uk_plural(count, forms):
    """
    Usage: {{ count|uk_plural:"відгук,відгуки,відгуків" }}
    """
    forms = forms.split(',')
    count = abs(int(count))
    if 11 <= count % 100 <= 19:
        return forms[2]
    elif count % 10 == 1:
        return forms[0]
    elif 2 <= count % 10 <= 4:
        return forms[1]
    else:
        return forms[2]