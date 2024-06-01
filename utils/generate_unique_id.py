import random
import string

def generate_unique_id(length=5):
    return ''.join(random.choices(string.ascii_uppercase, k=length))