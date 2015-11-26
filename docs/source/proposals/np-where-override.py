import numpy as np

from numba import types
from numba.extending import overlay


@overlay(np.where)
def where(cond, x, y):
    if isinstance(cond, types.Array):
        # Array where() => return an array of the same shape
        if all(ty.layout == 'C' for ty in (cond, x, y)):
            # Faster implementation for C-contiguous arrays
            def where_impl(cond, x, y):
                shape = cond.shape
                if x.shape != shape or y.shape != shape:
                    raise ValueError("all inputs should have the same shape")
                res = np.empty_like(x)
                cf = cond.flat
                xf = x.flat
                yf = y.flat
                rf = res.flat
                for i in range(cond.size):
                    rf[i] = xf[i] if cf[i] else yf[i]
                return res
        else:
            # Generic implementation for other arrays
            def where_impl(cond, x, y):
                shape = cond.shape
                if x.shape != shape or y.shape != shape:
                    raise ValueError("all inputs should have the same shape")
                res = np.empty_like(x)
                for idx, c in np.ndenumerate(cond):
                    res[idx] = x[idx] if c else y[idx]
                return res

    else:
        # Scalar where() => return a 0-dim array
        def where_impl(cond, x, y):
            scal = x if cond else y
            return np.full_like(scal, scal)

    return where_impl
