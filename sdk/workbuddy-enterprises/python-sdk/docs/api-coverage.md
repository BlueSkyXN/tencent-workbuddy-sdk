# API coverage matrix

> **注意（2026-07-28）：** `contract_tested` 表示存在 Python mock 合同测试，且样例已按 YAML 关键字段校正。
> 这**不等于**全部 73 个 operation 已在真实企业环境 live 验证。

Status keys:

- `implemented`: real client method
- `contract_tested`: mock HTTP contract test
- `live_read_verified`: optional live read smoke
- `live_write_verified`: requires explicit authorization

Total operations: **73**

| Domain | Method | Path | SDK API | implemented | contract_tested | live_read_verified | live_write_verified |
|---|---|---|---|---|---|---|---|
| enterprise | GET | `/enterprises/{enterpriseId}/info` | `enterprise.get_info` | yes | yes | optional | no |
| enterprise | GET | `/enterprises/{enterpriseId}/license` | `enterprise.get_license` | yes | yes | no | no |
| users | GET | `/enterprises/{enterpriseId}/users` | `users.list` | yes | yes | no | no |
| users | POST | `/enterprises/{enterpriseId}/users/{userId}/update` | `users.update` | yes | yes | no | no |
| users | POST | `/enterprises/{enterpriseId}/users/{userId}/delete` | `users.delete` | yes | yes | no | no |
| users | POST | `/enterprises/{enterpriseId}/users/{userId}/password/update` | `users.update_password` | yes | yes | no | no |
| members | GET | `/enterprises/{enterpriseId}/openapi/members` | `members.list` | yes | yes | no | no |
| members | POST | `/enterprises/{enterpriseId}/openapi/members/add` | `members.add` | yes | yes | no | no |
| licenses | GET | `/enterprises/{enterpriseId}/openapi/license/overview` | `licenses.overview` | yes | yes | no | no |
| licenses | POST | `/enterprises/{enterpriseId}/openapi/license/members/query` | `licenses.query_members` | yes | yes | no | no |
| licenses | POST | `/enterprises/{enterpriseId}/openapi/license/members/grant` | `licenses.grant` | yes | yes | no | no |
| licenses | POST | `/enterprises/{enterpriseId}/openapi/license/members/revoke` | `licenses.revoke` | yes | yes | no | no |
| usage | GET | `/enterprises/{enterpriseId}/openapi/usage/quota-cycle` | `usage.get_quota_cycle` | yes | yes | no | no |
| usage | GET | `/enterprises/{enterpriseId}/openapi/usage/default-quota` | `usage.get_default_quota` | yes | yes | optional | no |
| usage | POST | `/enterprises/{enterpriseId}/openapi/usage/default-quota/update` | `usage.update_default_quota` | yes | yes | no | no |
| usage | POST | `/enterprises/{enterpriseId}/openapi/usage/members/query` | `usage.query_members` | yes | yes | no | no |
| usage | POST | `/enterprises/{enterpriseId}/openapi/usage/members/limit-query` | `usage.query_member_limits` | yes | yes | no | no |
| usage | POST | `/enterprises/{enterpriseId}/openapi/usage/members/quota/update` | `usage.update_member_quota` | yes | yes | no | no |
| usage | POST | `/enterprises/{enterpriseId}/openapi/usage/departments/{departmentId}/quota/update` | `usage.update_department_quota` | yes | yes | no | no |
| usage | POST | `/enterprises/{enterpriseId}/openapi/usage/members/detail` | `usage.query_member_details` | yes | yes | no | no |
| groups | GET | `/enterprises/{enterpriseId}/openapi/groups` | `groups.list` | yes | yes | no | no |
| groups | GET | `/enterprises/{enterpriseId}/openapi/groups/{groupId}` | `groups.get` | yes | yes | no | no |
| groups | GET | `/enterprises/{enterpriseId}/openapi/groups/{groupId}/members` | `groups.list_members` | yes | yes | no | no |
| groups | POST | `/enterprises/{enterpriseId}/openapi/groups/{groupId}/members/add` | `groups.add_members` | yes | yes | no | no |
| groups | POST | `/enterprises/{enterpriseId}/openapi/groups/{groupId}/members/remove` | `groups.remove_members` | yes | yes | no | no |
| groups | POST | `/enterprises/{enterpriseId}/openapi/groups/{groupId}/members/replace` | `groups.replace_members` | yes | yes | no | no |
| models | GET | `/enterprises/{enterpriseId}/openapi/models/builtin` | `models.list_builtin` | yes | yes | no | no |
| models | POST | `/enterprises/{enterpriseId}/openapi/models/builtin/{modelId}/toggle` | `models.set_builtin_enabled` | yes | yes | no | no |
| models | POST | `/enterprises/{enterpriseId}/openapi/models/builtin/{modelId}/visibility` | `models.set_builtin_visibility` | yes | yes | no | no |
| models | GET | `/enterprises/{enterpriseId}/openapi/models/custom` | `models.list_custom` | yes | yes | no | no |
| models | POST | `/enterprises/{enterpriseId}/openapi/models/custom` | `models.create_custom` | yes | yes | no | no |
| models | GET | `/enterprises/{enterpriseId}/openapi/models/custom/{modelId}` | `models.get_custom` | yes | yes | no | no |
| models | POST | `/enterprises/{enterpriseId}/openapi/models/custom/{modelId}/delete` | `models.delete_custom` | yes | yes | no | no |
| models | POST | `/enterprises/{enterpriseId}/openapi/models/custom/{modelId}/visibility` | `models.set_custom_visibility` | yes | yes | no | no |
| models | GET | `/enterprises/{enterpriseId}/openapi/models/available` | `models.list_available` | yes | yes | no | no |
| models | GET | `/enterprises/{enterpriseId}/openapi/models` | `models.list` | yes | yes | optional | no |
| models | GET | `/enterprises/{enterpriseId}/openapi/models/{modelId}` | `models.get` | yes | yes | no | no |
| models | POST | `/enterprises/{enterpriseId}/openapi/models/{modelId}/toggle` | `models.set_enabled` | yes | yes | no | no |
| models | POST | `/enterprises/{enterpriseId}/openapi/models/{modelId}/visibility` | `models.set_visibility` | yes | yes | no | no |
| skills | GET | `/enterprises/{enterpriseId}/openapi/skills` | `skills.list` | yes | yes | optional | no |
| skills | POST | `/enterprises/{enterpriseId}/openapi/skills` | `skills.create` | yes | yes | no | no |
| skills | GET | `/enterprises/{enterpriseId}/openapi/skills/{skillRef}` | `skills.get` | yes | yes | no | no |
| skills | POST | `/enterprises/{enterpriseId}/openapi/skills/{skillRef}/update` | `skills.update` | yes | yes | no | no |
| skills | POST | `/enterprises/{enterpriseId}/openapi/skills/{skillRef}/delete` | `skills.delete` | yes | yes | no | no |
| skills | POST | `/enterprises/{enterpriseId}/openapi/skills/{skillRef}/toggle` | `skills.set_enabled` | yes | yes | no | no |
| skills | POST | `/enterprises/{enterpriseId}/openapi/skills/{skillRef}/visibility` | `skills.set_visibility` | yes | yes | no | no |
| skills | GET | `/enterprises/{enterpriseId}/openapi/skills/{skillRef}/visibility` | `skills.get_visibility` | yes | yes | no | no |
| skill_categories | GET | `/enterprises/{enterpriseId}/openapi/skill-categories` | `skill_categories.list` | yes | yes | no | no |
| skill_categories | POST | `/enterprises/{enterpriseId}/openapi/skill-categories` | `skill_categories.create` | yes | yes | no | no |
| skill_categories | POST | `/enterprises/{enterpriseId}/openapi/skill-categories/{id}/update` | `skill_categories.update` | yes | yes | no | no |
| skill_categories | POST | `/enterprises/{enterpriseId}/openapi/skill-categories/{id}/delete` | `skill_categories.delete` | yes | yes | no | no |
| skill_categories | POST | `/enterprises/{enterpriseId}/openapi/skill-categories/reorder` | `skill_categories.reorder` | yes | yes | no | no |
| experts | GET | `/enterprises/{enterpriseId}/openapi/experts` | `experts.list` | yes | yes | no | no |
| experts | POST | `/enterprises/{enterpriseId}/openapi/experts` | `experts.create` | yes | yes | no | no |
| experts | GET | `/enterprises/{enterpriseId}/openapi/experts/{expertRef}` | `experts.get` | yes | yes | no | no |
| experts | POST | `/enterprises/{enterpriseId}/openapi/experts/{expertRef}/update` | `experts.update` | yes | yes | no | no |
| experts | POST | `/enterprises/{enterpriseId}/openapi/experts/{expertRef}/delete` | `experts.delete` | yes | yes | no | no |
| experts | POST | `/enterprises/{enterpriseId}/openapi/experts/{expertRef}/toggle` | `experts.set_enabled` | yes | yes | no | no |
| experts | POST | `/enterprises/{enterpriseId}/openapi/experts/{expertRef}/visibility` | `experts.set_visibility` | yes | yes | no | no |
| experts | GET | `/enterprises/{enterpriseId}/openapi/experts/{expertRef}/visibility` | `experts.get_visibility` | yes | yes | no | no |
| expert_categories | GET | `/enterprises/{enterpriseId}/openapi/expert-categories` | `expert_categories.list` | yes | yes | no | no |
| expert_categories | POST | `/enterprises/{enterpriseId}/openapi/expert-categories` | `expert_categories.create` | yes | yes | no | no |
| expert_categories | POST | `/enterprises/{enterpriseId}/openapi/expert-categories/{id}/update` | `expert_categories.update` | yes | yes | no | no |
| expert_categories | POST | `/enterprises/{enterpriseId}/openapi/expert-categories/{id}/delete` | `expert_categories.delete` | yes | yes | no | no |
| expert_categories | POST | `/enterprises/{enterpriseId}/openapi/expert-categories/reorder` | `expert_categories.reorder` | yes | yes | no | no |
| analytics | GET | `/enterprises/{enterpriseId}/metrics/download_url/v2` | `analytics.metrics_download_url_v2` | yes | yes | no | no |
| analytics | GET | `/enterprises/{enterpriseId}/metrics/download_url` | `analytics.metrics_download_url` | yes | yes | no | no |
| analytics | GET | `/enterprises/{enterpriseId}/metrics` | `analytics.metrics` | yes | yes | no | no |
| analytics | POST | `/enterprises/{enterpriseId}/dashboard/analytics/activity` | `analytics.activity` | yes | yes | no | no |
| analytics | POST | `/enterprises/{enterpriseId}/dashboard/analytics/dialog` | `analytics.dialog` | yes | yes | no | no |
| analytics | POST | `/enterprises/{enterpriseId}/dashboard/analytics/completion` | `analytics.completion` | yes | yes | no | no |
| analytics | POST | `/enterprises/{enterpriseId}/dashboard/analytics/generation` | `analytics.generation` | yes | yes | no | no |
| analytics | POST | `/enterprises/{enterpriseId}/dashboard/member/data` | `analytics.member_data` | yes | yes | no | no |

Note: `contract_tested=yes` for all 73 does **not** mean live enterprise verification.
