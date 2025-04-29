def page_identifier(request):
    return {
        'page_identifier': request.path.replace("/", "_") # can be changed if duplicates? shouldnt be...
    }
