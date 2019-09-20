import numpy as np
from Exceptions import WrongDimensionException, WrongTypeException


class Point:
    def __init__(self, coord, dtype=np.float64):
        self._coord = np.array(coord, dtype=dtype)

    @property
    def coord(self):
        return self._coord

    @coord.setter
    def coord(self, coord, dtype=np.float64):
        self._coord = np.array(coord, dtype=dtype)

    def __eq__(self, other):
        if type(self) != type(other):
            raise WrongTypeException(f"Can't compare Point and {type(other)}")
        if len(self) != len(other):
            raise WrongDimensionException(f"Comparing points with different dimensions: {len(self)} != {len(other)}")
        else:
            return (self._coord == other._coord).all()

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        try:
            return Point(self._coord + other._coord)
        except AttributeError:
            raise WrongTypeException(f"Can't add an object of type {type(other).__name__} to {type(self).__name__}")
        except ValueError:
            raise WrongDimensionException(
                f"Can't add {type(other).__name__} of len {len(other)} to {type(self).__name__} of len {len(self)}"
            )

    __radd__ = __add__
    __iadd__ = __add__

    def __getattr__(self, attrname):
        return getattr(self._coord, attrname)

    def __len__(self):
        return len(self._coord)

    def __getitem__(self, key):
        return self._coord.__getitem__(key)

    def __setitem__(self, key, value):
        self._coord.__setitem__(key, value)

    def __iter__(self):
        return self._coord.__iter__()

    def __contains__(self, item):
        return self._coord.__contains__(item)

    def __str__(self):
        return str(type(self).__name__) + self._coord.__repr__()[5:]

    def __repr__(self):
        return str(type(self).__name__) + self._coord.__repr__()[5:]

