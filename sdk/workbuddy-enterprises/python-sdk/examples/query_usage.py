
"""Query default quota (read-only)."""

from workbuddy_enterprise import WorkBuddyClient


def main() -> None:
    with WorkBuddyClient.from_env() as client:
        cycle = client.usage.get_quota_cycle()
        quota = client.usage.get_default_quota()
        print("cycle", cycle.data)
        print("default_quota", quota.data)
        print("request_id", quota.request_id)


if __name__ == "__main__":
    main()
