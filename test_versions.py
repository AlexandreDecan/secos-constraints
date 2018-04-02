import pytest
from versions import Version, Interval, IntervalSet


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
        
        assert Version.lowest() < v1 < Version.highest()


def test_range_containment():
    v1, v2, v3, v4 = Version('1.0.0'), Version('2.0.0'), Version('3.0.0'), Version('4.0.0')
    
    assert Interval.closed(v2, v3) in Interval.closed(v1, v4)
    assert v2 in Interval.closed(v1, v3)
    assert v2 in Interval.closed(v2, v3)
    assert v3 in Interval.closed(v2, v3)
    
    assert Interval.open(v1, v2) in Interval.closed(v1, v2)
    
    assert Interval.closed(v1, v2) in Interval.closed(v1, Version.highest())
    assert v1 in Interval.closed(v1, Version.highest())
        
    assert v1 not in Interval.open(v1, v2)
    assert v2 not in Interval.open(v1, v2)
    
    
def test_range_and():
    v1, v2, v3, v4 = Version('1.0.0'), Version('2.0.0'), Version('3.0.0'), Version('4.0.0')
    
    assert Interval.closed(v1, v3) & Interval.closed(v2, v4) == Interval.closed(v2, v3)
    assert Interval.closed(v1, Version.highest()) & Interval.closed(v2, v4) == Interval.closed(v2, v4)
    assert Interval.closed(Version.lowest(), v2) & Interval.closed(v1, v4) == Interval.closed(v1, v2)
    
    assert Interval.closed(v1, v2) & Interval.closed(v1, v2) == Interval.closed(v1, v2)
    assert Interval.closed(v1, v2) & Interval.closed(v2, v3) == Interval.closed(v2, v2)
    
    
def test_range_is_empty():
    v1, v2, v3, v4 = Version('1.0.0'), Version('2.0.0'), Version('3.0.0'), Version('4.0.0')
    
    assert not Interval.closed(v1, v2).empty()
    assert not Interval.closed(v1, v1).empty()
    
    assert Interval.openclosed(v1, v1).empty()
    assert Interval.closedopen(v1, v1).empty()
    assert (Interval.closed(v1, v2) & Interval.closed(v3, v4)).empty()


def test_range_intersection():
    v1, v2, v3, v4 = Version('1.0.0'), Version('2.0.0'), Version('3.0.0'), Version('4.0.0')
    
    assert (Interval.closed(v1, v2) & Interval.closed(v3, v4)).empty()
    assert Interval.closed(v1, v2) & Interval.closed(v1, v2) == Interval.closed(v1, v2)
    
    assert Interval.open(v1, v2) & Interval.closed(v1, v2) == Interval.open(v1, v2)
    assert Interval.closed(v1, v3) & Interval.open(v2, v4) == Interval.openclosed(v2, v3)


def test_range_union():
    v1, v2, v3, v4 = Version('1.0.0'), Version('2.0.0'), Version('3.0.0'), Version('4.0.0')
    
    assert Interval.closed(v1, v2) | Interval.closed(v1, v2) == Interval.closed(v1, v2)
    assert Interval.closed(v1, v4) | Interval.closed(v2, v3) == Interval.closed(v1, v4)
    
    assert Interval.closed(v1, v2) | Interval.open(v2, v3) == Interval.closedopen(v1, v3)
    assert Interval.closed(v1, v3) | Interval.closed(v2, v4) == Interval.closed(v1, v4)
    
    assert Interval.closedopen(v1, v2) | Interval.closed(v2, v3) == Interval.closed(v1, v3)
    assert Interval.open(v1, v2) | Interval.closed(v2, v4) == Interval.openclosed(v1, v4)
    
    assert Interval.closed(v1, v2) | Interval.closed(v3, v4) == IntervalSet(Interval.closed(v1, v2), Interval.closed(v3, v4))


def test_set_intersection():
    v1, v2, v3, v4, v5, v6 = Version('1.0.0'), Version('2.0.0'), Version('3.0.0'), Version('4.0.0'), Version('5.0.0'), Version('6.0.0')
    
    is1 = IntervalSet(Interval.closed(v1, v3), Interval.closed(v4, v6))
    is2 = IntervalSet(Interval.closed(v2, v4), Interval.open(v5, v6))
    is3 = IntervalSet(Interval.closed(v2, v3), Interval.closed(v4, v4), Interval.open(v5, v6))

    assert is1 & is2 == is3
    
    
def test_set_union():
    v1, v2, v3, v4 = Version('1.0.0'), Version('2.0.0'), Version('3.0.0'), Version('4.0.0')
    
    assert Interval.closed(v1, v2) | Interval.closed(v3, v4) == IntervalSet(Interval.closed(v1, v2), Interval.closed(v3, v4))
    assert Interval.closed(v1, v2) | Interval.closed(v3, v4) | Interval.closed(v2, v3) == IntervalSet(Interval.closed(v1, v4))
    
    assert (
        Interval.closed(1, 2) | Interval.closed(3, 4) | Interval.closed(4, 6) | Interval.closed(5, 6) | Interval.open(7, 7)
        == IntervalSet(Interval.closed(1, 2), Interval.closed(3, 6))
    )


def test_set_to_interval():
    v1, v2, v3, v4 = Version('1.0.0'), Version('2.0.0'), Version('3.0.0'), Version('4.0.0')
    
    assert IntervalSet(Interval.openclosed(v2, v3)).to_interval() == Interval.openclosed(v2, v3)
    assert IntervalSet(Interval.open(v1, v2), Interval.closed(v3, v4)).to_interval() == Interval.openclosed(v1, v4)
