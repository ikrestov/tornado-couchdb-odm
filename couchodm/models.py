#! /usr/bin/python

__author__="Igor Krestov"
__date__ ="$26-Jul-2012 15:35:32$"

from odm import Model
from .manager import CouchManager

from couch import AsyncCouch, CouchException, NotModified, BadRequest, NotFound, MethodNotAllowed, Conflict, PreconditionFailed, InternalServerError
from tornado import gen

class CouchModel(Model):
    Exception = CouchException
    NotModified = NotModified
    BadRequest = BadRequest
    NotFound = NotFound
    MethodNotAllowed = MethodNotAllowed
    Conflict = Conflict
    PreconditionFailed = PreconditionFailed
    InternalServerError = InternalServerError

    
    db = AsyncCouch() # TODO
    
    objects = CouchManager()
    
    class Meta:
        pass_to_manager = ('db',)
        
    @gen.engine
    def save(self, callback):
        res = yield gen.Task(self.db.save_doc, self.model_to_dict())
        print(res)
        callback(res)
        