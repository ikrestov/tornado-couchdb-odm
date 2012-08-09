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
  
    db = None 
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
    def attachments(self):
        return self.data.get('_attachments', None)

    @property
    def saved(self):
        return self.rev is not None and self.pk is not None

    def raw(self):
        d = {}
        d.update(self.data)
        return d

    def raw_identifiers(self):
        return dict(_id=self.pk, _rev=self.rev)


    @property
    def loaded(self):
        return self.saved and len(self.data) > 2

    @gen.engine
    def save(self, callback):
        res = yield gen.Task(self.db.set, self.model_to_dict())
        if res.get('ok', False):
            assert 'id' in res and 'rev' in res
            self.pk = res['id']
            self.rev = res['rev']
        callback(self)

    @gen.engine
    def add_attachment(self, name, data, callback, type='text/plain'):
        if self.saved:
            res = yield gen.Task(self.db.set_attachment, self.raw_identifiers(),name, data, type)
            callback(res)
        else:
            raise self.NotFound("Document is not saved")

    @gen.engine
    def get_attachment(self, name, callback, cache=False):
        if self.saved:
            data = yield gen.Task(self.db.get_attachment, self.pk, name)
            callback(data)
        else:
            raise self.NotFound("Document is not saved")

    @classmethod
    def get_attachment_by_doc(cls, pk, name, callback):
        data = yield gen.Task(cls.db.get_attachment, pk, name)
        callback(data)

    @gen.engine
    def delete(self, callback):
        try:
            if self.saved:
                res = yield gen.Task(self.db.delete, self.raw_identifiers())
                if res.get('ok', False):
                    self.pk = None
                    self.rev = None
        except self.NotFound:
            self.pk=None
            self.rev=None
        callback(self)
 
    @gen.engine
    def refresh(self, callback, attachments=False):
        try:
            if self.saved:
                res = yield gen.Task(self.db.get, self.pk, attachments=attachments)
                if self.rev != res['_rev'] or len(self.rev) != len(res):
                    self.load(res)
        except self.NotFound:
            self.pk=None
            self.rev=None
        callback(self)
