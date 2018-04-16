import pytest
from versions import Version
from constraints import allow_major, allow_minor, allow_patch, strict, bounded, Constraint

import intervals as I


def test_create_versions():
    assert Version('1.2.3') == Version(1, 2, 3)
    assert Version('v1.2.3') == Version(1, 2, 3)
    assert Version('V1.2.3') == Version(1, 2, 3)
    assert Version('1.2.3-pre') == Version(1, 2, 3, '-pre')
    assert Version('1.2.3.4.5') == Version(1, 2, 3, '.4.5')
    
    failures = ['a', '1', '1.2', '1a.2.3', '']
    for failure in failures:
        with pytest.raises(ValueError):
            Version(failure)
            
    
def test_versions_comparison():
    pairs = [
        ('1.0.0', '2.0.0'),
        ('1.0.0', '1.1.0'),
        ('1.0.0', '1.0.1'),
        ('1.0.0-pre', '1.0.0'),
    ]
    
    for v1, v2 in pairs:
        v1, v2 = Version(v1), Version(v2)
        
        assert v1 == v1
        assert v2 == v2
        assert v1 != v2
        assert v1 < v2
        assert v1 <= v2
        assert v2 > v1
        assert v2 >= v1


def test_difference():
    assert Version('1.0.0') - Version('1.0.0') == (0, 0, 0)
    assert Version('1.0.0') - Version('0.0.0') == (1, 0, 0)
    assert Version('1.2.3') - Version('1.2.3') == (0, 0, 0)
    assert Version('2.4.6') - Version('1.2.3') == (1, 2, 3)
    assert Version('1.2.3') - Version('2.4.6') == (-1, -2, -3)
    assert Version('2.0.0') - Version('1.2.3') == (1, -2, -3)
    assert Version('2.2.3') - Version('1.3.5') == (1, -1, -2)


def test_strict_atomic_constraints():
    assert strict(I.closed(Version('1.0.0'), Version('1.0.0')).to_atomic())
    assert strict(I.closedopen(Version('1.0.0'), Version('1.0.1')).to_atomic())
    assert strict(I.closedopen(Version('1.0.0'), Version('1.0.1')).to_atomic())
    
    assert not strict(I.closed(Version('1.0.0'), Version('1.0.1')).to_atomic())
    assert not strict(I.closed(Version('1.0.0'), Version('1.1.0')).to_atomic())
    assert not strict(I.closed(Version('1.0.0'), Version('2.0.0')).to_atomic())
    assert not strict(I.closed(Version('1.0.0'), I.inf).to_atomic())
    
    
def test_bounded_atomic_constraints():
    assert bounded(I.closed(Version('1.0.0'), Version('2.0.0')).to_atomic())
    assert bounded(I.closed(Version('1.0.0'), Version('1.0.0')).to_atomic())
    assert bounded(I.closed(Version('1.0.0'), Version('1.0.1')).to_atomic())
    assert bounded(I.closed(Version('1.0.0'), Version('1.1.0')).to_atomic())
    assert bounded(I.closedopen(Version('1.0.0'), Version('1.0.1')).to_atomic())
    assert not bounded(I.closed(Version('1.0.0'), I.inf).to_atomic())


def test_soft_atomic_constraints():
    i = I.closed(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allow_major(i) and allow_minor(i) and allow_patch(i)
    
    i = I.closedopen(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allow_major(i) and allow_minor(i) and allow_patch(i)
    
    i = I.openclosed(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allow_major(i) and allow_minor(i) and allow_patch(i)
    
    i = I.open(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allow_major(i) and allow_minor(i) and allow_patch(i)
    
    i = I.closed(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allow_major(i) and not allow_minor(i) and allow_patch(i)
    
    i = I.closedopen(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allow_major(i) and not allow_minor(i) and allow_patch(i)
    
    i = I.openclosed(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allow_major(i) and not allow_minor(i) and allow_patch(i)
    
    i = I.open(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allow_major(i) and not allow_minor(i) and allow_patch(i)
    
    i = I.closed(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allow_major(i) and not allow_minor(i) and not allow_patch(i)

    i = I.closedopen(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allow_major(i) and not allow_minor(i) and not allow_patch(i)
    
    i = I.openclosed(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allow_major(i) and not allow_minor(i) and not allow_patch(i)
    
    i = I.open(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allow_major(i) and not allow_minor(i) and not allow_patch(i)


def test_hard_atomic_constraints():
    i = I.closed(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.open(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and not allow_patch(i, soft=False)
    
    i = I.closed(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allow_major(i, soft=False) and allow_minor(i, soft=False) and allow_patch(i, soft=False)

    i = I.open(Version('1.0.0'), Version('1.1.0')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.closed(Version('1.0.0'), Version('1.0.0')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and not allow_patch(i, soft=False)
    
    i = I.closed(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert allow_major(i, soft=False) and allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.open(Version('1.0.0'), Version('2.0.0')).to_atomic()
    assert not allow_major(i, soft=False) and allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.openclosed(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and not allow_patch(i, soft=False)
    
    i = I.closedopen(Version('1.0.0'), Version('1.0.1')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and not allow_patch(i, soft=False)
    
    i = I.open(Version('1.0.0'), I.inf).to_atomic()
    assert allow_major(i, soft=False) and allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.closed(Version('0.0.1'), Version('1.0.0')).to_atomic()
    assert allow_major(i, soft=False) and allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.open(Version('0.0.1'), Version('1.0.0')).to_atomic()
    assert not allow_major(i, soft=False) and allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.closed(Version('0.0.1'), Version('0.0.1')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and not allow_patch(i, soft=False)
    
    i = I.closed(Version('0.0.1'), Version('0.0.2')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.open(Version('0.0.1'), Version('0.0.2')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and not allow_patch(i, soft=False)
    
    i = I.closed(Version('0.0.1'), Version('0.1.0')).to_atomic()
    assert not allow_major(i, soft=False) and allow_minor(i, soft=False) and allow_patch(i, soft=False)
    
    i = I.open(Version('0.0.1'), Version('0.1.0')).to_atomic()
    assert not allow_major(i, soft=False) and not allow_minor(i, soft=False) and allow_patch(i, soft=False)


def test_interval_constraints():
    tests = {
        I.closedopen(Version('1.0.0'), Version('3.0.0')): {
            'strict': False,
            'bounded': True,
            'soft_latest': (False, True, True),
            'soft_all': (False, True, True),
            'hard_latest': (True, True, True),
            'hard_all': (True, True, True),
        },
        I.closedopen(Version('1.0.0'), Version('3.0.0')) | I.singleton(Version('4.0.0')): {
            'strict': False,
            'bounded': True,
            'soft_latest': (False, False, False),
            'soft_all': (False, True, True),
            'hard_latest': (False, False, False),
            'hard_all': (True, True, True),
        },
        I.closed(Version('1.0.0'), Version('2.0.0')) | I.closedopen(Version('3.0.0'), Version('3.1.0')): {
            'strict': False,
            'bounded': True,
            'soft_latest': (False, False, True),
            'soft_all': (False, True, True),
            'hard_latest': (False, False, True),
            'hard_all': (True, True, True),
        },
        I.closed(Version('1.0.0'), Version('2.0.0')) | I.closed(Version('3.0.0'), Version('3.1.0')): {
            'strict': False,
            'bounded': True,
            'soft_latest': (False, False, True),
            'soft_all': (False, True, True),
            'hard_latest': (False, True, True),
            'hard_all': (True, True, True),
        },
    }
    
    for constraint, expected in tests.items():
        i = Constraint(constraint)

        assert i.strict() == expected['strict']
        assert i.bounded() == expected['bounded']
        p = {'soft': True, 'latest': True}
        assert (i.allow_major(**p), i.allow_minor(**p), i.allow_patch(**p)) == expected['soft_latest']
        p = {'soft': True, 'latest': False}
        assert (i.allow_major(**p), i.allow_minor(**p), i.allow_patch(**p)) == expected['soft_all']
        p = {'soft': False, 'latest': True}
        assert (i.allow_major(**p), i.allow_minor(**p), i.allow_patch(**p)) == expected['hard_latest']
        p = {'soft': False, 'latest': False}
        assert (i.allow_major(**p), i.allow_minor(**p), i.allow_patch(**p)) == expected['hard_all']
