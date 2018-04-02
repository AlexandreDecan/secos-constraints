import re
from functools import total_ordering
from itertools import combinations


@total_ordering
class Version:
    """
    Represent a three-component (+ optional prerelease tags) based version.
    If a string is provided, try to parse it using Version.from_string.
    """

    RE = r'^(?:v|V)?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<misc>.+)?$'
    
    def __init__(self, major_or_str, minor=None, patch=None, misc=None):
        if isinstance(major_or_str, str):
            version = Version.from_string(major_or_str)
            major_or_str = version.major
            minor = version.minor
            patch = version.patch
            misc = version.misc
        
        if isinstance(major_or_str, int) and isinstance(minor, int) and isinstance(patch, int):
            self.major = major_or_str
            self.minor = minor
            self.patch = patch
            self.misc = misc
        else:
            raise ValueError('Major, minor and patch components must be integers.')
        
    @staticmethod
    def from_string(string):
        """
        Parse given string and return a Version instance.
        """
        match = re.fullmatch(Version.RE, string)
        if match is not None:
            v = match.groupdict()
            return Version(int(v['major']), int(v['minor']), int(v['patch']), v['misc'])
        else:
            raise ValueError('Cannot parse {}'.format(string))
    
    def __eq__(self, other):
        if isinstance(other, Version):
            return (
                self.major == other.major
                and self.minor == other.minor
                and self.patch == other.patch
                and self.misc == other.misc
            )
        else:
            return NotImplemented
    
    def __hash__(self):
        return hash(self.minor) + hash(self.minor) + hash(self.patch)
    
    def __lt__(self, other):
        if isinstance(other, Version):
            if self.major < other.major:
                return True
            elif self.major == other.major:
                if self.minor < other.minor:
                    return True
                elif self.minor == other.minor:
                    if self.patch < other.patch:
                        return True
                    elif self.patch == other.patch:
                        if self.misc and other.misc:
                            return self.misc < other.misc
                        else:
                            # prereleases are always before non-prereleases
                            return self.misc and not other.misc
            return False
        else:
            return NotImplemented
    
    def __repr__(self):
        if self.major in [float('inf'), float('-inf')]:
            return str(self.major)
        else:
            return '{}.{}.{}{}'.format(self.major, self.minor, self.patch, self.misc if self.misc else '')


class Interval:
    """
    Represent an (open/closed) interval.
    Support intersection (&) and union (|).
    
    Inspiration taken from https://github.com/intiocean/pyinter
    """
    
    @total_ordering
    class _Infinity:
        """
        Use to represent positive or negative infinity.
        """
        def __init__(self, sign=True):
            self._sign = sign
        
        def __neg__(self):
            return self.__class__(not self._sign)
            
        def __lt__(self, o):
            return not self._sign
            
        def __gt__(self, o):
            return self._sign
            
        def __eq__(self, o):
            if isinstance(o, self.__class__):  # Exact type matching
                return o.sign == self._sign
            else:
                return False
                
        def __repr__(self):
            return '+inf' if self._sign else '-inf'
    
    OPEN = 0
    CLOSED = 1
    INF = _Infinity()
    
    def __init__(self, left, lower, upper, right):
        if lower > upper:
            raise ValueError('Bounds are not ordered correctly: {} must be before {}'.format(lower, upper))
        self.left = left
        self.lower = lower
        self.upper = upper
        self.right = right

    @staticmethod
    def open(lower, upper):
        return Interval(Interval.OPEN, lower, upper, Interval.OPEN)
        
    @staticmethod
    def closed(lower, upper):
        return Interval(Interval.CLOSED, lower, upper, Interval.CLOSED)
        
    @staticmethod
    def openclosed(lower, upper):
        return Interval(Interval.OPEN, lower, upper, Interval.CLOSED)
        
    @staticmethod
    def closedopen(lower, upper):
        return Interval(Interval.CLOSED, lower, upper, Interval.OPEN)

    def empty(self):
        return self.lower == self.upper and (self.left == Interval.OPEN or self.right == Interval.OPEN)

    def __eq__(self, other):
        if isinstance(other, Interval):
            return (
                self.left == other.left and
                self.lower == other.lower and
                self.upper == other.upper and
                self.right == other.right
            )
        else:
            return NotImplemented

    def overlaps(self, other, contiguous=False):
        """
        Return True if sets have any overlapping value.
        If 'contiguous' is set to True, it considers [1, 2) and [2, 3] as an
        overlap on value 2, not [1, 2) and (2, 3].
        """
        if self.lower > other.lower:
            first, second = other, self
        else:
            first, second = self, other
         
        # if second.empty():
        #    return False
         
        if first.upper == second.lower:
            if contiguous:
                return first.right == Interval.CLOSED or second.right == Interval.CLOSED
            else:
                return first.right == Interval.CLOSED and second.right == Interval.CLOSED
         
        return first.upper > second.lower

    def __and__(self, other):
        if isinstance(other, Interval):
            if self.lower == other.lower:
                lower = self.lower
                left = self.left if self.left == Interval.OPEN else other.left
            else:
                lower = max(self.lower, other.lower)
                left = self.left if lower == self.lower else other.left
                
            if self.upper == other.upper:
                upper = self.upper
                right = self.right if self.right == Interval.OPEN else other.right
            else:
                upper = min(self.upper, other.upper)
                right = self.right if upper == self.upper else other.right
            
            if lower <= upper:
                return Interval(left, lower, upper, right)
            else:
                return Interval(Interval.OPEN, lower, lower, Interval.OPEN)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, Interval):
            if self.overlaps(other, contiguous=True):
                if self.lower == other.lower:
                    lower = self.lower
                    left = self.left if self.left == Interval.OPEN else other.left
                else:
                    lower = min(self.lower, other.lower)
                    left = self.left if lower == self.lower else other.left
                    
                if self.upper == other.upper:
                    upper = self.upper
                    right = self.right if self.right == Interval.OPEN else other.right
                else:
                    upper = max(self.upper, other.upper)
                    right = self.right if upper == self.upper else other.right
                
                return Interval(left, lower, upper, right)
            else:
                return IntervalSet(self, other)
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.lower)
        
    def _contains_value(self, value):
        left = (value >= self.lower) if self.left == Interval.CLOSED else (value > self.lower)
        right = (value <= self.upper) if self.right == Interval.CLOSED else (value < self.upper)
        return left and right
            
    def __contains__(self, item):
        if isinstance(item, Interval):
            left = item.lower > self.lower or (item.lower == self.lower and (item.left == self.left or self.left == Interval.CLOSED))
            right = item.upper < self.upper or (item.upper == self.upper and (item.right == self.right or self.right == Interval.CLOSED))
            return left and right
        else:
            return self._contains_value(item)

    def __repr__(self):
        return '{}{},{}{}'.format(
            '[' if self.left == Interval.CLOSED else ']',
            repr(self.lower),
            repr(self.upper),
            ']' if self.right == Interval.CLOSED else '[',
        )


class IntervalSet:
    """
    Disjunction of intervals.
    """
    def __init__(self, interval, *intervals):
        self.intervals = set()
        
        self.intervals.add(interval)
        for interval in intervals:
            self.intervals.add(interval)
        
        self.clean()

    def clean(self):
        # Remove empty intervals
        self.intervals = {i for i in self.intervals if not i.empty()}
        
        # Remove intervals contained in other ones
        to_remove = set()
        for i1, i2 in combinations(self.intervals, 2):
            if i1 not in to_remove and i1 in i2:
                to_remove.add(i1)
        self.intervals = self.intervals.difference(to_remove)
        
        # Merge contiguous intervals
        to_remove = set()
        to_add = set()
        for i1, i2 in combinations(self.intervals, 2):
            if i1 not in to_remove and i2 not in to_remove and i1.overlaps(i2, contiguous=True):
                # Merge i1 and i2
                i3 = i1 | i2
                assert isinstance(i3, Interval)
                to_remove.add(i1)
                to_remove.add(i2)
                to_add.add(i3)
                
        # Do until nothing change
        self.intervals = self.intervals.difference(to_remove).union(to_add)
        if len(to_remove) + len(to_add) > 0:
            self.clean()
            
    def empty(self):
        return len(self.intervals) == 0

    def to_interval(self):
        first = next(iter(self.intervals))
        
        lower = first.lower
        left = first.left
        upper = first.upper
        right = first.right
        
        for interval in self.intervals:
            if interval.lower < lower:
                lower = interval.lower
                left = interval.left
            elif interval.lower == lower:
                if left == Interval.OPEN and interval.left == Interval.CLOSED:
                    left = Interval.CLOSED
                    
            if interval.upper > upper:
                upper = interval.upper
                right = interval.right
            elif interval.upper == upper:
                if right == Interval.OPEN and interval.right == Interval.CLOSED:
                    right = Interval.CLOSED
        
        return Interval(left, lower, upper, right)

    def __len__(self):
        return len(self.intervals)
    
    def __iter__(self):
        return iter(self.intervals)
    
    def __contains__(self, item):
        for i in self.intervals:
            if item in i:
                return True
        return False
        
    def __and__(self, other):
        if isinstance(other, (Interval, IntervalSet)):
            if isinstance(other, Interval):
                intervals = [other]
            else:
                intervals = list(other.intervals)
            new_intervals = []
            for interval in self.intervals:
                for o_interval in intervals:
                    new_intervals.append(interval & o_interval)
            return IntervalSet(*new_intervals)
        else:
            return NotImplemented
        
    def __or__(self, other):
        if isinstance(other, Interval):
            return self | IntervalSet(other)
        elif isinstance(other, IntervalSet):
            return IntervalSet(*(list(self.intervals) + list(other.intervals)))
        else:
            return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, Interval):
            return IntervalSet(other) == self
        elif isinstance(other, IntervalSet):
            return self.intervals == other.intervals
        else:
            return NotImplemented
    
    def __repr__(self):
        return ' | '.join(repr(i) for i in self.intervals)
