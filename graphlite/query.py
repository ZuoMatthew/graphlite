from contextlib import closing
import graphlite.sql as SQL


class V(object):
    def __init__(self, src=None, rel=None, dst=None):
        self.src = src
        self.rel = rel
        self.dst = dst

    def __getattr__(self, attr):
        values = self.__dict__
        if attr in values:
            return values[attr]
        self.rel = attr
        return self

    def __call__(self, dst):
        self.dst = dst
        return self


class Query(object):
    def __init__(self, db):
        self.db = db
        self.sql = []
        self.params = []

    def __iter__(self):
        statement = '\n'.join(self.sql)
        with closing(self.db.cursor()) as cursor:
            cursor.execute(statement, self.params)
            for item in cursor:
                yield item[0]

    def __call__(self, edge):
        src, rel, dst = edge.src, edge.rel, edge.dst
        statement, params = (
            SQL.forwards_relation(src, rel) if dst is None else
            SQL.inverse_relation(dst, rel)
        )
        self.sql.append(statement)
        self.sql.extend(params)

    @property
    def intersection(self):
        self.sql.append('INTERSECTION')
        return self

    @property
    def difference(self):
        self.sql.append('EXCEPT')
        return self

    @property
    def union(self):
        self.sql.append('UNION')
        return self