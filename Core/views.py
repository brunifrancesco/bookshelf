from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from Core.services import create_user
from Core.services import ensure_login
from Core.services import add_book
from Core.services import get_books_by_user
from Core.services import delete_book
from Core.decorators import book_details
from Core.services import get_insights
from Core.services import filter_books_by_data
from Core.services import get_books_by_user_author
import json


def index(request):
    """
    Show index view

    Keyword arguments:
    @param request: the incoming request
    """
    return render(request, "index.html")


def login(request):
    """
    Log user in and show message via django messages middleware if login fails

    Keyword arguments:
    @param request: the incoming request
    """
    user = ensure_login(request.POST)
    if user:
        return _set_expire_and_redirect(user, request)
    else:
        messages.add_message(request, messages.INFO, 'User/password wrong. Please sign up.')
        return redirect("/signup?login_failed=True")


def logout(request):
    """
    Log user out

    Keyword arguments:
    @param request: the incoming request
    """
    auth_logout(request)
    return redirect("/")


def signup(request, login_failed=False):
    """
    Sign user up.
    Handle a previous login failed effort.

    Keyword arguments:
    @param request: the incoming request
    """
    if request.method == 'POST' and not "login_failed" in request.GET:
        user = create_user(request.POST)
        return _set_expire_and_redirect(user, request)
    else:
        return render(request, "index.html", {'signup': True})


def _set_expire_and_redirect(user, request):
    """
    Set rememeber me cookie, given a user

    Keyword arguments:
    @param request: the incoming request
    @param user: the user whose rememeber me cookies need to be persisted
    """
    user.backend = 'mongoengine.django.auth.MongoEngineBackend'
    auth_login(request, user)
    request.session.set_expiry(240 * 60 * 1)
    return redirect("/")


def book(request):
    """
    Handle new book insert/retrieving

    Keyword arguments:
    @param request: the incoming request
    """
    if request.method == "POST":
        if "isbn" in request.POST and request.POST["isbn"]:
            result = add_book(request.user, request.POST)
            if result:
                data = dict(zip(["books", "authors", "genres", "reads_dates", "reads_values", "titles"], result))
                print data
                return render(request, "books.html", data)
            return HttpResponse("Unexpected error", status=500)
        return HttpResponse("Missing values", status=400)
    elif request.method == "GET":
        data = dict(zip(["books", "authors", "genres", "reads_dates", "reads_values", "titles"], get_books_by_user(request.user)))
        return render(request, "books.html", data)
    else:
        return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def filter(request):
    if request.method == "POST":
        if not request.user:
            return HttpResponse("Forbidden", status=403)
        authors = [request.POST[key].encode("utf8") for key in request.POST.keys() if key.startswith("author")]
        authors, books = filter_books_by_data(request.user, authors)
        return render(request, "books.html", dict(
            books=books,
            authors=authors,
        ))
    else:
        if "query" in request.GET and request.GET["query"]:
            authors = get_books_by_user_author(request.user, request.GET["query"])
            return HttpResponse(json.dumps(dict(suggestions=list(set(authors)))), content_type="application/json")
        else:
            return HttpResponse("Query missing param", status=403)


@book_details
def book_details(request, name, book=None):
    """
    Handle book deletion via POST request and book details retrieving,
    via the @book_details decorator.
    """
    if request.method == "POST":
        delete_book(book, request.user)
        return redirect("/")
    return render(request, "book.html", {'book': book})


def about(request):
    """
    Render about view

    Keyword arguments:
    @param request: the incoming request
    """
    return render(request, "about.html")


def insights(request):
    """
    Render insights view

    Keyword arguments:
    @param request: the incoming request
    """
    data = dict(zip(["tags", "categories", "authors"], get_insights()))
    data = {k: json.dumps(data[k]) for k in data}
    return render(request, "insights.html", data)


def pnf(request):
    """
    Handles the 404 HTTP status code.

    Keyword arguments:
    @param: request the incoming request
    """
    return render(request, "404.html")


def ise(request):
    """Handles the 500 HTTP status code.

    Keyword arguments:
    @param: request the incoming request
    """
    return render(request, "500.html")
