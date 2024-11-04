def AuthorizeMiddleware(get_response):
    def middleware(request):
        if str(request.get_full_path()).startswith("/api"):
            print("API request")
        return get_response(request)
    return middleware