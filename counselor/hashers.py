from django.contrib.auth.hashers import Argon2PasswordHasher


class CustomArgon2PasswordHasher(Argon2PasswordHasher):
    time_cost = super().time_cost * 10
    memory_cost = super().memory_cost * 3
