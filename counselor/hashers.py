from django.contrib.auth.hashers import ScryptPasswordHasher


class CustomScryptPasswordHasher(ScryptPasswordHasher):
    iterations = ScryptPasswordHasher.work_factor * 100
