import intervals as I
from .versions import Version


def empty(interval):
    return interval.is_empty()
    

def upper_bounded(interval):
    if isinstance(interval, I.Interval):
        return upper_bounded(interval.to_atomic())
    elif isinstance(interval, I.AtomicInterval):
        return interval.upper != I.inf
    else:
        raise TypeError('Parameter must be an Interval or an AtomicInterval instance.')


def lower_bounded(interval):
    if isinstance(interval, I.Interval):
        return lower_bounded(interval.to_atomic())
    elif isinstance(interval, I.AtomicInterval):
        return interval.lower != Version.FIRST
    else:
        raise TypeError('Parameter must be an Interval or an AtomicInterval instance.')


def strict(interval):
    if isinstance(interval, I.Interval):
        try:
            return strict(interval[0])
        except IndexError:  # empty interval
            return False
    elif isinstance(interval, I.AtomicInterval):
        return not allows_patch(interval, soft=False)
    else:
        raise TypeError('Parameter must be an Interval or an AtomicInterval instance.')
    

def allows_major(interval, soft=True):
    if isinstance(interval, I.Interval):
        try:
            interval = I.Interval(interval[-1]) if soft else interval
        except IndexError:  # empty interval
            return False
        return any(allows_major(i, soft) for i in interval)
    elif isinstance(interval, I.AtomicInterval):
        inc = float('inf') if soft else 1 + int(interval.left == I.OPEN)
        next_version = Version(interval.lower.major + inc, 0, 0)
        return next_version in interval
    else:
        raise TypeError('Parameter must be an Interval or an AtomicInterval instance.')
    

def allows_minor(interval, soft=True):
    if isinstance(interval, I.Interval):
        try:
            interval = I.Interval(interval[-1]) if soft else interval
        except IndexError:  # empty interval
            return False
        return any(allows_minor(i, soft) for i in interval)
    elif isinstance(interval, I.AtomicInterval):
        inc = float('inf') if soft else 1 + int(interval.left == I.OPEN)
        next_version = Version(interval.lower.major, interval.lower.minor + inc, 0)
        return next_version in interval
    else:
        raise TypeError('Parameter must be an Interval or an AtomicInterval instance.')


def allows_patch(interval, soft=True):
    if isinstance(interval, I.Interval):
        try:
            interval = I.Interval(interval[-1]) if soft else interval
        except IndexError:  # empty interval
            return False
        return any(allows_patch(i, soft) for i in interval)
    elif isinstance(interval, I.AtomicInterval):
        inc = float('inf') if soft else 1 + int(interval.left == I.OPEN)
        next_version = Version(interval.lower.major, interval.lower.minor, interval.lower.patch + inc)
        return next_version in interval
    else:
        raise TypeError('Parameter must be an Interval or an AtomicInterval instance.')


def dev(interval):
    if isinstance(interval, I.Interval):
        # Whyt not all(dev(i) for i in interval)?
        # .. because it returns True if interval is empty.
        return not any([not dev(i) for i in interval])
    elif isinstance(interval, I.AtomicInterval):
        return interval <= I.closedopen(Version(0, 0, 0), Version(1, 0, 0))
        # (
        #     interval.upper.major == 0 or (
        #         interval.upper.major == 1
        #         and interval.upper.minor == 0
        #         and interval.upper.patch == 0
        #         and interval.right == I.OPEN
        #     )
        # )
    else:
        raise TypeError('Parameter must be an Interval or an AtomicInterval instance.')


def allows_all_compatible(interval, semver=False):
    if dev(interval):
        if semver:
            return True
        else:
            return allows_patch(interval)
    else:
        return allows_minor(interval) and allows_patch(interval)

    
def allows_compatible(interval, semver=False):
    if dev(interval):
        if semver:
            return True
        else:
            return allows_patch(interval)
    else:
        return allows_minor(interval) or allows_patch(interval)

    
def allows_incompatible(interval, semver=False):
    if dev(interval):
        if semver:
            return allows_major(interval) or allows_minor(interval) or allows_patch(interval)
        else:
            return allows_major(interval) or allows_minor(interval)
    else:
        return allows_major(interval)


def allows_compatible_only(interval, semver=False):
    return allows_compatible(interval, semver) and not allows_incompatible(interval, semver)
    
    
def allows_all_compatible_only(interval, semver=False):
    return allows_all_compatible(interval, semver) and not allows_incompatible(interval, semver)
    

def patch_interval(version):
    return I.closedopen(
        version,
        Version(version.major, version.minor + 1, 0)
    )
    
    
def minor_interval(version):
    return I.closedopen(
        version,
        Version(version.major + 1, 0, 0)
    )
    
    
def comparator_interval(op, version):
    if op == '=':
        return I.singleton(version)
    if op == '<':
        return I.closedopen(Version.FIRST, version)
    if op == '<=':
        return I.closed(Version.FIRST, version)
    if op == '>':
        return I.open(version, I.inf)
    if op == '>=':
        return I.closedopen(version, I.inf)
    if op == '!=':
        return I.closedopen(Version.FIRST, version) | I.openclosed(version, I.inf)
