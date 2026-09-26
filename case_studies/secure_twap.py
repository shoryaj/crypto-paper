"""Assumed bounded oracle; a TWAP implementation is not modeled."""
import json
from .bzx_exploit import run


if __name__ == '__main__':
    print(json.dumps(run('bounded', epsilon='0.1').verify_economic_invariant(), indent=2))
