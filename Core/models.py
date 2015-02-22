from mongoengine import *
from mongoengine.django.auth import User

import datetime


class BookDetail(EmbeddedDocument):
    authors = ListField(StringField())
    tags = ListField(StringField())
    image_link = StringField()
    description = StringField()
    isbn = StringField()
    parsed_tags = ListField(StringField())

    meta = {'indexes': [
         {'fields': ['$authors'],
          #'weight': {'title': 10, 'content': 2}
         }
     ]}


class Book(EmbeddedDocument):
    title = StringField(required=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    details = EmbeddedDocumentField(BookDetail)
    pk = IntField()

    meta = {'indexes': [
         {'fields': ['$title'],
          'default_language': 'italian',
          #'weight': {'title': 10, 'content': 2}
         }
     ]}

    def is_valid(self):
        return self.title and self.author


class Profile(Document):
    user = ReferenceField(User)
    books = ListField(EmbeddedDocumentField(Book))
