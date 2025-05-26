from typing import Dict, Callable, List

import json
import pytest
from nornir.core.task import MultiResult, Result
from nornir_napalm.plugins.tasks import napalm_cli

from nuts.context import NornirNutsContext
from nuts.helpers.result import AbstractHostResultExtractor, NutsResult


class IsisExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> int:
        count = 0

        result = self._simple_extract(single_result)["show isis neighbors | json"]
        json_data = json.loads(result)

        instances = (
            json_data.get("vrfs", {}).get("default", {}).get("isisInstances", {})
        )
        for instance in instances.values():
            neighbors = instance.get("neighbors", {})
            for adjacencies in neighbors.values():
                for adjacency in adjacencies.get("adjacencies", []):
                    if adjacency.get("state") == "up":
                        count += 1
        return count


class IsisContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return napalm_cli

    def nuts_arguments(self) -> Dict[str, List[str]]:
        return {"commands": ["show isis neighbors | json"]}

    def nuts_extractor(self) -> IsisExtractor:
        return IsisExtractor(self)


CONTEXT = IsisContext


class TestIsisNeighborsCount:
    @pytest.mark.nuts("neighbor_count")
    def test_username(self, single_result: NutsResult, neighbor_count: int) -> None:
        assert neighbor_count == single_result.result, (
            f"Expected neighbor count {neighbor_count} does not match the result {single_result.result}"
        )
