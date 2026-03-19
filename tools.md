# Tools

This file documents the MCP tools currently callable from this workspace.

Source of truth:
- Runtime exposure: `agentic-tools-mcp/agentic_tools_mcp/server_factory.py`
- Platform contracts: `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-*/tool_catalog.json`
- Runtime policy: `/Users/maximilian/coding/agentic-platform-tools/agentic-tools-*/policy/capabilities.yaml`

## How To Read This File

- Read tools expose the logical tool id with `.` replaced by `_`. Example: `ashby.get_recent_hires` becomes `ashby_get_recent_hires`.
- Write tools are staged, not executed immediately. Their callable name adds `_stage`. Example: `gem.create_project` becomes `gem_create_project_stage`.
- Read tool responses have this envelope:
  - `output`: tool-specific payload documented below
  - `summary`: short human summary
  - `verification`: runtime verification result
- Stage tool responses have this envelope:
  - `checkpoint_id`, `run_id`, `status`, `risk_tier`, `tool_id`
  - `action`: staged input, preview output, compensation hint, and verification
- `checkpoint_list`, `checkpoint_commit`, and `checkpoint_reject` exist on every server. They only operate on checkpoints created on that server.
- For inputs named `profiles` or `seed_profiles`, include identity fields like `email`, `linkedin`, or `candidate_id` whenever possible. Those are the main keys used for deduplication.

## Current Callable Names

### Ashby
- `ashby_audit_hire_coverage`
- `ashby_get_recent_hires`
- `ashby_get_recent_technical_hires`
- `ashby_search_hires`

### Gem
- `gem_get_candidate`
- `gem_list_project_candidates`
- `gem_list_projects`
- `gem_add_candidate_note_stage`
- `gem_add_profiles_to_project_stage`
- `gem_create_project_stage`
- `gem_set_custom_value_stage`

### Harmonic
- `harmonic_create_saved_search_from_query_stage`
- `harmonic_derive_company_headcount_change_last_90_days`
- `harmonic_derive_company_recent_joiners`
- `harmonic_derive_company_recent_leavers`
- `harmonic_enrich_company_stage`
- `harmonic_enrich_person_stage`
- `harmonic_export_people_saved_search_results_as_csv`
- `harmonic_find_similar_profiles`
- `harmonic_get_company_current_headcount`
- `harmonic_get_company_employee_urns`
- `harmonic_get_company_funding_rounds`
- `harmonic_get_company_funding_summary`
- `harmonic_get_people_saved_search_results_with_metadata`
- `harmonic_get_saved_search`
- `harmonic_get_saved_searches`
- `harmonic_get_search_typeahead_results`
- `harmonic_get_team_network_connections_to_company`
- `harmonic_search_companies_by_natural_language`

### Metaview
- `metaview_enrich_candidate_profiles`

### Common Checkpoint Tools
- `checkpoint_list`
- `checkpoint_commit`
- `checkpoint_reject`

## Common Checkpoint Tools

### `checkpoint_list`
What it does:
- Lists staged checkpoints for the current server.

Inputs:
- `status`: optional status filter. Leave empty to list all checkpoints.

Outputs:
- `count`: number of checkpoints returned.
- `checkpoints`: list of checkpoint summaries.
- `checkpoints[].checkpoint_id`: checkpoint identifier.
- `checkpoints[].run_id`: run that created the checkpoint.
- `checkpoints[].status`: checkpoint state such as `pending_approval`, `completed`, `failed`, or `rejected`.
- `checkpoints[].risk_tier`: `low` or `high`.
- `checkpoints[].created_at`: creation timestamp.
- `checkpoints[].tool_ids`: staged tool ids inside the checkpoint.
- `checkpoints[].summaries`: human summaries for the staged actions.

### `checkpoint_commit`
What it does:
- Approves and executes a staged write checkpoint.

Inputs:
- `checkpoint_id`: checkpoint to execute.

Outputs:
- `checkpoint_id`: checkpoint that was committed.
- `status`: final checkpoint status, usually `completed` or `failed`.
- `receipts`: execution receipts for each staged action.
- `receipts[].status`: `success`, `failed`, `duplicate`, or `compensated`.
- `receipts[].result`: tool-specific result. On success this contains the committed business output plus `_verification`.

### `checkpoint_reject`
What it does:
- Rejects a staged checkpoint without executing it.

Inputs:
- `checkpoint_id`: checkpoint to reject.
- `reason`: optional reason for rejection.

Outputs:
- `checkpoint_id`: checkpoint that was rejected.
- `status`: resulting checkpoint status.
- `reason`: echoed rejection reason.

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

`gem_get_candidate`, `gem_list_project_candidates`, and `gem_list_projects` are read tools and return the standard read envelope described above. The `*_stage` Gem tools below are staged writes, and their actual provider results appear later in `checkpoint_commit.receipts[].result`.

### `gem_get_candidate`
What it does:
- Fetches a Gem candidate by id and returns the provider's full candidate payload.

Inputs:
- `candidate_id`: Gem candidate id to fetch.

Outputs in `output`:
- `candidate_id`: id of the fetched candidate.
- `candidate`: full candidate object from Gem.
- `candidate.candidate_id`: convenience alias of the Gem `id` field.

### `gem_list_project_candidates`
What it does:
- Lists candidates in a Gem project and can hydrate each membership with the full candidate record.

Inputs:
- `project_id`: Gem project id to inspect.
- `page`: results page to fetch. Default `1`.
- `page_size`: memberships per page. Default `20`, max `100`.
- `added_after`: optional Unix timestamp filter for memberships added after this time.
- `added_before`: optional Unix timestamp filter for memberships added before this time.
- `sort`: optional membership sort direction, `asc` or `desc`.
- `include_candidates`: whether to include full candidate payloads for the returned memberships. Default `true`.

Outputs in `output`:
- `project_id`: project that was queried.
- `project`: full project object from Gem.
- `project.project_id`: convenience alias of the Gem `id` field.
- `entries`: candidate memberships on the requested page.
- `entries[].candidate_id`: Gem candidate id in the project.
- `entries[].added_at`: when that candidate was added to the project.
- `entries[].candidate`: full candidate object when `include_candidates=true`; otherwise an empty object.
- `pagination`: Gem pagination metadata plus `page_size` and `returned_count`.
- `unresolved_candidate_ids`: candidate ids that appeared in the project membership list but could not be hydrated into full candidate payloads.

### `gem_list_projects`
What it does:
- Lists existing Gem projects with pagination and optional owner/access filters.

Inputs:
- `owner_user_id`: optional filter for projects owned by a specific Gem user.
- `readable_by_user_id`: optional filter for projects readable by a specific Gem user.
- `writable_by_user_id`: optional filter for projects writable by a specific Gem user.
- `is_archived`: optional archived filter.
- `created_after`: optional Unix timestamp filter for projects created after this time.
- `created_before`: optional Unix timestamp filter for projects created before this time.
- `sort`: optional sort direction, `asc` or `desc`.
- `page`: results page to fetch. Default `1`.
- `page_size`: projects per page. Default `20`, max `100`.

Outputs in `output`:
- `projects`: returned project objects.
- `projects[].project_id`: convenience alias of the Gem `id` field.
- `pagination`: Gem pagination metadata plus `page_size` and `returned_count`.

### `gem_add_candidate_note_stage`
What it does:
- Stages adding a note to a Gem candidate profile.

Inputs:
- `candidate_id`: Gem candidate id to update.
- `note`: note text to add.
- `user_id`: optional Gem user id to attribute the note to.

Committed result in `checkpoint_commit.receipts[].result`:
- `candidate_id`: candidate that was updated.
- `note`: note text that was written.
- `user_id`: Gem user id used for the write, if any.
- `provider_response`: raw provider response details.

### `gem_add_profiles_to_project_stage`
What it does:
- Stages importing or upserting profiles and adding them to a Gem project.

Inputs:
- `project_id`: target Gem project id.
- `profiles`: list of candidate profile objects. Include identifiers like `email`, `linkedin`, `candidate_id`, or `name` when possible.
- `user_id`: optional Gem user id to attribute the write to.

Committed result in `checkpoint_commit.receipts[].result`:
- `project_id`: project that received the profiles.
- `added_candidate_ids`: Gem candidate ids that were added.
- `mapping`: mapping from source identity to Gem candidate id.
- `user_id`: Gem user id used for the write, if any.
- `provider_response`: raw provider response details.

### `gem_create_project_stage`
What it does:
- Stages creating a new Gem project.

Inputs:
- `project_name`: name of the project to create.
- `metadata`: optional metadata object to send with the project.
- `user_id`: optional Gem user id to attribute the write to.

Committed result in `checkpoint_commit.receipts[].result`:
- `project_id`: id of the created project.
- `name`: name of the created project.
- `user_id`: Gem user id used for the write, if any.
- `provider_response`: raw provider response details.

### `gem_set_custom_value_stage`
What it does:
- Stages setting a custom field value on a Gem candidate.

Inputs:
- `candidate_id`: Gem candidate id to update.
- `key`: custom field key to set.
- `value`: value to write to the custom field.
- `project_id`: optional project context for the custom field.

Committed result in `checkpoint_commit.receipts[].result`:
- `candidate_id`: candidate that was updated.
- `key`: custom field key that was written.
- `custom_field_id`: resolved Gem custom field id, if returned by Gem.
- `value`: value that was written.
- `provider_response`: raw provider response details.

## Harmonic

`harmonic_create_saved_search_from_query_stage`, `harmonic_enrich_company_stage`, and `harmonic_enrich_person_stage` are staged writes. Calling them returns the standard stage response described above. Their actual provider result appears later in `checkpoint_commit.receipts[].result`.

### `harmonic_create_saved_search_from_query_stage`
What it does:
- Stages creating a Harmonic saved search from a raw `query` payload.

Inputs:
- `name`: saved search name.
- `query`: raw saved-search query object or query value to send to Harmonic.
- `payload`: optional raw request payload. If provided, it can include any provider-specific fields.

Committed result in `checkpoint_commit.receipts[].result`:
- `saved_search_urn`: urn of the created saved search.
- `raw`: raw provider response.

### `harmonic_derive_company_headcount_change_last_90_days`
What it does:
- Estimates a company's 90-day headcount change from Harmonic's current headcount, snapshots, and `traction_metrics` signals.

Inputs:
- `company_id_or_urn`: Harmonic company id or urn.

Outputs in `output`:
- `current_headcount`: best current headcount value, preferring `corrected_headcount`.
- `estimated_headcount_90_days_ago`: best historical estimate near the 90-day target date.
- `estimated_absolute_change`: estimated numeric delta from 90 days ago to now.
- `estimated_relative_change_percent`: estimated percentage delta.
- `status`: `estimated`, `relative_only`, or `unavailable`.
- `confidence`: `high`, `medium`, `low`, or `none`.
- `notes`: caveats about snapshot gaps or conflicting signals.

### `harmonic_derive_company_recent_joiners`
What it does:
- Reconstructs recent company joiners by combining company `people` entries with person experience history.

Inputs:
- `company_id_or_urn`: Harmonic company id or urn.
- `since_days`: how far back to look. Default `90`, max `365`.
- `transition_filter`: `all`, `external_only`, `internal_only`, or `unknown_only`.
- `limit`: max transitions to return. Default `25`, max `200`.

Outputs in `output`:
- `transitions`: reconstructed joiner records with `name`, `linkedin_url`, `transition_date`, `role_leaving`, `role_entering`, `company_leaving`, `company_joining`, `transition_type`, and `confidence`.
- `skipped_missing_profile_count`: company people records skipped because person profiles could not be fetched.
- `notes`: caveats about partial coverage.

### `harmonic_derive_company_recent_leavers`
What it does:
- Reconstructs recent company leavers by combining company `people` entries with person experience history.

Inputs:
- `company_id_or_urn`: Harmonic company id or urn.
- `since_days`: how far back to look. Default `90`, max `365`.
- `transition_filter`: `all`, `external_only`, `internal_only`, or `unknown_only`.
- `limit`: max transitions to return. Default `25`, max `200`.

Outputs in `output`:
- `transitions`: reconstructed leaver records with `name`, `linkedin_url`, `transition_date`, `role_leaving`, `role_entering`, `company_leaving`, `company_joining`, `transition_type`, and `confidence`.
- `skipped_missing_profile_count`: company people records skipped because person profiles could not be fetched.
- `notes`: caveats about partial coverage.

### `harmonic_enrich_company_stage`
What it does:
- Stages a Harmonic company enrichment request from a company identifier or raw payload.

Inputs:
- `company_urn`: Harmonic company urn.
- `domain`: company domain.
- `name`: company name.
- `website_url`: company website URL.
- `payload`: optional raw request payload.
- At least one identifier or a non-empty `payload` is required.

Committed result in `checkpoint_commit.receipts[].result`:
- `status`: enrichment status returned by Harmonic.
- `message`: provider message about the enrichment request.
- `enrichment_urn`: Harmonic enrichment job urn.
- `enriched_company_urn`: company urn that Harmonic enriched, if known.
- `raw`: raw provider response.

### `harmonic_enrich_person_stage`
What it does:
- Stages a Harmonic person enrichment request from a person identifier or raw payload.

Inputs:
- `person_urn`: Harmonic person urn.
- `linkedin_url`: LinkedIn URL for the person.
- `email`: email address.
- `full_name`: full name.
- `company_name`: current company name.
- `payload`: optional raw request payload.
- At least one identifier or a non-empty `payload` is required.

Committed result in `checkpoint_commit.receipts[].result`:
- `status`: enrichment status returned by Harmonic.
- `message`: provider message about the enrichment request.
- `enrichment_urn`: Harmonic enrichment job urn.
- `enriched_person_urn`: person urn that Harmonic enriched, if known.
- `raw`: raw provider response.

### `harmonic_export_people_saved_search_results_as_csv`
What it does:
- Fetches readable Harmonic people saved-search rows as JSON and flattens them into CSV text client-side.

Inputs:
- `saved_search_id_or_urn`: Harmonic saved search id or urn.
- `page_size`: rows to fetch per page. Default `100`, max `1000`.
- `max_pages`: how many pages to fetch. Default `1`, max `20`.
- `include_raw_json`: whether to add a `raw_json` CSV column.

Outputs in `output`:
- `row_count`: number of CSV rows produced.
- `columns`: CSV column order.
- `csv_text`: generated CSV content.
- `truncated`: whether more pages were available than the tool fetched.
- `saved_search`: saved-search metadata used for the export.
- `notes`: caveats about this being a client-side export, not a provider-native CSV endpoint.

### `harmonic_find_similar_profiles`
What it does:
- Finds candidate profiles similar to the seed profiles you provide.

Inputs:
- `seed_profiles`: list of seed profile objects. Include identifiers like `email`, `linkedin`, `candidate_id`, `name`, or `skills` when possible.
- `per_seed`: how many similar profiles to request per seed. Default `10`, max `50`.

Outputs in `output`:
- `candidates`: deduplicated similar profile results.
- `dedupe_report`: counts for how many profiles were merged during deduplication.

### `harmonic_get_company_current_headcount`
What it does:
- Fetches the current headcount fields exposed on a Harmonic company record.

Inputs:
- `company_id_or_urn`: Harmonic company id or urn.

Outputs in `output`:
- `current_headcount`: best current headcount value, preferring `corrected_headcount`.
- `headcount`: raw top-level `headcount`.
- `corrected_headcount`: corrected headcount when present.
- `external_headcount`: external headcount when present.

### `harmonic_get_company_employee_urns`
What it does:
- Fetches employee urns from Harmonic's company employees endpoint.

Inputs:
- `company_id_or_urn`: Harmonic company id or urn.
- `size`: page size. Default `100`, max `1000`.
- `page`: offset page number. Default `0`.
- `cursor`: optional cursor.
- `employee_group_type`: optional Harmonic employee group filter.
- `user_connection_status`: optional `TEAM_CONNECTION` or `NO_CONNECTION`.
- `employee_status`: optional `ACTIVE`, `ACTIVE_AND_NOT_ACTIVE`, or `NOT_ACTIVE`.

Outputs in `output`:
- `employee_urns`: deduplicated employee urns returned by the provider.
- `dedupe_report`: duplicate counts removed from the raw urn list.
- `page_info`: pagination metadata.

### `harmonic_get_company_funding_rounds`
What it does:
- Fetches round-level funding data from a Harmonic company record when that data is present.

Inputs:
- `company_id_or_urn`: Harmonic company id or urn.

Outputs in `output`:
- `funding_rounds_count`: number of round rows present on the company record.
- `has_round_level_data`: whether Harmonic returned any round-level entries.
- `funding_rounds`: normalized funding rounds with `amount`, `date`, `round_type`, and `raw`.
- `notes`: caveats, including that this field may be absent for some keys or plans.

### `harmonic_get_company_funding_summary`
What it does:
- Fetches the funding summary fields exposed on a Harmonic company record.

Inputs:
- `company_id_or_urn`: Harmonic company id or urn.

Outputs in `output`:
- `funding_total`: total funding amount.
- `num_funding_rounds`: count of funding rounds in the summary.
- `last_funding_at`: date of the latest round in the summary.
- `last_funding_total`: amount of the latest round in the summary.
- `last_funding_type`: type of the latest round.
- `funding_stage`: current summary funding stage.

### `harmonic_get_people_saved_search_results_with_metadata`
What it does:
- Fetches people results for a Harmonic saved search and resolves the saved-search metadata alongside those rows.

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
- `raw_metadata`: saved-search metadata such as `id`, `entity_urn`, `name`, `type`, `creator`, `is_private`, `updated_at`, `created_at`, and `query` when readable.

### `harmonic_get_saved_search`
What it does:
- Fetches a single Harmonic saved search and returns its full query definition.

Inputs:
- `saved_search_id_or_urn`: Harmonic saved search id or urn.

Outputs in `output`:
- `name`, `type`, `creator`, `visibility`, `updated_at`, `created_at`: saved-search metadata.
- `query`: full saved-search query payload.
- `column_view_settings`: provider column settings for the saved search.
- `raw`: raw provider payload.

### `harmonic_get_saved_searches`
What it does:
- Lists Harmonic saved searches with metadata you can use for discovery or filtering.

Inputs:
- `search_type`: optional type filter such as `PERSONS`.
- `visibility`: `all`, `shared`, or `private`.
- `size`: optional max number of searches to return.

Outputs in `output`:
- `count`: number of saved searches returned after filtering.
- `saved_searches`: saved-search rows including `name`, `type`, `creator`, `visibility`, `updated_at`, `created_at`, `query`, and `column_view_settings`.

### `harmonic_get_search_typeahead_results`
What it does:
- Runs Harmonic's typeahead endpoint for companies, people, or investors.

Inputs:
- `query`: text to search.
- `search_type`: `COMPANY`, `PERSON`, or `INVESTOR`.
- `limit`: max results to keep from the provider response. Default `25`, max `100`.

Outputs in `output`:
- `count`: provider count for the query.
- `results`: normalized typeahead rows with `entity_urn`, `type`, `text`, `alt_text`, `index_field`, `subtype`, `ranking_score`, and `raw`.

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
- Runs Harmonic's Scout natural-language company search.

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
