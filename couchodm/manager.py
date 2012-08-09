#! /usr/bin/python

__author__="Igor Krestov"
__date__ ="$26-Jul-2012 15:36:42$"


from odm import Manager
from tornado import gen

class CouchManager(Manager):
        
    @gen.engine
    def create(self, **kwargs):
        """
        Create and save new Model object based on passed keyword arguments
        """
        try: callback = kwargs.pop('callback')
        except KeyError: callback = None
        obj = yield gen.Task(self.model_class(kwargs).save)
        if hasattr(callback, '__call__'):
            callback(obj)
    
    @gen.engine
    def get(self, pk, callback):
        """
        Function fetches/ loads only **one** record, returns instance of class *Model*
        """
        res = yield gen.Task(self.db.get, pk)
        callback(self.model_class(res))
        
    @gen.engine
    def fetch(self, design, view, callback, **kwargs):
        """
        Loads a list of objects, returns *Iterable*.
        Each value is instance of class *Model*.
        """
        res = yield gen.Task(self.db.view,design, view, **kwargs)
        callback(self._view_to_iterable(res))
        
    @gen.engine
    def fetch_all(self, callback, **kwargs):
        res = yield gen.Task(self.db.view, None, '_all_docs', **kwargs)
        iterator = (self.model_class(dict(_id=row['id'], _rev=row['value']['rev'])) for row in res['rows'])
        callback(iterator)

    def _view_to_iterable(self, res):
        """
        Transforms CouchDB's *view* result into generator that produces **Model** instances
        """
        return (self.model_class(row['value']) for row in res['rows'] if 'value' in row)

    @staticmethod
    def fetch_view(design, view):
        def _fetch_view(self, callback, **kwargs):
            self.fetch(design, view, callback, **kwargs)
        return _fetch_view
