from Core.models import Profile
from Core.models import Book, BookDetail
from Core.mining import retrieve_additional_info

from bson.objectid import ObjectId
from mongoengine.django.auth import User
import itertools
import functools
import json


def make_aggregation_query(query, function):
    """
    Lunch aggregation pipelines via mongoengine/pymongo wrapper

    @param query: the aggregation query (a string or a list of stages)
    @param function: the wrapper
    """
    return function(query)

make_aggregation_query_mongonegine = functools.partial(make_aggregation_query, function=Profile.objects.exec_js)
make_aggregation_query_pymongo = functools.partial(make_aggregation_query, function=Profile._get_collection().aggregate)


def get_books_by_user_author(user, querystring):
    """
    Return <user> books looking for querystring provided by client

    @param user: the user whose books need to be retrieved
    @param querystring: the querystring containing authors to filter out books
    """
    try:
        cfr = """db.profile.aggregate([{$match:{"user" : ObjectId("%s")}},{$project:{"books.details.authors":1}},{$unwind:"$books"},{$match:{"books.details.authors":{$regex:/.*%s*/i}}}])""" %(user.id,querystring)
        r = Profile.objects.exec_js(cfr)
        return list(itertools.chain.from_iterable([result["books"]["details"]["authors"] for result in r["_firstBatch"]]))
    except Exception as e:
        print e
        return None


def create_user(data):
    """
    Add new User

    Keyword arguments:
    @param data: data whose user details need to be extracted
    """
    user = User.create_user(data["username"], data["password"], data["email"])
    profile = Profile(user=user)
    profile.save()
    return user


def ensure_login(data):
    """
    Ensure user is signed up

    Keyword arguments:
    @param data: to check user credentials
    """
    try:
            user = User.objects.get(username=data["username"])
            if user.check_password(data["password"]):
                    return user
            else:
                return None
    except User.DoesNotExist:
        return None
    except Exception:
        return None


def add_book(user, data):
    """
    Add a new book for logged user

    keyword arguments:
    @param user: the user whose the book belongs to
    @param data: POST data to add the new book
    """
    try:
            profile = Profile.objects.get(user=user)
            if not profile.books:
                profile.books = list()
            book = retrieve_additional_info(data["isbn"])
            profile.books = profile.books + [book]
            profile.save()
            return get_books_by_user(user)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


def get_books_by_user(user):
    """
    Get books by user, along with its reading insights

    keyword arguments:
    @param user: the user whose books belongs to
    """
    profile = Profile.objects.filter(user=user) \
        .order_by("books.updated_at").first()
    authors = list(set(author for book in profile.books for author in book.details.authors))
    genres = list(set(genre for book in profile.books for genre in book.details.tags))
    data = make_aggregation_query_pymongo([
        {"$match":{"_id":ObjectId('%s' %profile.id)}},
        {"$project":{"books.updated_at":1, "books.title":1}},
        {"$unwind":"$books"},
        {"$group":{"elements":{"$push":"$books.title"}, "_sum":{"$sum":1}, "_id":{"year":{"$year":"$books.updated_at"}, "month":{"$month":"$books.updated_at"}}}}])
    reads_values = []
    reads_dates = []
    titles = []
    if "result" in data:
        for result in data["result"]:
            reads_values.append(result["_sum"])
            reads_dates.append("%s-%s" %(result["_id"]["month"],result["_id"]["year"]))
            titles.append(result["elements"])
    return profile.books, authors, genres, reads_dates[::-1], reads_values[::-1], json.dumps(titles[::-1])


def filter_books_by_data(user, authors):
    """
    Filter books by author data, got from HTTP request.

    Keyword arguments:
    @param user: the current logged in user
    @param authors: the authors to be used for searching
    """
    try:
        querystring_authors = ",".join(['"'+author+'"' for author in authors])
        if querystring_authors:
            querystring_authors = ',{$match:{"books.details.authors":{$elemMatch:{$in:[%s]}}}}' %querystring_authors
        querystring = """db.profile.aggregate([{$match:{"user" : ObjectId("%s")}},{$project:{"books.details.tags":1,"books.details.image_link":1,"books.details.authors":1, "books.title":1}},{$unwind:"$books"}%s])""" %(user.id,querystring_authors)
        querystring = unicode(querystring, "utf8").encode("utf8")
        r = make_aggregation_query_mongonegine(querystring)
        return authors, [Book(**result["books"]) for result in r["_firstBatch"]]
    except Exception as e:
        print e
        return None, None


def get_book_by_name(name, user):
    """
    Get book by name and user

    keyword arguments:
    @param: name the name of the book to be searched for
    @param: the user whose the book belongs to
    """
    result = make_aggregation_query_pymongo(({"$unwind":"$books"}, {"$match":{"books.title":name}}))
    if "result" in result and result["result"]:
        return Book(**result["result"][0]["books"])
    return None


def delete_book(book, user):
    """
    Delete book

    Keyword arguments:
    @param: book the book to be deleted
    @param: user the user whose the book belongs to
    """
    try:
        profile = Profile.objects(user=user).update_one(pull__books__title=book.title)
    except Exception as e:
        print "Error in deleting ", book


def get_insights():
    """
    Get Magnet insights using the aggregate framework;
    use pymongo instead of mongoengine wrapper, because it seems experiencing iussues with aggregation framework
    """
    tags = make_aggregation_query_pymongo(({"$unwind":"$books"},{"$project":{"books.details.parsed_tags":1}}, {"$unwind":"$books.details.parsed_tags"}, {"$group":{"_id":"$books.details.parsed_tags", "count": { "$sum": 1 }}},{"$sort":{"count":1}}))
    categories = make_aggregation_query_pymongo(({"$unwind":"$books"},{"$project":{"books.details.tags":1}}, {"$unwind":"$books.details.tags"}, {"$group":{"_id":"$books.details.tags", "count": { "$sum": 1 }}}))
    authors = make_aggregation_query_pymongo(({"$unwind":"$books"},{"$project":{"books.details.authors":1}}, {"$unwind":"$books.details.authors"}, {"$group":{"_id":"$books.details.authors", "count": { "$sum": 1 }}}))
    tags = [dict(name=d["_id"], count=d["count"]) for d in tags["result"] if d["count"] >4]
    categories = [dict(name=d["_id"], count=d["count"]) for d in categories["result"]]
    authors = [dict(name=d["_id"], count=d["count"]) for d in authors["result"]]
    return tags, categories, authors
