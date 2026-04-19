from __future__ import annotations


def equals(actual: object, expected: object) -> bool:
    return actual == expected


def contains(actual: object, expected: object) -> bool:
    return str(expected) in str(actual)
