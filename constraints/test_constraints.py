import pytest
from versions import Version
from constraints import (
    allows_major, allows_minor, allows_patch,
    strict, upper_bounded, lower_bounded
)

import intervals as I


def test_strict_constraints():
    assert strict(I.closed(Version('1.0.0'), Version('1.0.0')))
    assert strict(I.closedopen(Version('1.0.0'), Version('1.0.1')))
    assert strict(I.closedopen(Version('1.0.0'), Version('1.0.1')))
    
    assert not strict(I.closed(Version('1.0.0'), Version('1.0.1')))
    assert not strict(I.closed(Version('1.0.0'), Version('1.1.0')))
    assert not strict(I.closed(Version('1.0.0'), Version('2.0.0')))
    assert not strict(I.closed(Version('1.0.0'), I.inf))
    
    
def test_bounded_constraints():
    assert upper_bounded(I.closed(Version('1.0.0'), Version('2.0.0')))
    assert upper_bounded(I.closed(Version('1.0.0'), Version('1.0.0')))
    assert upper_bounded(I.closed(Version('1.0.0'), Version('1.0.1')))
    assert upper_bounded(I.closed(Version('1.0.0'), Version('1.1.0')))
    assert upper_bounded(I.closedopen(Version('1.0.0'), Version('1.0.1')))
    assert not upper_bounded(I.closed(Version('1.0.0'), I.inf))

    assert lower_bounded(I.closed(Version('0.0.1'), Version('2.0.0')))
    assert lower_bounded(I.closed(Version('0.0.2'), Version('2.0.0')))
    assert not lower_bounded(I.closed(Version.FIRST, Version('2.0.0')))


def test_soft_atomic_constraints():
    i = I.closed(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allows_major(i) and allows_minor(i) and allows_patch(i)
    
    i = I.closedopen(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allows_major(i) and allows_minor(i) and allows_patch(i)
    
    i = I.openclosed(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allows_major(i) and allows_minor(i) and allows_patch(i)
    
    i = I.open(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allows_major(i) and allows_minor(i) and allows_patch(i)
    
    i = I.closed(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allows_major(i) and not allows_minor(i) and allows_patch(i)
    
    i = I.closedopen(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allows_major(i) and not allows_minor(i) and allows_patch(i)
    
    i = I.openclosed(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allows_major(i) and not allows_minor(i) and allows_patch(i)
    
    i = I.open(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allows_major(i) and not allows_minor(i) and allows_patch(i)
    
    i = I.closed(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allows_major(i) and not allows_minor(i) and not allows_patch(i)

    i = I.closedopen(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allows_major(i) and not allows_minor(i) and not allows_patch(i)
    
    i = I.openclosed(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allows_major(i) and not allows_minor(i) and not allows_patch(i)
    
    i = I.open(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allows_major(i) and not allows_minor(i) and not allows_patch(i)


def test_hard_atomic_constraints():
    i = I.closed(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.open(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and not allows_patch(i, soft=False)
    
    i = I.closed(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allows_major(i, soft=False) and allows_minor(i, soft=False) and allows_patch(i, soft=False)

    i = I.open(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.closed(Version('1.0.0'), Version('1.0.0')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and not allows_patch(i, soft=False)
    
    i = I.closed(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert allows_major(i, soft=False) and allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.open(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allows_major(i, soft=False) and allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.openclosed(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and not allows_patch(i, soft=False)
    
    i = I.closedopen(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and not allows_patch(i, soft=False)
    
    i = I.open(Version('1.0.0'), I.inf).to_atomic()
    assert allows_major(i, soft=False) and allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.closed(Version.FIRST, Version('1.0.0')).to_atomic()
    assert allows_major(i, soft=False) and allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.open(Version.FIRST, Version('1.0.0')).to_atomic()
    assert not allows_major(i, soft=False) and allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.closed(Version.FIRST, Version.FIRST).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and not allows_patch(i, soft=False)
    
    i = I.closed(Version.FIRST, Version('0.0.2')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.open(Version.FIRST, Version('0.0.2')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and not allows_patch(i, soft=False)
    
    i = I.closed(Version.FIRST, Version('0.1.0')).to_atomic()
    assert not allows_major(i, soft=False) and allows_minor(i, soft=False) and allows_patch(i, soft=False)
    
    i = I.open(Version.FIRST, Version('0.1.0')).to_atomic()
    assert not allows_major(i, soft=False) and not allows_minor(i, soft=False) and allows_patch(i, soft=False)


def test_interval_constraints():
    tests = {
        I.closedopen(Version('1.0.0'), Version('3.0.0')): {
            'strict': False,
            'bounded': (True, True),
            'soft': (False, True, True),
            'hard': (True, True, True),
        },
        I.closedopen(Version('1.0.0'), Version('3.0.0')) | I.singleton(Version('4.0.0')): {
            'strict': False,
            'bounded': (True, True),
            'soft': (False, False, False),
            'hard': (True, True, True),
        },
        I.closed(Version('1.0.0'), Version('2.0.0')) | I.closedopen(Version('3.0.0'), Version('3.1.0')): {
            'strict': False,
            'bounded': (True, True),
            'soft': (False, False, True),
            'hard': (True, True, True),
        },
        I.closed(Version('1.0.0'), Version('2.0.0')) | I.closed(Version('3.0.0'), Version('3.1.0')): {
            'strict': False,
            'bounded': (True, True),
            'soft': (False, False, True),
            'hard': (True, True, True),
        },
    }
    
    for constraint, expected in tests.items():
        assert strict(constraint) == expected['strict']
        assert (lower_bounded(constraint), upper_bounded(constraint)) == expected['bounded']
        assert (allows_major(constraint), allows_minor(constraint), allows_patch(constraint)) == expected['soft']
        assert (allows_major(constraint, soft=False), allows_minor(constraint, soft=False), allows_patch(constraint, soft=False)) == expected['hard']
