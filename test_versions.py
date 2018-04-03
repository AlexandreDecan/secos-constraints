import pytest
from versions import Version


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
