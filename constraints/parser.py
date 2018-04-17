import intervals as I
from versions import Version
from constraints import minor_interval, patch_interval, comparator_interval

from lark import Lark, InlineTransformer


class CargoParser(InlineTransformer):
    # https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
    grammar = """
    constraints: [constraint ("," constraint)*]

    constraint: [OP] version
    OP: "=" | "<=" | "<" | ">=" | ">" | "~" | "^"
    version: MAJOR ("." MINOR ("." PATCH ("-" MISC)?)?)?

    MAJOR: INT | "*"
    MINOR: INT | "*"
    PATCH: INT | "*"
    MISC: /[0-9A-Za-z-]+/

    %import common.INT
    %import common.WS
    %ignore WS
    """
    
    def __init__(self):
        self._parser = Lark(self.grammar, start='constraints')
        
    def parse(self, text):
        return self.transform(self._parser.parse(text))
        
    def constraints(self, *intervals):
        interval = I.closedopen(Version.FIRST, I.inf)
        for other_interval in intervals:
            interval = interval & other_interval
        return interval
        
    def constraint(self, op, version=None):
        if version is None:
            version = op
            op = '*'
            
        major, minor, patch = version
        
        if op == '*':
            if major == '*':
                return I.closedopen(Version.FIRST, I.inf)
            elif minor == '*':
                return minor_interval(Version(major, 0, 0))
            elif patch == '*':
                return patch_interval(Version(major, minor, 0))
            else:
                # Equivalent to ^x.y.z
                op = '^'
        
        if op == '^':
            if minor is None:
                # ^1 := >=1.0.0 <2.0.0
                # ^0 := >=0.0.0 <1.0.0
                return minor_interval(Version(major, 0, 0))
            elif patch is None:
                # ^1.2 := >=1.2.0 <2.0.0
                # ^0.0 := >=0.0.0 <0.1.0
                if major == 0:
                    return patch_interval(Version(major, minor, 0))
                else:
                    return minor_interval(Version(major, minor, 0))
            else:
                # ^1.2.3 := >=1.2.3 <2.0.0
                # ^0.2.3 := >=0.2.3 <0.3.0
                # ^0.0.3 := >=0.0.3 <0.0.4
                if major == 0:
                    if minor == 0:
                        return I.closedopen(Version(0, 0, patch), Version(0, 0, patch + 1))
                    else:
                        return patch_interval(Version(0, minor, patch))
                else:
                    return minor_interval(Version(major, minor, patch))
        elif op == '~':
            if minor is None:
                # ~1 := >=1.0.0 <2.0.0
                return minor_interval(Version(major, 0, 0))
            elif patch is None:
                # ~1.2 := >=1.2.0 <1.3.0
                return patch_interval(Version(major, minor, 0))
            else:
                # ~1.2.3 := >=1.2.3 <1.3.0
                return patch_interval(Version(major, minor, patch))
        else:
            # =, >=, >, <=, <, !=
            minor = 0 if minor is None else minor
            patch = 0 if patch is None else patch
            return comparator_interval(op, Version(major, minor, patch))
        
        assert False, (op, version)
            
    def version(self, major, minor=None, patch=None, misc=None):
        return tuple(
            int(x) if (x is not None and str.isdigit(x)) else x
            for x in (major, minor, patch)
        )
        
        
class RubyGemsParser(InlineTransformer):
    # http://guides.rubygems.org/patterns/#declaring-dependencies
    # https://www.devalot.com/articles/2012/04/gem-versions.html
    grammar = """
    constraints: [constraint ("," constraint)*]

    constraint: [OP] version
    OP: "!=" | "=" | "<=" | "<" | ">=" | ">" | "~>"
    version: MAJOR ("." MINOR ("." PATCH ("-" MISC)?)?)?

    MAJOR: INT
    MINOR: INT
    PATCH: INT
    MISC: /[0-9A-Za-z-]+/

    %import common.INT
    %import common.WS
    %ignore WS
    """
    
    def __init__(self):
        self._parser = Lark(self.grammar, start='constraints')
        
    def parse(self, text):
        return self.transform(self._parser.parse(text))
        
    def constraints(self, *intervals):
        interval = I.closedopen(Version.FIRST, I.inf)
        for other_interval in intervals:
            interval = interval & other_interval
        return interval
        
    def constraint(self, op, version=None):
        if version is None:
            version = op
            op = '='
            
        major, minor, patch = version
        if op == '~>':
            if patch is None:
                # ~>1.0 := >=1.0 <2.0
                return minor_interval(Version(major, minor, 0))
            else:
                # ~>1.5.0 := >=1.5.0 <1.6.0
                # ~>1.5.3 := >=1.5.3 <1.6.0
                return patch_interval(Version(major, minor, patch))
        else:
            # =, >=, >, <=, <, !=
            minor = 0 if minor is None else minor
            patch = 0 if patch is None else patch
            return comparator_interval(op, Version(major, minor, patch))
        
        assert False, (op, version)
            
    def version(self, major, minor=None, patch=None, misc=None):
        return tuple(
            int(x) if (x is not None and str.isdigit(x)) else x
            for x in (major, minor, patch)
        )
        
        
class PackagistParser(InlineTransformer):
    # https://getcomposer.org/doc/articles/versions.md#writing-version-constraints
    grammar = """
    disjunction: [conjunction ("||" conjunction)*]
    conjunction: constraint ([","] constraint)*

    constraint: [OP] version           -> constraint_operator
              | version "-" version    -> constraint_range
    OP: "!=" | "=" | "<=" | "<" | ">=" | ">" | "~" | "^"
    version: MAJOR ("." MINOR ("." PATCH ("-" MISC)?)?)?

    MAJOR: INT
    MINOR: INT | "*"
    PATCH: INT | "*"
    MISC: /[0-9A-Za-z-]+/

    %import common.INT
    %import common.WS
    %ignore WS
    """

    def __init__(self):
        self._parser = Lark(self.grammar, start='disjunction')

    def parse(self, text):
        return self.transform(self._parser.parse(text))

    def disjunction(self, *intervals):
        interval = I.empty()
        for other_interval in intervals:
            interval = interval | other_interval
        return interval

    def conjunction(self, *intervals):
        interval = I.closedopen(Version.FIRST, I.inf)
        for other_interval in intervals:
            interval = interval & other_interval
        return interval

    def constraint_range(self, left, right):
        lmajor, lminor, lpatch = left
        rmajor, rminor, rpatch = right
        
        lminor = 0 if lminor is None else lminor
        lpatch = 0 if lpatch is None else lpatch
        
        if rminor is None:
            # 1.0.0 - 2 := >=1.0.0 <3.0.0 because "2" becames "2.*.*"
            return I.closedopen(
                Version(lmajor, lminor, lpatch),
                Version(rmajor + 1, 0, 0)
            )
        elif rpatch is None:
            # 1.0.0 - 2.0 := >=1.0.0 <2.1 because "2.0" becames "2.0.*"
            return I.closedopen(
                Version(lmajor, lminor, lpatch),
                Version(rmajor, rminor + 1, 0)
            )
        else:
            # Inclusive
            return I.closed(Version(lmajor, lminor, lpatch), Version(rmajor, rminor, rpatch))

    def constraint_operator(self, op, version=None):
        if version is None:
            version = op
            op = '='
            
        major, minor, patch = version

        if minor == '*':
            return minor_interval(Version(major, 0, 0))
        elif patch == '*':
            return patch_interval(Version(major, minor, 0))
    
        if op == '^':
            if major == 0:
                # ^0.3 := >=0.3.0 < 0.4.0
                return patch_interval(Version(major, minor, patch or 0))
            else:
                return minor_interval(Version(major, minor, patch or 0))
        elif op == '~':
            if minor is None:
                # ~1 := ~1.0
                minor = 0
            
            if patch is None:
                # ~1.2 := >=1.2.0 <2.0.0
                return minor_interval(Version(major, minor, 0))
            else:
                # ~1.2.3 := >=1.2.3 <1.3.0
                return patch_interval(Version(major, minor, patch))
        else:
            # =, >=, >, <=, <, !=
            minor = 0 if minor is None else minor
            patch = 0 if patch is None else patch
            return comparator_interval(op, Version(major, minor, patch))

        assert False, (op, version)
        
    def version(self, major, minor=None, patch=None, misc=None):
        return tuple(
            int(x) if (x is not None and str.isdigit(x)) else x
            for x in (major, minor, patch)
        )
