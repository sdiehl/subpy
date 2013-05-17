from .features import *
from .validate import detect, fd, checker, validator, \
    FeatureNotSupported, FullPython


from .tests.test_features import run

test = run
