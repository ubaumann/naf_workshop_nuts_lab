from pytest import  FixtureRequest
from nuts.context import NutsContext, NornirNutsContext
from nuts.helpers.result import NutsResult

def pytest_nuts_single_result(request: FixtureRequest, nuts_ctx: NutsContext, result: NutsResult) -> None:
    if isinstance(nuts_ctx, NornirNutsContext):
        # This is a Nornir context
        if eos := nuts_ctx.nornir.inventory.groups.get("eos"):
            if eos.platform == "mock":
                request.node.user_properties.append(("mocked", "True"))
                return
        request.node.user_properties.append(("mocked", "False"))
