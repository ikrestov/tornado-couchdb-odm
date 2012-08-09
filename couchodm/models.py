#! /usr/bin/python

__author__="Igor Krestov"
__date__ ="$26-Jul-2012 15:35:32$"

from odm import Model
from .manager import CouchManager

from tornado import gen
from trombi.exceptions import TrombiException, TrombiBadRequest, TrombiConflict, TrombiPreconditionFailed, TrombiNotFound, TrombiServerError, TrombiInvalidDatabaseName, TrombiConnectionFailed

class CouchModel(Model):
    Exception 		= TrombiException
    BadRequest 		= TrombiBadRequest
    Conflict		= TrombiConflict
    PreconditionFailed	= TrombiPreconditionFailed
    NotFound		= TrombiNotFound
    ServerError		= TrombiServerError
    InvalidDatabaseName = TrombiInvalidDatabaseName
    ConnectionFailed	= TrombiConnectionFailed    

    db = #AsyncCouch() # TODO
    
    objects = CouchManager()
    
    class Meta:
        pk_name = '_id'
        pass_to_manager = ('db',)
        
    @property
    def rev(self):
        return self.data.get('_rev', None)

    @rev.setter
    def rev(self, value):
        self.data['_rev'] = value

    @property
    def saved(self):
        return self.rev is not None and self.pk is not None

    @gen.engine
    def save(self, callback):
        res = yield gen.Task(self.db.set, self.model_to_dict())
        if res.get('ok', False):
            assert 'id' in res and 'rev' in res
            self.pk = res['id']
            self.rev = res['rev']
        callback(self)

    @gen.engine
    def delete(self, callback):
        res = yield gen.Task(self.db.delete, self.model_to_dict())
        if res.get('ok', False):
            self.pk = None
            self.rev = None
        callback(self)
