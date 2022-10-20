from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def handler_403(request, exception):
    return render(request, 'core/403.html')


def handler_500(request):
    return render(request, 'core/500.html')
