import couch
from couchodm import CouchModel, CouchManager
from tornado.testing import AsyncTestCase
from tornado import gen
from tornado import ioloop


class BaseManager(CouchManager):
  fetch_my_projects = CouchManager.fetch_view('design', 'view')

class BaseModel(CouchModel):
  db = couch.AsyncCouch('project')
  objects = BaseManager()

class CouchdbTestCase(AsyncTestCase):
    def test_http_fetch(self):
        self.m = BaseModel()
        self.m['name'] = 'Test Project'
        self.m.save(self._saved)
        self.wait()

    def _saved(self, r):
        print('Saved:', r, self.m.model_to_dict())
        self.stop()


def main():
    @gen.engine
    def in_loop():
        m = BaseModel()
        m['name'] = 'Test'
        #yield gen.Task(m.save)
        #print('Saved model:', m.saved, m.model_to_dict())
        #print('PK:', m.pk, m.Meta.pk_name, ', REV:', m.rev)
        try:
            m = yield gen.Task(BaseModel.objects.get, '1b2cbd0d69f8d69f2a5e263066019162')
        #print('Obj:', m, 'PK:', m.pk, m.model_to_dict())
        #yield gen.Task(m.delete)
        #try:
            print('PK:', m.pk, m.Meta.pk_name, ', REV:', m.rev)
            print("-"*30)
        except Exception as e:
            print(e)
        objects= yield gen.Task(BaseModel.objects.fetch_my_projects, key='1b2cbd0d69f8d69f2a5e263066019162')
        for obj in objects:
          print(obj)
        ioloop.IOLoop.instance().stop()
    ioloop.IOLoop.instance().add_callback(in_loop)
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
