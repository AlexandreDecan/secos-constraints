import re
from functools import total_ordering


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
