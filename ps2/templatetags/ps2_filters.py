from django import template

register = template.Library()


@register.filter(name='isbytezero', is_safe=False)
def isbytezero(value, arg):
    return (int(value) // 2 ** int(arg, 16)) % 2 == 0
