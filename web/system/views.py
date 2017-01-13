from django.shortcuts import render


def page_404_handler(request):
    return render(request, template_name='404.html', status=404)
