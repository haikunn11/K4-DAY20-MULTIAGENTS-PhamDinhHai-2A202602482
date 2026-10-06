---
name: parse-and-normalize-logs-for-errors
description: use this skill to parse log files extracting error and critical entries with normalized timestamps, service names, and repeat counts
---
1. Read the log file line by line.
2. Detect log entry lines by matching timestamp, log level, service name, and message.
3. Normalize timestamps to UTC in ISO 8601 format with 'Z' suffix.
4. Normalize service names to lowercase and replace hyphens with underscores.
5. Capture only entries with level ERROR or CRITICAL (case insensitive).
6. For each entry, capture the message text after the service name.
7. If a traceback follows, capture the last line as the exception message; otherwise, set exception to null.
8. Detect and sum any subsequent lines indicating repeated messages (e.g., '-- last message repeated N times --') to compute repeat_count.
9. Store each parsed entry with fields: timestamp_utc, service, level, message, exception, repeat_count.
10. Sort the final list of errors by service name, then timestamp ascending.
11. Aggregate counts by service summing repeat_count values.
12. Output the structured data in the required JSON schema with schema_version and generated_by metadata.
