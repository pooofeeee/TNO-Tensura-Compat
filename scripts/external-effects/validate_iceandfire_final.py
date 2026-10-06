"""Validate the current iceandfire native catalog independently of its old builder."""
import json

from validate_current_integrity import validate_mod


def validate_final():
    return validate_mod('iceandfire')


if __name__ == '__main__':
    print(json.dumps(validate_final(), sort_keys=True))
