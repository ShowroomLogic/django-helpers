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
