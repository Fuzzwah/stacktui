## 1. Data Model

- [x] 1.1 Add `ports: list[int]` field to `ServiceInfo.__init__()` with default empty list

## 2. Port Extraction

- [x] 2.1 In `parse_services()`, extract `Publishers` array from each JSON object, filter to `PublishedPort > 0`, deduplicate, sort, and pass to `ServiceInfo` constructor
- [x] 2.2 Ensure deduplication logic (highest-priority state wins) carries the winning container's ports

## 3. Display Property

- [x] 3.1 Add a `ports_text` property to `ServiceInfo` that returns formatted string (e.g., `:8000 :443`) or empty string if no ports

## 4. ServicePanel Integration

- [x] 4.1 In `ServicePanel.update_services()`, append `ports_text` in dim style after existing status elements (uptime, image tag, error count) when non-empty

## 5. Verification

- [x] 5.1 Run the app against the demo environment and verify ports display correctly for services with published ports
- [x] 5.2 Verify services without published ports show no extra whitespace or port info
