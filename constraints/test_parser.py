import pytest
import intervals as I

from .parser import CargoParser, RubyGemsParser, PackagistParser, NPMParser
from .versions import Version


basic_examples = [
    ('', '[0.0.0,+inf)'),
    ('=1.2.3', '[1.2.3]'),
    ('>1.2.3', '(1.2.3,+inf)'),
    ('>=1.2.3', '[1.2.3,+inf)'),
    ('<1.2.3', '[0.0.0,1.2.3)'),
    ('<=1.2.3', '[0.0.0,1.2.3]'),
]


def test_cargoparser():
    # https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
    examples = basic_examples + [
        ('^1.2.3', '[1.2.3,2.0.0)'),
        ('^1.2', '[1.2.0,2.0.0)'),
        ('^1', '[1.0.0,2.0.0)'),
        ('^0.2.3', '[0.2.3,0.3.0)'),
        ('^0.0.3', '[0.0.3,0.0.4)'),
        ('^0.0', '[0.0.0,0.1.0)'),
        ('^0', '[0.0.0,1.0.0)'),
        ('~1.2.3', '[1.2.3,1.3.0)'),
        ('~1.2', '[1.2.0,1.3.0)'),
        ('~1', '[1.0.0,2.0.0)'),
        ('*', '[0.0.0,+inf)'),
        ('1.*', '[1.0.0,2.0.0)'),
        ('1.2.*', '[1.2.0,1.3.0)'),
    ]
    
    parser = CargoParser()
    for constraint, result in examples:
        assert repr(parser.parse(constraint)) == result


def test_rubygemsparser():
    # http://guides.rubygems.org/patterns/#declaring-dependencies
    # https://www.devalot.com/articles/2012/04/gem-versions.html
    examples = basic_examples + [
        ('~> 1.0', '[1.0.0,2.0.0)'),
        ('~> 1.5', '[1.5.0,2.0.0)'),
        ('~> 1.5.0', '[1.5.0,1.6.0)'),
        ('~> 1.5.3', '[1.5.3,1.6.0)'),
    ]
    
    parser = RubyGemsParser()
    for constraint, result in examples:
        assert repr(parser.parse(constraint)) == result


def test_packagistparser():
    # https://getcomposer.org/doc/articles/versions.md#writing-version-constraints
    examples = basic_examples + [
        ('1.0.2', '[1.0.2]'),
        ('>=1.0', '[1.0.0,+inf)'),
        ('>=1.0 <2.0', '[1.0.0,2.0.0)'),
        ('>=1.0 <1.1 || >=1.2', '[1.0.0,1.1.0) | [1.2.0,+inf)'),
        ('1.0 - 2.0', '[1.0.0,2.1.0)'),
        ('1.0.0 - 2.1.0', '[1.0.0,2.1.0]'),
        ('1.0.*', '[1.0.0,1.1.0)'),
        ('~1.2', '[1.2.0,2.0.0)'),
        ('~1.2.3', '[1.2.3,1.3.0)'),
        ('^1.2.3', '[1.2.3,2.0.0)'),
        ('^0.3', '[0.3.0,0.4.0)'),
        ('^0', '[0.0.0,0.1.0)'),
        ('^1', '[1.0.0,2.0.0)'),
        ('1 - 2', '[1.0.0,3.0.0)')
    ]
    
    parser = PackagistParser()
    for constraint, result in examples:
        assert repr(parser.parse(constraint)) == result, constraint


def test_npmparser():
    # https://docs.npmjs.com/misc/semver
    examples = basic_examples + [
        ('>=1.2.7', '[1.2.7,+inf)'),
        ('>=1.2.7 <1.3.0', '[1.2.7,1.3.0)'),
        ('1.2.7 || >=1.2.9 <2.0.0', '[1.2.7] | [1.2.9,2.0.0)'),
        ('1.2.3 - 2.3.4', '[1.2.3,2.3.4]'),
        ('1.2 - 2.3.4', '[1.2.0,2.3.4]'),
        ('1.2.3 - 2.3', '[1.2.3,2.4.0)'),
        ('1.2.3 - 2', '[1.2.3,3.0.0)'),
        ('*', '[0.0.0,+inf)'),
        ('1.x', '[1.0.0,2.0.0)'),
        ('1.2.x', '[1.2.0,1.3.0)'),
        ('1', '[1.0.0,2.0.0)'),
        ('1.2', '[1.2.0,1.3.0)'),
        ('~1.2.3', '[1.2.3,1.3.0)'),
        ('~1.2', '[1.2.0,1.3.0)'),
        ('~1', '[1.0.0,2.0.0)'),
        ('~0.2.3', '[0.2.3,0.3.0)'),
        ('~0.2', '[0.2.0,0.3.0)'),
        ('~0', '[0.0.0,1.0.0)'),
        ('^1.2.3', '[1.2.3,2.0.0)'),
        ('^0.2.3', '[0.2.3,0.3.0)'),
        ('^0.0.3', '[0.0.3,0.0.4)'),
        ('^1.2.x', '[1.2.0,2.0.0)'),
        ('^0.0.x', '[0.0.0,0.1.0)'),
        ('^0.0', '[0.0.0,0.1.0)'),
        ('^1.x', '[1.0.0,2.0.0)'),
        ('^0.x', '[0.0.0,1.0.0)'),
    ]
    
    parser = NPMParser()
    for constraint, result in examples:
        assert repr(parser.parse(constraint)) == result, constraint
