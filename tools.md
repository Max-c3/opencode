# Tools

This file documents the MCP tools currently callable from this workspace.

Source of truth:

- Runtime exposure: `agentic-tools-mcp/agentic_tools_mcp/server_factory.py`
- Platform contracts: `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-*/tool_catalog.json`
- Runtime policy: `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-*/policy/capabilities.yaml`

## How To Read This File

- MCP tools expose the logical tool id with `.` replaced by `_`. Example: `ashby.get_recent_hires` becomes `ashby_get_recent_hires`.
- Read tool responses have this envelope:
  - `output`: tool-specific payload documented below
  - `summary`: short human summary
  - `verification`: runtime verification result
- Write tool responses have this envelope:
  - `output`: committed business result
  - `summary`: short execution summary
  - `verification`: post-execution verification result
  - `receipt`: receipt metadata with `receipt_id`, `tool_id`, `status`, `idempotency_key`, and `created_at`
- For inputs named `profiles` or `seed_profiles`, include identity fields like `email`, `linkedin`, or `candidate_id` whenever possible. Those are the main keys used for deduplication.

## Current Callable Names

### Ashby

- `ashby_audit_hire_coverage`
- `ashby_get_recent_hires`
- `ashby_get_recent_technical_hires`
- `ashby_search_hires`

### Gem

- `gem_find_candidates`
- `gem_find_projects`
- `gem_get_candidate`
- `gem_get_project`
- `gem_get_sequence`
- `gem_list_candidate_notes`
- `gem_list_candidates`
- `gem_list_custom_field_options`
- `gem_list_custom_fields`
- `gem_list_project_candidates`
- `gem_list_project_field_options`
- `gem_list_project_fields`
- `gem_list_project_membership_log`
- `gem_list_projects`
- `gem_list_sequences`
- `gem_list_uploaded_resumes`
- `gem_list_users`
- `gem_add_candidate_note`
- `gem_add_custom_field_options`
- `gem_add_profiles_to_project`
- `gem_create_candidate`
- `gem_create_custom_field`
- `gem_create_project_field_option`
- `gem_create_project_field`
- `gem_create_project`
- `gem_remove_candidates_from_project`
- `gem_set_custom_value`
- `gem_set_project_field_value`
- `gem_update_candidate`
- `gem_update_custom_field_option`
- `gem_update_project_field_option`
- `gem_update_project`
- `gem_upload_resume`

### Harmonic

- `harmonic_enrich_company`
- `harmonic_enrich_person`
- `harmonic_find_similar_profiles`
- `harmonic_get_employees_by_company`
- `harmonic_get_people_saved_search_results_with_metadata`
- `harmonic_get_team_network_connections_to_company`
- `harmonic_search_companies_by_natural_language`

### Metaview

- `metaview_enrich_candidate_profiles`

### LinkedIn Profile Changes

- `linkedin_profile_changes_watchlist_upsert`
- `linkedin_profile_changes_watchlist_list`
- `linkedin_profile_changes_profile_list_upsert`
- `linkedin_profile_changes_profile_list_list`
- `linkedin_profile_changes_profile_list_rename`
- `linkedin_profile_changes_profile_list_members_list`
- `linkedin_profile_changes_profile_list_members_upsert`
- `linkedin_profile_changes_profile_list_members_remove`
- `linkedin_profile_changes_browser_auth_status`
- `linkedin_profile_changes_browser_auth_bootstrap`
- `linkedin_profile_changes_collect_snapshot`
- `linkedin_profile_changes_collect_due_snapshots`
- `linkedin_profile_changes_collect_profile_list_baseline`
- `linkedin_profile_changes_collect_profile_list_check`
- `linkedin_profile_changes_get_recent_changes`
- `linkedin_profile_changes_get_profile_history`
- `linkedin_profile_changes_diff_latest`

## Ashby

### `ashby_audit_hire_coverage`

What it does:

- Audits Ashby hire data quality and tells you how complete the sampled records are.

Inputs:

- `sample_size`: how many hires to sample. Default `50`, max `200`.
- `max_scan_pages`: optional page budget for the upstream search.
- `require_fields`: fields you care about being present, such as `candidate_id`, `name`, `email`, `linkedin`, `job_title`, `hired_at`, `department_id`, or `location_id`.
- `filters`: optional filters with `status`, `keywords`, `department_ids`, `location_ids`, `candidate_ids`, and `technical_only`.

Outputs in `output`:

- `diagnostics`: scan and audit metadata.
- `coverage`: aggregate completeness metrics for the sample.
- `coverage.sample_size`: requested sample size.
- `coverage.returned_count`: number of records actually audited.
- `coverage.missing_email_count`: sampled hires missing email.
- `coverage.missing_linkedin_count`: sampled hires missing LinkedIn.
- `coverage.by_department`: counts by department id.
- `coverage.by_location`: counts by location id.
- `confidence`: confidence score from `0.0` to `1.0`.
- `sample_hires`: sampled hire records used in the audit.

### `ashby_get_recent_hires`

What it does:

- Returns recent hires from Ashby and lets you narrow the list by identifiers, departments, locations, or keywords.

Inputs:

- `count`: how many hires to return. Default `10`, max `100`.
- `role_context`: optional free-text role context.
- `keywords`: optional hire search keywords.
- `selection_mode`: retrieval strategy. One of `global_latest_exact`, `global_latest_best_effort`, or `fast_sample`.
- `sort_by`: sort field. One of `hired_at`, `created_at`, or `updated_at`.
- `sort_order`: `desc` or `asc`.
- `retrieval_policy`: `strict_count` or `fast_sample`.
- `max_scan_pages`: optional page budget.
- `require_fields`: fields that must be present on returned hires.
- `status`: optional status filter. Defaults to hired records.
- `department_ids`: optional department filter.
- `location_ids`: optional location filter.
- `candidate_ids`: optional candidate filter.

Outputs in `output`:

- `hires`: returned hire records.
- `diagnostics`: retrieval metadata such as requested count, scan behavior, and stop reason.
- `confidence`: confidence score from `0.0` to `1.0`.

### `ashby_get_recent_technical_hires`

What it does:

- Returns recent technical hires from Ashby using the same retrieval controls as recent hires, with technical filtering applied.

Inputs:

- `count`: how many hires to return. Default `10`, max `100`.
- `role_context`: optional role description used to expand technical keywords.
- `keywords`: optional technical keywords to add.
- `selection_mode`: `global_latest_exact`, `global_latest_best_effort`, or `fast_sample`.
- `sort_by`: `hired_at`, `created_at`, or `updated_at`.
- `sort_order`: `desc` or `asc`.
- `retrieval_policy`: `strict_count` or `fast_sample`.
- `max_scan_pages`: optional page budget.
- `require_fields`: fields that must be present on returned hires.
- `department_ids`: optional department filter.
- `location_ids`: optional location filter.
- `candidate_ids`: optional candidate filter.

Outputs in `output`:

- `hires`: returned technical hire records.
- `diagnostics`: retrieval metadata such as requested count, scan behavior, and stop reason.
- `confidence`: confidence score from `0.0` to `1.0`.

### `ashby_search_hires`

What it does:

- Searches Ashby hires with explicit filters and retrieval controls.

Inputs:

- `count`: how many hires to return. Default `10`, max `200`.
- `selection_mode`: `global_latest_exact`, `global_latest_best_effort`, or `fast_sample`.
- `sort_by`: `hired_at`, `created_at`, or `updated_at`.
- `sort_order`: `desc` or `asc`.
- `retrieval_policy`: `strict_count` or `fast_sample`.
- `max_scan_pages`: optional page budget.
- `require_fields`: fields that must be present on returned hires.
- `filters`: filter object with `status`, `keywords`, `department_ids`, `location_ids`, `candidate_ids`, and `technical_only`.

Outputs in `output`:

- `hires`: returned hire records.
- `diagnostics`: retrieval metadata such as requested count, scan behavior, and stop reason.
- `confidence`: confidence score from `0.0` to `1.0`.

## Gem

The read tools below return the standard read envelope described above. The write tools return the standard write envelope with `output`, `summary`, `verification`, and `receipt`.

### Read Tools

- `gem_find_candidates`: finds candidates by `email`, `linked_in_handle` or `linkedin_url`, or `candidate_ids`, plus optional API-backed filters and bounded scan controls. Output: `matches`, `scan`.
- `gem_find_projects`: finds projects by case-insensitive `name_exact` or `name_contains`, plus optional owner or access filters and bounded scan controls. Output: `matches`, `scan`.
- `gem_get_candidate`: fetches one candidate by `candidate_id`. Output: `candidate_id`, `candidate`.
- `gem_get_project`: fetches one project by `project_id`. Output: `project_id`, `project`.
- `gem_get_sequence`: fetches one sequence by `sequence_id`. Output: `sequence_id`, `sequence`.
- `gem_list_candidate_notes`: lists notes for `candidate_id` with optional `created_after`, `created_before`, `sort`, `page`, and `page_size`. Output: `candidate_id`, `notes`, `pagination`.
- `gem_list_candidates`: lists candidates with optional `created_after`, `created_before`, `updated_after`, `updated_before`, `created_by`, `email`, `linked_in_handle`, `candidate_ids`, `sort`, `page`, and `page_size`. Output: `candidates`, `pagination`.
- `gem_list_custom_field_options`: lists options for `custom_field_id` with optional `value`, `is_hidden`, `page`, and `page_size`. Output: `custom_field_id`, `options`, `pagination`.
- `gem_list_custom_fields`: lists custom fields with optional `scope`, `project_id`, `name`, `is_hidden`, `created_after`, `created_before`, `sort`, `page`, and `page_size`. Output: `custom_fields`, `pagination`.
- `gem_list_project_candidates`: lists project memberships for `project_id` with optional `added_after`, `added_before`, `sort`, `page`, `page_size`, and `include_candidates`. Output: `project_id`, `project`, `entries`, `pagination`, `unresolved_candidate_ids`.
- `gem_list_project_field_options`: lists options for `project_field_id` with optional `value`, `is_hidden`, `page`, and `page_size`. Output: `project_field_id`, `options`, `pagination`.
- `gem_list_project_fields`: lists project fields with optional `field_type`, `name`, `is_hidden`, `is_required`, `created_after`, `created_before`, `sort`, `page`, and `page_size`. Output: `project_fields`, `pagination`.
- `gem_list_project_membership_log`: lists membership log entries filtered by `project_id` or `candidate_id`, plus optional `changed_after`, `changed_before`, `sort`, `page`, and `page_size`. Output: `entries`, `pagination`.
- `gem_list_projects`: lists projects with optional `owner_user_id`, `readable_by_user_id`, `writable_by_user_id`, `is_archived`, `created_after`, `created_before`, `sort`, and pagination controls. Output: `projects`, `pagination`.
- `gem_list_sequences`: lists sequences with optional `user_id`, `created_after`, `created_before`, `sort`, `page`, and `page_size`. Output: `sequences`, `pagination`.
- `gem_list_uploaded_resumes`: lists uploaded resumes for `candidate_id` with optional `created_after`, `created_before`, `sort`, `page`, and `page_size`. Output: `candidate_id`, `resumes`, `pagination`.
- `gem_list_users`: lists users with optional `email`, `page`, and `page_size`. Output: `users`, `pagination`.

### Write Tools

- `gem_add_candidate_note`: writes a candidate note. Inputs: `candidate_id`, `note`, optional `user_id`. Output: `candidate_id`, `note`, `user_id`, `provider_response`.
- `gem_add_custom_field_options`: adds options to a custom field. Inputs: `custom_field_id`, `option_values`. Output: `custom_field_id`, `option_ids`, `options`, `provider_response`.
- `gem_add_profiles_to_project`: imports or upserts profiles into a project. Inputs: `project_id`, `profiles`, optional `user_id`. Output: `project_id`, `added_candidate_ids`, `mapping`, `user_id`, `provider_response`.
- `gem_create_candidate`: creates a candidate. Inputs: candidate creation fields such as `first_name`, `last_name`, `emails`, `linked_in_handle`, `profile_urls`, `project_ids`, `custom_fields`, optional `user_id`, and related native Gem fields. Output: `candidate_id`, `candidate`, `user_id`, `provider_response`.
- `gem_create_custom_field`: creates a custom field. Inputs: `name`, `value_type`, `scope`, optional `project_id`, optional `option_values`. Output: `custom_field_id`, `custom_field`, `provider_response`.
- `gem_create_project_field_option`: creates a project field option. Inputs: `project_field_id`, `options`. Output: `project_field_id`, `option_ids`, `options`, `provider_response`.
- `gem_create_project_field`: creates a project field. Inputs: `name`, `field_type`, optional `options`, optional `is_required`. Output: `project_field_id`, `project_field`, `provider_response`.
- `gem_create_project`: creates a project. Inputs: `project_name`, optional `metadata`, optional `user_id`. Output: `project_id`, `name`, `user_id`, `provider_response`.
- `gem_remove_candidates_from_project`: removes candidates from a project with partial-success reporting. Inputs: `project_id`, `candidate_ids`, optional `user_id`. Output: `project_id`, `removed_candidate_ids`, `already_missing_candidate_ids`, `user_id`, `provider_response`.
- `gem_set_custom_value`: sets a candidate custom field value. Inputs: `candidate_id`, `key`, `value`, optional `project_id`. Output: `candidate_id`, `key`, `custom_field_id`, `value`, `provider_response`.
- `gem_set_project_field_value`: updates a project field value. Inputs: `project_id`, `project_field_id`, `operation`, optional `option_ids`, optional `text`. Output: `project_id`, `project_field_id`, `operation`, `option_ids`, `text`, `provider_response`.
- `gem_update_candidate`: updates a candidate. Inputs: `candidate_id` plus any native candidate update fields such as `title`, `company`, `location`, `profile_urls`, `custom_fields`, or `due_date`. Output: `candidate_id`, `candidate`, `provider_response`.
- `gem_update_custom_field_option`: updates a custom field option visibility. Inputs: `custom_field_id`, `option_id`, `is_hidden`. Output: `custom_field_id`, `option_id`, `option`, `provider_response`.
- `gem_update_project_field_option`: updates a project field option visibility. Inputs: `project_field_id`, `project_field_option_id`, `is_hidden`. Output: `project_field_id`, `project_field_option_id`, `option`, `provider_response`.
- `gem_update_project`: updates a project. Inputs: `project_id`, optional `user_id`, optional `name`, optional `privacy_type`, optional `description`, optional `is_archived`. Output: `project_id`, `project`, `provider_response`.
- `gem_upload_resume`: uploads a resume. Inputs: `candidate_id`, `file_path`, optional `user_id`. Output: `candidate_id`, `user_id`, `uploaded_resume`, `provider_response`.

## Harmonic

### `harmonic_enrich_company`

What it does:

- Triggers a Harmonic company enrichment request from a company identifier or raw payload.

Inputs:

- `company_urn`: Harmonic company urn.
- `domain`: company domain.
- `name`: company name.
- `website_url`: company website URL.
- `payload`: optional raw request payload.
- At least one identifier or a non-empty `payload` is required.

Outputs in `output`:

- `status`: enrichment status returned by Harmonic.
- `message`: provider message about the enrichment request.
- `enrichment_urn`: Harmonic enrichment job urn.
- `enriched_company_urn`: company urn that Harmonic enriched, if known.
- `raw`: raw provider response.

### `harmonic_enrich_person`

What it does:

- Triggers a Harmonic person enrichment request from a person identifier or raw payload.

Inputs:

- `person_urn`: Harmonic person urn.
- `linkedin_url`: LinkedIn URL for the person.
- `email`: email address.
- `full_name`: full name.
- `company_name`: current company name.
- `payload`: optional raw request payload.
- At least one identifier or a non-empty `payload` is required.

Outputs in `output`:

- `status`: enrichment status returned by Harmonic.
- `message`: provider message about the enrichment request.
- `enrichment_urn`: Harmonic enrichment job urn.
- `enriched_person_urn`: person urn that Harmonic enriched, if known.
- `raw`: raw provider response.

### `harmonic_find_similar_profiles`

What it does:

- Finds candidate profiles similar to the seed profiles you provide.

Inputs:

- `seed_profiles`: list of seed profile objects. Include identifiers like `email`, `linkedin`, `candidate_id`, `name`, or `skills` when possible.
- `per_seed`: how many similar profiles to request per seed. Default `10`, max `50`.

Outputs in `output`:

- `candidates`: deduplicated similar profile results.
- `dedupe_report`: counts for how many profiles were merged during deduplication.

### `harmonic_get_employees_by_company`

What it does:

- Fetches employees for a single company from Harmonic.

Inputs:

- `company_id_or_urn`: Harmonic company id or urn.
- `size`: page size. Default `10`, max `1000`. Large values can produce very large hydrated employee payloads.
- `cursor`: optional pagination token. Harmonic currently expects numeric offset values here, such as `10` for the next page after `size=10`.

Outputs in `output`:

- `company_id_or_urn`: company that was queried.
- `count`: number of employee records in the response.
- `employees`: deduplicated employee profiles.
- `dedupe_report`: counts for how many profiles were merged during deduplication.
- `page_info`: pagination metadata for the next page. `page_info.next` is the token to pass back as `cursor`.

### `harmonic_get_people_saved_search_results_with_metadata`

What it does:

- Fetches people results for a Harmonic saved search along with raw search metadata.

Inputs:

- `saved_search_id_or_urn`: Harmonic saved search id or urn.
- `size`: page size. Default `100`, max `1000`.
- `cursor`: optional pagination cursor.

Outputs in `output`:

- `saved_search_id_or_urn`: saved search that was queried.
- `count`: number of candidate records in the response.
- `candidates`: deduplicated candidate profiles.
- `dedupe_report`: counts for how many profiles were merged during deduplication.
- `page_info`: pagination metadata for the next page.
- `raw_metadata`: raw saved search metadata from Harmonic.

### `harmonic_get_team_network_connections_to_company`

What it does:

- Fetches team network connection data for a company from Harmonic.

Inputs:

- `company_id_or_urn`: Harmonic company id or urn.
- `size`: page size. Default `100`, max `1000`.
- `cursor`: optional pagination cursor.

Outputs in `output`:

- `company_id_or_urn`: company that was queried.
- `count`: number of connection records in the response.
- `connections`: team network connection records.
- `page_info`: pagination metadata for the next page.
- `source_endpoint`: Harmonic endpoint used for the lookup.

### `harmonic_search_companies_by_natural_language`

What it does:

- Runs a natural-language company search in Harmonic.

Inputs:

- `query`: natural-language description of the companies you want.
- `similarity_threshold`: optional score threshold from `0.0` to `1.0`.
- `size`: page size. Default `25`, max `1000`.
- `cursor`: optional pagination cursor.

Outputs in `output`:

- `query`: original query string.
- `count`: number of companies in the response.
- `companies`: matching companies.
- `page_info`: pagination metadata for the next page.
- `query_interpretation`: Harmonic's interpretation of the query.

## Metaview

### `metaview_enrich_candidate_profiles`

What it does:

- Enriches candidate profile objects with Metaview data and deduplicates the results.

Inputs:

- `profiles`: list of candidate profile objects. Include identifiers like `email`, `linkedin`, `candidate_id`, or `name` when possible.

Outputs in `output`:

- `candidates`: enriched and deduplicated candidate profiles.
- `dedupe_report`: counts for how many profiles were merged during deduplication.

## LinkedIn Profile Changes

### `linkedin_profile_changes_profile_list_upsert`

What it does:

- Creates or updates a named LinkedIn profile list used for grouped monitoring.

Inputs:

- `list_name`: unique list name.
- `description`: optional description.
- `default_collector_mode`: usually `browser` or `fixture`.
- `active`: whether the list is active.

Outputs:

- `list`: stored list definition.
- `summary`: short confirmation.

### `linkedin_profile_changes_profile_list_rename`

What it does:

- Renames one stored LinkedIn profile list without changing its members.

Inputs:

- `current_list_name`: existing list name.
- `new_list_name`: new name to assign.

Outputs:

- `list`: stored list definition after the rename.
- `summary`: short confirmation.

### `linkedin_profile_changes_profile_list_members_upsert`

What it does:

- Adds or updates members for a named LinkedIn profile list.

Inputs:

- `list_name`: target list.
- `profiles`: list of member objects. Each member should include `profile_url` and may include `name`, `company`, `fixture_name`, `collector_mode`, and `active`.
- `replace_existing`: if true, removes current list members not present in the provided input.

Outputs:

- `list_name`: target list.
- `count`: number of members upserted.
- `members`: stored member rows.

### `linkedin_profile_changes_profile_list_members_remove`

What it does:

- Removes one or more LinkedIn profile URLs from a named list.

Inputs:

- `list_name`: target list.
- `profile_urls`: URLs to remove.

Outputs:

- `list`: stored list definition.
- `removed_count`: how many members were removed.
- `removed_urls`: URLs removed from the list.
- `missing_urls`: requested URLs that were not present.

### `linkedin_profile_changes_profile_list_members_list`

What it does:

- Lists the current members and metadata for a named LinkedIn profile list.

Inputs:

- `list_name`: target list.
- `active_only`: if true, only returns active members.
- `limit`: maximum member rows to return.

Outputs:

- `list_name`: target list.
- `count`: number of members returned.
- `members`: member rows with metadata like `profile_name`, `company_name`, `fixture_name`, and `collector_mode`.

### `linkedin_profile_changes_collect_profile_list_baseline`

What it does:

- Creates first snapshots for each active member of a named list and skips members that already have a stored baseline.

Inputs:

- `list_name`: target list.
- `active_only`: whether to limit to active members.
- `limit`: maximum members to process.

Outputs:

- `list`: stored list definition.
- `mode`: always `baseline`.
- `processed_count`, `collected_count`, `skipped_count`, `error_count`
- `items`: per-member result rows with `status`, `snapshot`, `previous_snapshot_id`, `change_count`, and any `error`.

### `linkedin_profile_changes_collect_profile_list_check`

What it does:

- Runs a subsequent check for each active member of a named list and returns detected changes.

Inputs:

- `list_name`: target list.
- `active_only`: whether to limit to active members.
- `limit`: maximum members to process.

Outputs:

- `list`: stored list definition.
- `mode`: always `check`.
- `processed_count`, `collected_count`, `skipped_count`, `error_count`
- `items`: per-member result rows including `changes`.

### `linkedin_profile_changes_watchlist_upsert`

What it does:

- Creates or updates a single watched LinkedIn profile entry.

Inputs:

- `profile_url`: LinkedIn profile URL.
- `display_name`: optional display name override.
- `fixture_name`: fixture filename for fixture mode.
- `collector_mode`: `browser` or `fixture`.
- `monitor_headline`, `monitor_about`, `monitor_experience`: section toggles.
- `active`: whether the watch entry is active.

Outputs:

- `profile`: stored watch profile.
- `summary`: short confirmation.

### `linkedin_profile_changes_watchlist_list`

What it does:

- Lists the stored watch profiles.

Inputs:

- `active_only`: if true, only returns active watch profiles.
- `limit`: maximum rows.

Outputs:

- `count`: number of watch profiles returned.
- `profiles`: watch profile rows.

### `linkedin_profile_changes_browser_auth_status`

What it does:

- Reports whether a reusable LinkedIn browser session is configured.

Inputs:

- none.

Outputs:

- `storage_state_exists`: whether saved auth state is present.
- `storage_state_path`: auth state file path.
- `credentials_configured`: whether env credentials are set.
- `browser_headless`, `browser_channel`, `auth_autofill`, `auth_timeout_seconds`
- `available`: whether browser collection is configured.

### `linkedin_profile_changes_browser_auth_bootstrap`

What it does:

- Opens a real browser window, waits for LinkedIn login to complete, and saves reusable session state.

Inputs:

- none.

Outputs:

- `storage_state_path`: saved auth state path.
- `message`: confirmation string.

### `linkedin_profile_changes_collect_snapshot`

What it does:

- Collects one snapshot for a single LinkedIn profile.

Inputs:

- `profile_url`: LinkedIn profile URL.
- `fixture_name`: optional fixture filename.
- `collector_mode`: optional override for `browser` or `fixture`.

Outputs:

- `collector_run_id`
- `watch_profile`
- `snapshot`
- `previous_snapshot_id`
- `change_count`
- `changes`

### `linkedin_profile_changes_collect_due_snapshots`

What it does:

- Collects snapshots for all active watchlist entries.

Inputs:

- `limit`: maximum active watch profiles to process.

Outputs:

- `processed_count`, `error_count`
- `results`: per-profile collection results.
- `errors`: failures.

### `linkedin_profile_changes_get_recent_changes`

What it does:

- Returns recently persisted LinkedIn profile changes.

Inputs:

- `limit`: maximum changes.
- `profile_url`: optional profile filter.

Outputs:

- `count`: number of changes returned.
- `changes`: change rows.

### `linkedin_profile_changes_get_profile_history`

What it does:

- Returns recent snapshots for one LinkedIn profile.

Inputs:

- `profile_url`: LinkedIn profile URL.
- `limit`: maximum snapshots.

Outputs:

- `count`: number of snapshots returned.
- `snapshots`: stored snapshot rows.

### `linkedin_profile_changes_diff_latest`

What it does:

- Compares the latest two stored snapshots for one LinkedIn profile.

Inputs:

- `profile_url`: LinkedIn profile URL.

Outputs:

- `profile_url`
- `changed`
- `changes`
- `snapshot_before_id`
- `snapshot_after_id`
