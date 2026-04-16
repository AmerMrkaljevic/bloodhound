# tests/test_entity_resolver.py
from normalizer.entity_resolver import EntityResolver


def test_resolver_finds_exact_match():
    resolver = EntityResolver(["Apple Inc.", "Microsoft Corp", "Tesla Inc"])
    match = resolver.resolve("Apple Inc.")
    assert match == "Apple Inc."


def test_resolver_finds_fuzzy_match():
    resolver = EntityResolver(["Apple Inc.", "Microsoft Corp", "Tesla Inc"])
    match = resolver.resolve("Apple Incorporated")
    assert match == "Apple Inc."


def test_resolver_returns_none_for_no_match():
    resolver = EntityResolver(["Apple Inc.", "Microsoft Corp"])
    match = resolver.resolve("Completely Unknown XYZ Corp", threshold=90)
    assert match is None


def test_resolver_handles_empty_candidates():
    resolver = EntityResolver([])
    match = resolver.resolve("Apple Inc.")
    assert match is None
