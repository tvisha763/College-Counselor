from django.contrib.auth.hashers import Argon2PasswordHasher


class CustomArgon2PasswordHasher(Argon2PasswordHasher):
    time_cost = Argon2PasswordHasher.time_cost * 5
    memory_cost = Argon2PasswordHasher.memory_cost * 5
