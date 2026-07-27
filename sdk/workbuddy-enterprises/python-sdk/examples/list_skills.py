
"""List custom enterprise skills (read-only)."""

from workbuddy_enterprise import WorkBuddyClient
from workbuddy_enterprise.types import SkillSource


def main() -> None:
    with WorkBuddyClient.from_env() as client:
        resp = client.skills.list(source=SkillSource.CUSTOM, page_num=1, page_size=50)
        print("request_id=", resp.request_id, "total=", resp.data.total_count)
        for skill in resp.data.items:
            print(f"{skill.name}\t{skill.display_name}\t{skill.version}\tenabled={skill.enabled}")


if __name__ == "__main__":
    main()
