# With unlicensed gratitude from https://github.com/Flushot/pydepend
import collections
from typing import Generic, List, Optional, TypeVar


class CyclicDependencyError(Exception):
    """
    Indicates that there was a cyclic dependency in the graph.
    e.g. a -> b -> c -> b
    """

    def __init__(self, dep):
        self.dep = dep
        self.message = "Cyclic dependency on %s" % dep


T = TypeVar("T")


class Dependency(Generic[T]):
    """
    Represents wrapped object :obj: in a dependency graph.

    Usage example:

    >>> a = Dependency('a')
    >>> b = Dependency('b')
    >>> c = Dependency('c')
    >>> d = Dependency('d')
    >>> a.depends_on([b, c])
    >>> b.depends_on(d)
    >>> a.ordered_deps
    ['d', 'b', 'c']
    """

    def __init__(self, obj: T, deps: Optional[List[T]] = None):
        """
        :obj: can be any object you'd like to wrap
        """
        self.obj = obj
        self._deps: List[T] = list(deps or [])
        self._ordered_dep_cache = None

    def depends_on(self, dep):
        self._ordered_dep_cache = None

        if isinstance(dep, collections.Sequence):
            map(self.depends_on, dep)
            return

        if not isinstance(dep, Dependency):
            raise ValueError("dep must be another Depdenency object")

        if dep not in self._deps:
            self._deps.append(dep)

    @property
    def direct_deps(self):
        """
        Returns a tuple of unordered, direct dependencies.
        Does not traverse depdendency graph.
        """
        return tuple(self._deps)

    @property
    def ordered_deps(self):
        """
        Returns a tuple of ordered dependencies by traversing dependency graph.
        Detected cycles will raise a CyclicDependencyError.
        """
        if self._ordered_dep_cache is not None:
            return self._ordered_dep_cache

        # DFS graph traversal
        def _order_deps(dep, ordered, visited):
            if dep is None or not isinstance(dep, Dependency):
                raise ValueError("dep must be a Dependency object but is %s" % type(dep))
            if dep in ordered:
                raise CyclicDependencyError(dep)

            if not dep.direct_deps:
                visited.add(dep)
                ordered.append(dep)
                return

            for parent in dep.direct_deps:
                if parent in visited:
                    continue
                visited.add(parent)
                _order_deps(parent, ordered, visited)

            visited.add(dep)
            if dep in ordered:
                raise CyclicDependencyError(dep)
            ordered.append(dep)

        self._ordered_dep_cache = []  # OrderedSet would be more ideal
        _order_deps(self, self._ordered_dep_cache, set())
        self._ordered_dep_cache = self._ordered_dep_cache[:-1]  # Pop original dep
        return tuple(self._ordered_dep_cache)

    def __lt__(self, other):
        if other == self:
            return False
        else:
            return other in self.ordered_deps

    def __gt__(self, other):
        if other == self:
            return False
        else:
            return other not in self.ordered_deps

    def __eq__(self, other):
        return self.obj == other.obj

    def __hash__(self):
        return hash(self.obj)

    def __iter__(self):
        for dep in self.ordered_deps:
            yield dep

    def __contains__(self, other):
        return other in self.ordered_deps

    def __len__(self):
        return len(self.ordered_deps)

    def __repr__(self):
        return repr(self.obj)

    def __str__(self):
        return str(self.obj)

    def __unicode__(self):
        return unicode(self.obj)
