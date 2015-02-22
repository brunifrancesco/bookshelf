from functools import wraps
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.shortcuts import redirect

from Core.services import get_book_by_name


def book_details(view_func):
    """
    Return the specified book object, given a name.

    Keyword arguments:
    @param view_func: the the wrapped controller method
    """
    @wraps(view_func)
    def _get_book(request, *args, **kwargs):
        if not isinstance(request.user, AnonymousUser):
            book = get_book_by_name(kwargs["name"], request.user)
            if book:
                return view_func(request, kwargs["name"], book)
            return render(request, "404.html", status=404)
        return redirect("/")
    return _get_book
