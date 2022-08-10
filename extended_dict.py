from slpp import slpp


class ExtendedDict(dict):
    def rename(self, key, newkey):
        if key in self:
            self[newkey] = self[key]
            del self[key]

    def to_table(self):
        return slpp.encode(self)

    def delete(self, item):
        if item in self:
            del self[item]
