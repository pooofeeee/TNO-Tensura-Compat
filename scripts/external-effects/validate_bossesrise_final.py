"""Validate the current block_factorys_bosses native catalog independently of its old builder."""
import json

from validate_current_integrity import validate_mod


def validate_final():
    return validate_mod('block_factorys_bosses')


if __name__ == '__main__':
    print(json.dumps(validate_final(), sort_keys=True))
