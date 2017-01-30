from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(request, items, page_size):

    paginator = Paginator(items, page_size)
    page = request.GET.get('page')

    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def redirect_or_next(request, url_name, *args, **kwargs):
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect(url_name, *args, **kwargs)
