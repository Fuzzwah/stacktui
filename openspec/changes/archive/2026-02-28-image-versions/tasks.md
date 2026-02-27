## 1. Data Model

- [x] 1.1 Add `image: str` field to `ServiceInfo.__init__()` (default empty string)
- [x] 1.2 Add `image_tag` property to `ServiceInfo` that extracts the tag portion after the last `:`, returning empty string if no tag present

## 2. Data Extraction

- [x] 2.1 Update `parse_services()` to extract the `Image` field from `docker compose ps` JSON and pass it to `ServiceInfo`

## 3. Display

- [x] 3.1 Update `ServicePanel.update_services()` to append image tag in dim style after status/uptime for infra services with a non-empty tag
- [x] 3.2 Ensure primary services and stopped services do not display image tags
