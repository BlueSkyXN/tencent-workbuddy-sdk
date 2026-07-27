
from workbuddy_enterprise.pagination import page_query, parse_page


def test_page_query_styles():
    assert page_query(page=2, page_size=10) == {"page": 2, "pageSize": 10}
    assert page_query(page_num=3, page_size=50) == {"pageNum": 3, "pageSize": 50}
    assert page_query(page_token="abc") == {"pageToken": "abc"}


def test_parse_page_fields():
    page = parse_page(
        {
            "items": [{"id": 1}],
            "totalCount": 1,
            "pageNum": 1,
            "pageSize": 20,
            "nextPageToken": "n1",
        }
    )
    assert page.items[0]["id"] == 1
    assert page.total_count == 1
    assert page.page_num == 1
    assert page.next_page_token == "n1"
