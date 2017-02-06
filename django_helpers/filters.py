from django.db.models import Q
from django.http.request import QueryDict
import django_filters


class DefaultFilterSet(django_filters.FilterSet):
    def __init__(self, data=None, queryset=None, prefix=None, strict=None):
        
        if hasattr(self, 'Meta'):
            defaults = getattr(self.Meta, 'defaults', {})

            if isinstance(data, QueryDict):
                data = data.copy()
                for key, value in defaults.items():
                    if isinstance(value, (list, tuple)):
                        data.setlistdefault(key, value)
                    else:
                        data.setdefault(key, value)
            else:
                data = dict(defaults, **data)

        super(DefaultFilterSet, self).__init__(data, queryset, prefix, strict)


class TagFilter(django_filters.Filter):
    
    def __init__(self, *args, **kwargs):
        # Get the action out of the kwargs
        self.tag_field = kwargs.pop('tag_field', 'tags')

        # Call the parent
        super(TagFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        
        # This is a really dumb thing we have to do to get
        # access to multiple values
        if isinstance(self.parent.data, QueryDict):
            value = self.parent.data.getlist(self.name, [])

        if not isinstance(value, (list, tuple)):
            value = [value]

        if not value or value == ['']:
            return qs

        kwargs = {
            "{}__slug__in".format(self.tag_field): value
        }
        return qs.filter(**kwargs)


class SearchFilter(django_filters.Filter):
    
    def __init__(self, search_fields, exact=True, *args, **kwargs):
        # Get the action out of the kwargs
        self.search_fields = search_fields
        self.exact = exact

        # Call the parent
        super(SearchFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        
        if self.exact:
            terms = [value]
        else:
            terms = value.split()

        for term in terms:
            filter = Q(**{self.search_fields[0]: term})
            for field in self.search_fields[1:]:
                filter |= Q(**{field: term})

            if value and filter:
                qs = qs.filter(filter)
    
        return qs


def get_filter_value_list(data, key, is_int=False):
    """
    Get a list of values from a QueryDict (or string or list/tuple).
    This function supports both plain lists of values and values that are
    comma separated values. For example: '1,2,3' or [1,2,3] or ['1,2,3', '4'].
    When is_int == True then all the values will be cast to an int. If the values
    are not ints they will be ignored (in order to avoid nasty excpetions in the api).
    """

    raw_value = []
    if isinstance(data, QueryDict):
        raw_value = data.getlist(key, [])
    elif not isinstance(data, (list, tuple)):
        raw_value = data.split(',')
    else:
        raw_value = data

    value = []
    for v in raw_value:
        if v:
            for vv in v.split(','):
                if vv:
                    if is_int:
                        try:
                            value.append(int(vv))
                        except ValueError:
                            pass  # If it's not an int ignore it nicely
                    else:
                        value.append(vv)

    if not value or value == ['']:
        value = None

    return value
