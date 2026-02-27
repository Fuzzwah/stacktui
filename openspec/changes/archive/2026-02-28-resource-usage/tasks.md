## 1. Resource Stats Collection

- [x] 1.1 Add `get_resource_stats()` helper function that runs `docker stats --no-stream --format json`, parses the output, and returns a dict mapping service names to `(cpu_percent: float, mem_usage_str: str)` tuples
- [x] 1.2 Add `_format_memory()` helper that converts Docker memory strings (e.g., "256MiB", "2.3GiB") to compact format ("256M", "2.3G")
- [x] 1.3 Handle `docker stats` failure or timeout gracefully — return an empty dict so callers don't need error handling

## 2. Refresh Integration

- [x] 2.1 Call `get_resource_stats()` inside `_refresh_status()` and pass the result to `ServicePanel.update_services()`
- [x] 2.2 Update `update_services()` signature to accept an optional `resource_stats` parameter (dict mapping service name to CPU/memory data)

## 3. ServicePanel Display

- [x] 3.1 In `update_services()`, append compact resource usage text (e.g., "45% 256M") in dim style after existing status info for running services
- [x] 3.2 Style CPU values in warning color (yellow) when CPU > 80%
- [x] 3.3 Style memory values in warning color (yellow) when memory percentage exceeds 80% of the container's limit
- [x] 3.4 Show no resource info for stopped services (already handled by the else branch)
