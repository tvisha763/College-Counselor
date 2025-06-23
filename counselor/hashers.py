from django.contrib.auth.hashers import Argon2PasswordHasher


class CustomArgon2PasswordHasher(Argon2PasswordHasher):
    def __init__():
        super().__init__()
        self.time_cost = super().time_cost * 10
        self.memory_cost = super().memory_cost * 3
