import random

import pytest

from src.sorting.bucket_sort import bucket_sort_desc
from src.sorting.counting_sort import counting_sort_desc
from src.sorting.radix_sort import radix_sort_desc

ALGORITHMS = [counting_sort_desc, radix_sort_desc, bucket_sort_desc]


def reference(pairs):
    # sorted() es estable: los empates conservan el orden alfabético de entrada
    return sorted(pairs, key=lambda p: -p[1])


def make_pairs(n: int, max_freq: int, seed: int):
    rng = random.Random(seed)
    return sorted((f"term{i:06d}", rng.randint(1, max_freq)) for i in range(n))


@pytest.mark.parametrize("sort_fn", ALGORITHMS, ids=lambda f: f.__name__)
class TestSorting:
    def test_empty(self, sort_fn):
        assert sort_fn([]) == []

    def test_single(self, sort_fn):
        assert sort_fn([("ai", 5)]) == [("ai", 5)]

    def test_all_equal_keeps_alphabetical(self, sort_fn):
        pairs = [("a", 3), ("b", 3), ("c", 3)]
        assert sort_fn(pairs) == pairs

    def test_ties_alphabetical(self, sort_fn):
        pairs = [("research", 46), ("review", 46), ("zeta", 50)]
        assert sort_fn(pairs) == [("zeta", 50), ("research", 46), ("review", 46)]

    @pytest.mark.parametrize("n,max_freq", [(10, 5), (911, 86), (5000, 1000), (2000, 10**6)])
    def test_random_matches_reference(self, sort_fn, n, max_freq):
        pairs = make_pairs(n, max_freq, seed=n)
        assert sort_fn(pairs) == reference(pairs)

    def test_does_not_modify_input(self, sort_fn):
        pairs = make_pairs(100, 20, seed=1)
        copy = list(pairs)
        sort_fn(pairs)
        assert pairs == copy


def test_bucket_sort_with_few_buckets():
    pairs = make_pairs(911, 86, seed=7)
    assert bucket_sort_desc(pairs, num_buckets=5) == reference(pairs)