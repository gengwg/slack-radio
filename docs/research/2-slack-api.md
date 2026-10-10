# Slack unread-messages research (verified 2026-10-08)

Sources are docs.slack.dev, slack.com/help and slack.com/terms only. Anything marked UNVERIFIED was not confirmed in a primary source.

## 1. Finding unread messages

**Listing conversations.** `users.conversations` with `types=public_channel,private_channel,mpim,im` and `exclude_archived=true` returns the conversations the token's user is a member of. It is Tier 3, `limit` max 999, and needs `channels:read, groups:read, im:read, mpim:read`. Results are "limited objects" that don't include `is_member` or read state, so you need `conversations.info` for the full object. https://docs.slack.dev/reference/methods/users.conversations
`conversations.list` is Tier 2 and returns everything the token can see, not just your memberships, so `users.conversations` is the better fit. https://docs.slack.dev/reference/methods/conversations.list

**Read cursor.** The conversation object defines `last_read` as "The timestamp for the last message the calling user has read in this channel", and `unread_count_display` as unread messages "that matter to them (excludes things like join/leave messages)". https://docs.slack.dev/reference/objects/conversation-object
`conversations.info` (Tier 3, same `*:read` scopes, works with user tokens) shows `last_read`, `unread_count` and `unread_count_display` only in its 1:1 DM example. The docs say: "Some fields in the response, like `unread_count` and `unread_count_display`, are included for DM conversations only." https://docs.slack.dev/reference/methods/conversations.info
Takeaway: `last_read` is the documented cursor. Whether `conversations.info` returns it for public/private channels and MPDMs is not stated in the docs, so test it with a real xoxp token. Unread counts are documented for DMs only, so compute counts yourself.

**Fetching messages.** Call `conversations.history` with `oldest=<last_read>`. The bound is exclusive by default ("If a message has the same timestamp as `oldest` or `latest` it will not be included") and results come newest first. Paginate with `next_cursor`. Default `limit` is 100 and the docs recommend 200 or fewer per page. With a user token it can read "Any private conversation the user is a member of, and all public conversations." https://docs.slack.dev/reference/methods/conversations.history
Thread replies are not in the history results. Fetch them with `conversations.replies` (same `*:history` scopes, Tier 3 for internal apps). The parent message in its example includes `reply_count`, `subscribed`, `last_read` and `unread_count`, but the docs never define those fields. https://docs.slack.dev/reference/methods/conversations.replies

**Unread threads.** There is no official "Threads view" or unread-threads API. `subscriptions.thread.*` returns 404 on docs.slack.dev. In practice:
- (a) For each parent message in history with `reply_count > 0`, call `conversations.replies` with `oldest=<cursor>`.
- (b) For threads whose parent is older than the channel cursor, there is no documented signal. You can use the parent's `last_read`/`subscribed` from `conversations.replies` (undocumented semantics, so verify empirically) or keep a local per-thread cursor.

**Undocumented methods to avoid.** I checked each against docs.slack.dev/reference/methods/<name> on 2026-10-08 and all returned HTTP 404: `client.counts`, `users.counts`, `client.boot`, `subscriptions.thread.getView`, `subscriptions.thread.mark`. These are internal web-client methods with no stability or support guarantee. UNVERIFIED: they are commonly reported to need browser session tokens (xoxc + cookie). Using those tokens is outside the supported platform.
Read-marker events (`channel_marked`, `im_marked`) are RTM-only. https://docs.slack.dev/reference/events/channel_marked, https://docs.slack.dev/reference/events/im_marked
"Granular permission Slack apps cannot use the RTM API", and classic apps "may no longer be created". https://docs.slack.dev/legacy/legacy-rtm-api

**Marking read.** `conversations.mark` takes `channel` and `ts`. It is Tier 3 and accepts user or bot tokens. User-token scopes: `channels:write, groups:write, im:write, mpim:write`. "The associated user must be a member of the channel." Slack advises calling it infrequently, with roughly a 5-second debounce per channel. It has an error `enterprise_is_restricted`: "The method cannot be called from an Enterprise." I could not determine exactly when that error fires on Enterprise orgs. Test it there. https://docs.slack.dev/reference/methods/conversations.mark
There is no documented method for marking a thread read.

## 2. Token type and scopes

You need a user token (xoxp). User tokens "represent the same access a user has to a workspace". A bot token sees only conversations the bot belongs to, so it cannot see your DMs, and `last_read` is "the calling user's" cursor. https://docs.slack.dev/authentication/tokens

User scopes:
- `channels:history, groups:history, im:history, mpim:history` to read messages
- `channels:read, groups:read, im:read, mpim:read` to list conversations and read info
- `users:read` for `users.info` (Tier 4) to resolve names. https://docs.slack.dev/reference/methods/users.info
- Optional: `channels:write, groups:write, im:write, mpim:write` for `conversations.mark`. These are broader than "mark read", so check each scope page before requesting them.

**OAuth v2.** The flow is `https://slack.com/oauth/v2/authorize?client_id=..&user_scope=<scopes>`, then `oauth.v2.access`. The user token is in `authed_user.access_token`. "OAuth tokens do not expire" unless you enable token rotation. https://docs.slack.dev/authentication/installing-with-oauth
For a single-user internal app you can skip the redirect flow. Add the User Token Scopes, click "Install to Workspace" on the app's OAuth & Permissions page, and copy the "User OAuth Token" (xoxp-). Reinstall after any scope change. https://docs.slack.dev/app-management/quickstart-app-settings/ (via search, not fetched in full)

## 3. Rate limits

Limits are "per API method per workspace/team per app". On 429, honor `Retry-After`. https://docs.slack.dev/apis/web-api/rate-limits

| Method | Tier (internal app) |
|---|---|
| users.conversations | Tier 3 (50+/min) |
| conversations.list | Tier 2 (20+/min) |
| conversations.info | Tier 3 |
| conversations.history | Tier 3 |
| conversations.replies | Tier 3 |
| conversations.mark | Tier 3 |
| users.info | Tier 4 (100+/min) |

**2025 change.** Changelog of 2025-05-29: https://docs.slack.dev/changelog/2025/05/29/rate-limit-changes-for-non-marketplace-apps
> "The new rate limits only apply to commercially distributed applications outside the Marketplace."
> "Internal customer-built applications are not impacted by these changes."
> FAQ: "No, internal customer-built apps are not impacted and retain their current, higher rate limits."
> Affected apps "will be limited to 1 request per minute"; "The maximum and default for the `limit` parameter has been reduced to 15 objects."

Clarification of 2025-06-03: "Any internal customer-built apps will maintain their existing rate limits and will not be subject to the new posted limits." https://docs.slack.dev/changelog/2025/06/03/rate-limits-clarity
The method pages say: "For Marketplace and internal customer-built applications, this method has Tier 3 rate limits."
Caveat: Slack never formally defines "internal customer-built". An app you create and install only in your own workspace fits the plain reading, but no primary source says so explicitly. I found no 2026 change to these limits.

## 4. Admin approval

By default "members can install them without approval from a Workspace Owner". If an owner turns on "Require approved apps" / "Only allow pre-approved apps", members must request the app. https://slack.com/help/articles/222386767-Manage-app-approval-for-your-workspace
Members can by default "build internal integrations to fit your company's needs". https://slack.com/help/articles/360001670528-Security-recommendations-for-approving-apps
On Enterprise Grid: "By default, members of an Enterprise organization can install any app to workspaces they belong to." However, "Setting an app management policy turns on app approval for every workspace in an org." https://slack.com/help/articles/360038559694-Set-organization-level-policies-for-apps
UNVERIFIED: whether any approval step specifically targets user-scope tokens on Grid. I found nothing beyond the `conversations.mark` `enterprise_is_restricted` error. Expect most corporate Grid orgs to have approval on, so plan for an admin request.

## 5. Events API / Socket Mode

User-scope events such as `message.im` (needs `im:history`) are delivered for what the authorizing user "can 'see'". https://docs.slack.dev/apis/events-api/, https://docs.slack.dev/reference/events/message.im
Socket Mode needs an app-level token and no public URL, allows up to 10 connections, and is "not currently allowed in the public Slack Marketplace" (irrelevant for an internal app). https://docs.slack.dev/apis/events-api/using-socket-mode
The docs do not say whether Socket Mode delivers user-scope events; test it.
Usefulness: good for a live "read new messages as they arrive" mode. It does not give read state, since there are no read-marker events outside RTM, and it does not backfill. You still need the history/`last_read` sweep at startup.

## 6. Recent platform changes (2025-2026)

**API Terms** (effective 2025-10-10) prohibit: "(A) use API Data to train a large language model", "(B) bulk export Slack message and file data except where expressly allowed by an additional agreement". Under Data Access/RTS: "you may not create persistent copies, archives, indexes, or long-term data stores of other organizations' API Data". https://slack.com/terms-of-service/api
The Oct 2025 changelog says the "Distribution Beyond Your Organization" section applies only to third-party apps distributed outside your org, not to custom internal apps. https://docs.slack.dev/changelog/2025/10/13/api-terms-update
The terms do not ban LLM inference or TTS on API data, only training. For a personal internal app, keep data transient: no stored archive, and send text to a cloud TTS/LLM only if your company policy allows it.

**Real-time Search API** (`assistant.search.context`, formerly Data Access API): "available for directory-published apps and internal apps only". User-only scopes such as `search:read.im` give private data. It has special rate limits and no unread or read-state filter, so it does not solve this problem. It also says not to use legacy `search.messages`. https://docs.slack.dev/apis/web-api/real-time-search-api

## Recommended approach

1. Create an internal app in your own workspace with User Token Scopes only (the `*:read`, `*:history` and `users:read` scopes above, plus `*:write` only if you want to mark messages read). Install it from app settings and use the xoxp token. Request admin approval if the workspace or Grid requires it.
2. Sweep: run `users.conversations` (all four types). For each conversation call `conversations.info` to get `last_read`, then `conversations.history` with `oldest=last_read`. For returned parents with replies, call `conversations.replies`. Cache `users.info` lookups.
3. Older threads with new replies: keep a small local per-thread cursor, or empirically validate the parent's `last_read`/`subscribed` from `conversations.replies`. Do not use `client.counts`, `users.counts`, `client.boot` or `subscriptions.thread.*`.
4. After reading aloud, optionally call `conversations.mark` with the newest `ts`, debounced. Threads cannot be marked read via the API.
5. Optionally add Socket Mode with `message.*` user events for live playback.
6. Stay within Tier 3 with a simple 429/`Retry-After` handler. Do not persist message bodies.
