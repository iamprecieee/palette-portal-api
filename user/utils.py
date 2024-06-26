from uuid import uuid4


def generate_default_username():
    return f"user{str(uuid4())}"