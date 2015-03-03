from Core.models import BookDetail
from Core.models import Book
from Core.keys import API_KEY

from pattern.it import parsetree as it_parsetree
from pattern.en import parsetree as en_parsetree
from pattern.search import search
import requests
import json


def remove_uncorrect_tokens(tokens):
    """Remove useless tokens"""
    tokens = list(set(tokens))
    tokens = filter(lambda t: len(t) > 3, tokens)
    tokens = sorted(tokens, key=lambda token: -len(token))
    return tokens


def get_ngrams(description, lang='it'):
    """
    Analyze description and get relevant ngrams using an italian POS tagger,
    looking for exact combination of POS pattern
    """
    s = it_parsetree(description, relations=True, lemmata=True)
    if lang == "en":
        s = en_parsetree(description, relations=True, lemmata=True)

    matches = []
    ngrams = []
    for match in search("JJ NN", s):
            matches.append(match.constituents())
    for match in search("NN JJ", s):
            matches.append(match.constituents())
    for match in search("NN", s):
            matches.append(match.constituents())
    for match in matches:
        ngrams.append(" ".join([chunk.string for chunk in match]).encode("utf8"))
    return remove_uncorrect_tokens(ngrams)


def retrieve_additional_info(isbn):
    """
    Retrieve additional info about books not yet processed

    Keyword arguments:
    @param: isbn the ISBN book code
    """
    r = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:%s&key=%s&country=IT" %(isbn, API_KEY))
    response = json.loads(r.text)
    pres = {}
    parsed_result = {}
    book = None
    if "items" in response:
        parsed_result = response["items"][0]
        if "title" in parsed_result["volumeInfo"]:
            book = Book(title=(parsed_result["volumeInfo"]["title"]).encode("utf8"))
        if "authors" in parsed_result["volumeInfo"]:
            pres["authors"] = [author.encode("utf8") for author in parsed_result["volumeInfo"]["authors"]]
        if "categories" in parsed_result["volumeInfo"]:
            pres["tags"] = parsed_result["volumeInfo"]["categories"]
        if "imageLinks" in parsed_result["volumeInfo"]:
            pres["image_link"] = parsed_result["volumeInfo"]["imageLinks"]["thumbnail"]
        if "industryIdentifiers" in parsed_result["volumeInfo"]:
            pres["isbn"] = isbn
        if not "description" in parsed_result["volumeInfo"]:
            r = requests.get("%s?key=%s&country=IT" %(parsed_result["selfLink"], API_KEY))
            parsed_result = (json.loads(r.text))
        pres["description"] = parsed_result["volumeInfo"].get("description", "")
        lang = parsed_result["volumeInfo"]["language"]
    pres["parsed_tags"] = get_ngrams(pres["description"], lang=lang)
    book.details = BookDetail(**pres)
    return book
