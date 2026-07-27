
"""List unified models (read-only)."""

from workbuddy_enterprise import WorkBuddyClient


def main() -> None:
    with WorkBuddyClient.from_env() as client:
        resp = client.models.list(page_num=1, page_size=50)
        print("request_id=", resp.request_id, "total=", resp.data.total_count)
        for item in resp.data.items:
            print(item)


if __name__ == "__main__":
    main()
