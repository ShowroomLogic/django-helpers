import json
from decimal import Decimal, ROUND_HALF_UP

from django import template
from django.core.urlresolvers import resolve, Resolver404

from django.template.defaultfilters import floatformat
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag(takes_context=True)
def active_path(context, path, exact=False, active_class="active", **kwargs):
    """
    TODO: This needs Documentation
    """

    is_match = False

    try:
        match = resolve(context['request'].path)

        if path.endswith(':') and match.namespace.startswith(path[:-1]):
            is_match = True
        elif path == match.namespace + ':' + match.url_name:
            is_match = True
        else:
            is_match = False

        # check kwargs
        if is_match:
            for k, v in kwargs.items():
                if k not in match.kwargs or str(match.kwargs[k]) != str(v):
                    is_match = False

    except Resolver404:
        pass

    if not is_match:
        current_path = context['request'].path
        if exact and path == current_path:
            is_match = True
        elif not exact and current_path.startswith(path):
            is_match = True
        else:
            return ''

    return active_class if is_match else ''


@register.simple_tag(takes_context=True)
def active_query(context, active_class="active", **kwargs):
    """
    TODO: Needs documentation
    """
    query_dict = context['request'].GET.copy()
    for k, v in kwargs.items():
        v = str(v)
        if k in query_dict:
            items = query_dict.getlist(k)
            if str(v) not in items:
                return ''
        elif v is not None:
            return ''
    return active_class


@register.simple_tag(takes_context=True)
def active_query_by_key(context, key, value, active_class="active"):
    """
    TODO: Needs documentation
    """
    kwargs = {}
    kwargs[key] = value
    return active_query(context, active_class=active_class, **kwargs)


@register.simple_tag(takes_context=True)
def query(context, **kwargs):
    """
    TODO: This needs Documentation
    """
    updated = context['request'].GET.copy()
    for k, v in kwargs.items():
        if v is None:
            updated.pop(k, None)
        else:
            updated[k] = v

    return updated.urlencode()


@register.simple_tag(takes_context=True)
def query_by_key(context, key, value):
    """
    TODO: This needs Documentation
    """

    kwargs = {}
    kwargs[key] = value
    return query(context, **kwargs)


@register.simple_tag(takes_context=True)
def query_toggle(context, **kwargs):
    """
    TODO: This neds Documentation
    """
    updated = context['request'].GET.copy()
    for k, v in kwargs.items():
        v = str(v)
        if k in updated:
            items = updated.getlist(k)
            if v in items:
                items.remove(v)
                updated.setlist(k, items)
            else:
                items.append(v)
                updated.setlist(k, items)
        else:
            updated[k] = v
    return updated.urlencode()


@register.simple_tag(takes_context=True)
def query_toggle_by_key(context, key, value):
    """
    TODO: This neds Documentation
    """
    kwargs = {}
    kwargs[key] = value
    return query_toggle(context, **kwargs)


@register.tag()
def query_key_exists(parser, token):
    nodelist = parser.parse(('endquery_key_exists',))
    parser.delete_first_token()

    tag_name, key_variable = token.split_contents()

    return QueryKeyExistsNode(nodelist, key_variable)


class QueryKeyExistsNode(template.Node):
    def __init__(self, nodelist, key_variable):
        self.nodelist = nodelist
        self.key_variable = template.Variable(key_variable)

    def render(self, context):
        key = self.key_variable.resolve(context)
        if len(context.request.GET.getlist(key)) > 0:
            return self.nodelist.render(context)

        return ''


@register.filter()
def percentage(value, decimal_places=2):
    if value is None or value == "":
        return ""

    return '{}%'.format(floatformat(value * 100.0, decimal_places))


@register.filter()
def currency(dollars, use_parentheses=True, include_cents=True, positive=False):
    if dollars is None or dollars == "":
        return ""

    dollars = Decimal(dollars)

    if not include_cents:
        whole_dollars = abs(int(dollars.quantize(0, ROUND_HALF_UP)))
        cents = ""
    else:
        whole_dollars = abs(int(dollars))
        cents = ("%0.2f" % dollars)[-3:]

    formatter = "${}{}"

    # Change formatter for negative numbers
    if dollars < 0.0:
        formatter = "${}{}"
        if use_parentheses:
            formatter = "(${}{})"
        elif not positive:
            formatter = "-${}{}"

    return formatter.format(intcomma(whole_dollars), cents)


@register.filter()
def intcurrency(dollars, use_parentheses=True):
    return currency(
        dollars,
        use_parentheses=use_parentheses,
        include_cents=False
    )


@register.filter()
def humanize_time(amount, units='seconds'):

    if not amount:
        return ""

    if amount < 1 and units == 'seconds':
        return "less than a second"

    INTERVALS = [1, 60, 3600, 86400, 604800, 2419200, 29030400]
    NAMES = [('second', 'seconds'),
             ('minute', 'minutes'),
             ('hour', 'hours'),
             ('day', 'days'),
             ('week', 'weeks'),
             ('month', 'months'),
             ('year', 'years')]

    result = []

    unit = list(map(lambda a: a[1], NAMES)).index(units)
    # Convert to seconds
    amount *= INTERVALS[unit]

    for i in range(len(NAMES) - 1, -1, -1):
        a = int(amount / INTERVALS[i])
        if a > 0:
            result.append("{} {}".format(a, NAMES[i][1 % a]))
            amount -= a * INTERVALS[i]

    return ", ".join(result)


@register.filter()
def to_json(value):
    """
    Mainly for debugging purposes
    """

    return json.dumps(value)
