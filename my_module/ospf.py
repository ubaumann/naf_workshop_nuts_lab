from typing import Dict, Callable, List

import json
import pytest
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_cli

from nuts.context import NornirNutsContext
from nuts.helpers.result import AbstractHostResultExtractor, NutsResult

from pprint import pprint as pp

class OspfExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> int:
        count = 0

        result = self._simple_extract(single_result)[
            "show ip ospf neighbor summary | json"
        ]
        json_data = json.loads(result)
        pp(json_data)
        ospf_inst = json_data.get("vrfs", {}).get("default", {}).get("instList", {})
        pp(ospf_inst)
        for ospf in ospf_inst.values():
            count += ospf.get("neighborSummary", {}).get("numFull", 0)
        return count


class OspfContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_cli

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"commands": ["show ip ospf neighbor summary | json"]}

    def nuts_extractor(self) -> OspfExtractor:
        return OspfExtractor(self)


CONTEXT = OspfContext


class TestOspfNeighborsCount:
    @pytest.mark.nuts("neighbor_count")
    def test_username(self, single_result: NutsResult, neighbor_count: int) -> None:
        assert neighbor_count == single_result.result, (
            f"Expected neighbor count {neighbor_count} does not match the result {single_result.result}"
        )
