from django import template
register = template.Library()

@register.filter
def eq(value, arg):
    # Handle string comparison carefully in templates if needed (e.g. integer vs string)
    # Django templates usually convert, but explicit casting might be safer if types mismatched
    # For now, standard equality
    if str(value) == str(arg):
        return True
    return value == arg
