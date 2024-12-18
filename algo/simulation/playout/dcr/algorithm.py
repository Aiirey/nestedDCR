'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from pm4py.algo.simulation.playout.dcr.variants import classic
from pm4py.util import exec_utils
from enum import Enum
from pm4py.objects.dcr.obj import DcrGraph, Marking
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC
VERSIONS = {Variants.CLASSIC}


def apply(dcr: DcrGraph, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> EventLog:
    """
    Do the playout of a Petrinet generating a log

    Parameters
    -----------
    dcr
        DCR graph to play-out
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to use:
            - Variants.BASIC_PLAYOUT: generates random traces from the model
    """
    return exec_utils.get_variant(variant).apply(dcr, parameters=parameters)
