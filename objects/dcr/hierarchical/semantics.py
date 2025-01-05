from typing import Set

from pm4py.objects.dcr.extended.semantics import ExtendedSemantics


class HierarchicalDcrSemantics(ExtendedSemantics):
    @classmethod
    def enabled(cls, graph):
        res = set(graph.marking.included)

        for e in set(res):
            super_conditions = cls.get_super_constraints(graph, e, "conditions")
            conditions = cls.get_nested_constraints(graph, super_conditions)
            if len(conditions.intersection(graph.marking.included.difference(
                    graph.marking.executed))) > 0:
                res.discard(e)
        
        for e in set(res):
            super_milestones = cls.get_super_constraints(graph, e, "milestones")
            milestones = cls.get_nested_constraints(graph, super_milestones)
            if len(milestones.intersection(
                    graph.marking.included.intersection(graph.marking.pending))) > 0:
                res.discard(e)
        return res

    @classmethod
    def execute(cls, graph, event):
        if event in graph.marking.pending:
            graph.marking.pending.discard(event)
        graph.marking.executed.add(event)

        for child in cls.get_super_constraints(graph, event, "excludes"):
            cls.update_nested_markings(graph, child, "included", "discard")

        for child in cls.get_super_constraints(graph, event, "includes"):
            cls.update_nested_markings(graph, child, "included", "add")

        for child in cls.get_super_constraints(graph, event, "responses"):
            cls.update_nested_markings(graph, child, "pending", "add")

    @classmethod
    def update_nested_markings(cls, graph, event, constraint, action):
        if event not in graph.nestedgroups: # nochildren left
            getattr(getattr(graph.marking, constraint), action)(event)
            return
        for child in graph.nestedgroups[event]:
            cls.update_nested_markings(graph, child, constraint, action)

    @classmethod
    def get_super_constraints(cls, graph, event, constraint):
        constraints = set()
        if event in getattr(graph, constraint):
            constraints = constraints.union(getattr(graph, constraint)[event])
        if event in graph.nestedgroups_map:
            constraints = constraints.union(cls.get_super_constraints(graph, graph.nestedgroups_map[event], constraint))
        return constraints

    @classmethod
    def get_nested_constraints(cls, graph, constraints):
        nested_constraints = set()
        for event in constraints:
            nested_constraints = nested_constraints.union(cls.get_nested_atomic_events(graph, event))
        return nested_constraints

    @classmethod
    def get_nested_atomic_events(cls, graph, event):
        if event not in graph.nestedgroups:
            return set([event])
        nested_atomic_events = set()
        for e in graph.nestedgroups[event]:
            nested_atomic_events = nested_atomic_events.union(cls.get_nested_atomic_events(graph, e))
        return nested_atomic_events
