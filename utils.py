import os

def normalize(path):
    """
    normalize path to Unix style
    """
    path = os.path.normpath(path)
    path = path.replace('\\', '/')
    return path