## 1. ServiceInfo Extension

- [x] 1.1 Add `restart_count: int = 0` parameter to `ServiceInfo.__init__()` and store as instance attribute

## 2. Restart Count Query

- [x] 2.1 In `parse_services()`, after building the service list, query `docker inspect --format '{{.RestartCount}}' <container_name>` for each service and populate `restart_count`
- [x] 2.2 Handle missing/stopped containers gracefully (default to 0)

## 3. ServicePanel Badge Display

- [x] 3.1 In `ServicePanel.update_services()`, append restart count badge `" ↻N"` to the status Text when restart_count > 0
- [x] 3.2 Style badge yellow for counts 1-4, red for counts >= 5

## 4. Auto-Select Restart-Looping Services

- [x] 4.1 In `ServicePanel.update_services()`, add services with restart_count >= 5 to the unhealthy set for auto-checkbox selection

## 5. Verification

- [x] 5.1 Run the demo environment and verify restart count displays correctly (may need to manually trigger restarts to test)
