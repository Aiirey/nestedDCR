"""
TODO: FIX KOMMENTARER
This module extends the MilestoneNoResponseDcrGraph class to include support for
nested groups and subprocesses within Dynamic Condition Response (DCR) Graphs.

The module adds functionality to handle hierarchical structures in DCR Graphs,
allowing for more complex process models with nested elements and subprocesses.

Classes:
    NestingSubprocessDcrGraph: Extends MilestoneNoResponseDcrGraph to include nested groups and subprocesses.

This class provides methods to manage and manipulate nested groups and subprocesses
within a DCR Graph, enhancing the model's ability to represent complex organizational
structures and process hierarchies.

References
----------
.. [1] Hildebrandt, T., Mukkamala, R.R., Slaats, T. (2012). Nested Dynamic Condition Response Graphs. In: Arbab, F., Sirjani, M. (eds) Fundamentals of Software Engineering. FSEN 2011. Lecture Notes in Computer Science, vol 7141. Springer, Berlin, Heidelberg. `DOI <https://doi.org/10.1007/978-3-642-29320-7_23>`_.

.. [2] Normann, H., Debois, S., Slaats, T., Hildebrandt, T.T. (2021). Zoom and Enhance: Action Refinement via Subprocesses in Timed Declarative Processes. In: Polyvyanyy, A., Wynn, M.T., Van Looy, A., Reichert, M. (eds) Business Process Management. BPM 2021. Lecture Notes in Computer Science(), vol 12875. Springer, Cham. `DOI <https://doi.org/10.1007/978-3-030-85469-0_12>`_.
"""
from pm4py.objects.dcr.extended.obj import ExtendedDcrGraph
from pm4py.objects.dcr.obj import Relations
from typing import Set, Dict
from collections import defaultdict

class NestedDict():
    def __init__(self):
        self.roots = {}
        self.allNodes = {}
    
    
    def __getitem__(self, key):
        return [node.key for node in self.allNodes[key]]
    

    def __setitem__(self, key, value):
        if key not in self.allNodes:
            subNodes = {}
            for val in value:
                newNode = {}
                subNodes[val] = newNode
                self.allNodes[val] = newNode
            self.roots[key] = subNodes
            self.allNodes[key] = subNodes
        else:
            for node in self.allNodes[key]:
                if node[key] not in value:
                    self.roots[node[key]] = node
                    self.allNodes[key].remove(node)

            subNodes = {}
            for val in value:
                if val not in self.allNodes:
                    newNode = {}
                    subNodes[val] = newNode
                    self.allNodes[val] = newNode
                elif val in self.roots:
                    subNodes[val] = self.allNodes[val]
                    del self.roots[val]
                else:                 
                    subNodes[val] = self.allNodes[val]
            if key in self.roots:
                self.roots[key] = subNodes
            self.allNodes[key] = subNodes


class NestedDcrGraph(ExtendedDcrGraph):
    """
    This class extends the MilestoneNoResponseDcrGraph to include nested groups, allowing for
    more complex structures in DCR Graphs.

    Attributes
    ----------
    self.__nestedgroups: Dict[str, Set[str]]
        A dictionary mapping group names to sets of event IDs within each group.
    self.__subprocesses: Dict[str, Set[str]]
        A dictionary mapping subprocess names to sets of event IDs within each subprocess.
    self.__nestedgroups_map: Dict[str, str]
        A dictionary mapping event IDs to their corresponding group names.

    Methods
    -------
    obj_to_template(self) -> dict:
        Converts the object to a template dictionary, including nested groups and subprocesses.

    """
    def __init__(self, template=None):
        super().__init__(template)
        self.__nested = NestedDict() if template is None or not isinstance(template['nestedgroups'], NestedDict) else template['nestedgroups']
        self.__constraints = defaultdict(lambda: [])

    def obj_to_template(self):
        res = super().obj_to_template()
        res['nestedgroups'] = self.__nested
        return res

    def _update_nests_fall_down(self, node):
        if len(self.nested.allNodes[node]) == 0:
            return
        for subNode in self.nested.allNodes[node]:
            for constraint in Relations:
                if node in getattr(self, constraint.value):
                    if subNode not in getattr(self, constraint.value):
                        getattr(self, constraint.value)[subNode] = getattr(self, constraint.value)[node]
                    else:
                        getattr(self, constraint.value)[subNode].extend(getattr(self, constraint.value)[node])
            self._update_nests_fall_down(subNode)

    def _update_nests_transfer(self, node):
        if len(self.nested.allNodes[node]) == 0:
            return
        for subNode in self.nested.allNodes[node]:
            for (key, constraint) in self.__constraints[node]:
                getattr(self, constraint)[key].append(subNode)
                self.__constraints[subNode].append((key, constraint))
            self._update_nests_transfer(subNode)


    def update_nests(self):
        for root in self.nested.roots:
            self._update_nests_fall_down(root)
        
        for constraint in Relations:
            for (key, subKeys) in getattr(self, constraint.value).items():
                for subKey in subKeys:
                    self.__constraints[subKey].append((key, constraint.value))
        
        for root in self.nested.roots:
            self._update_nests_transfer(root)

    @property
    def nested(self) -> NestedDict:
        return self.__nested
