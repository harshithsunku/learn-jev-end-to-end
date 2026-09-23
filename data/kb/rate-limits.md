# API rate limits

## Limits by plan
Free workspaces can make 60 API requests per minute. Pro workspaces can make 600 requests per minute. Enterprise workspaces get 6,000 requests per minute, and higher limits are available on request.

## What happens when you exceed a limit
Requests over the limit receive HTTP 429 Too Many Requests with a Retry-After header. Clients should wait for the number of seconds in Retry-After, then retry with exponential backoff.

## Burst allowance
Every plan may burst to 2x its per-minute limit for up to 10 seconds.
