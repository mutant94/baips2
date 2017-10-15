from django.contrib.auth.hashers import BasePasswordHasher


class PlainHasher(BasePasswordHasher):
    algorithm = 'none'

    def verify(self, password, encoded):
        return password == encoded.split('$')[2]

    def encode(self, password, salt):
        return "{0}${1}${2}".format(self.algorithm, 0, password)

    def safe_summary(self, encoded):
        return {"password": encoded, "algorithm": self.algorithm}
