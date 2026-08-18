from django import template

register = template.Library()



@register.filter
def ua_plural(count, forms):
    try:
        count = int(count)
    except (TypeError, ValueError):
        return ""
 
    forms_list = [f.strip() for f in forms.split(",")]
    if len(forms_list) != 3:
        return forms_list[0] if forms_list else ""
 
    singular, few, many = forms_list
 
    n = abs(count) % 100
    n1 = n % 10
 
    if 11 <= n <= 14:
        return many
    if n1 == 1:
        return singular
    if 2 <= n1 <= 4:
        return few
    return many
 