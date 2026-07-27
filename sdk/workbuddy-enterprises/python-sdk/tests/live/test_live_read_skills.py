
import os

import pytest

from workbuddy_enterprise import WorkBuddyClient
from workbuddy_enterprise.types import SkillSource

pytestmark = pytest.mark.live


@pytest.mark.skipif(
    not os.environ.get("WORKBUDDY_LIVE"),
    reason="Set WORKBUDDY_LIVE=1 and credentials to enable live tests",
)
def test_live_list_custom_skills():
    with WorkBuddyClient.from_env() as client:
        resp = client.skills.list(source=SkillSource.CUSTOM, page_num=1, page_size=20)
    assert resp.code == 0
    assert resp.request_id is not None
