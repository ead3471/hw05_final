from django.core.paginator import Paginator, Page


def get_page(request, items, objects_per_page: int = 10) -> Page:
    """Returns Paginator Page from given HTTP request and items sequence.

    Parameters
    ---------------
    request: Django request object
    objects_list: A list, tuple, QuerySet, or other sliceable object
    with a count() or __len__() method.
    objects_per_page: The maximum number of items to include on a page,
    """
    page_number = request.GET.get('page')
    paginator = Paginator(items, objects_per_page)
    return paginator.get_page(page_number)
