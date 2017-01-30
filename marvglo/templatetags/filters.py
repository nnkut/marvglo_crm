from django import template

register = template.Library()


@register.filter(name='at')
def at(l, idx):
    try:
        return l[idx]
    except IndexError:
        return None