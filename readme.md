# TODOs

* [ ] Tutorial or explanation
  * [X] guided tours
  * [X] create a consent sheet tour
  * [X] share a consent sheet tour
  * [X] create group tour
  * [ ] join group tour
* [ ] Tests
* [X] Localisation
* [X] Group creation
* [X] Consent Sheet Saving
* [X] Consent Sheet Viewing
* [X] Consent Sheet Reuse
* [ ] Consent Sheet Reuse for group creation
* [X] Group summary
* [X] Commenting
* [X] Login without SSO
* [ ] Anonymous Public Sheets -> Sheet with Passcode and without any comments
* [ ] Groups from public sheets
* [X] Admin interface to modify texts
* [X] Radar plot for different playstyles
  * [ ] integrate into groups
  * [ ] summarize
* [X] Custom Triggers for Consent Sheet
  * [X] Shared in Group
* [X] Consent Summary preference based
* [X] sanitize group names
* [ ] use caching and reduce database queries

# Environment Variables

* DB_CONNECTION_STRING used to connect to the database. Default is `sqlite:///db/database.sqlite`.
* LOGLEVEL used to set the loglevel. Default is `INFO`.
* GOOGLE_CLIENT_ID used to authenticate with Google. Default is `...`.
* GOOGLE_CLIENT_SECRET used to authenticate with Google. Default is `...`.
* DISCORD_CLIENT_ID used to authenticate with Discord. Default is `...`.
* DISCORD_CLIENT_SECRET used to authenticate with Discord. Default is `...`.
* BASE_URL used to set the base url. Default is `http://localhost:8080`.
* ADMINS comma separated list of user ids that are admins. Default is no admin.
* SEED_ON_STARTUP used to seed the database on startup. Default is `False`.
* RELOAD used to reload the server on code changes. Default is `False`.
* STORAGE_SECRET used to encrypt the storage. Default is random string on every restart.

# Example Environment Variables
```ps1
$env:DB_CONNECTION_STRING = "sqlite:///db/database.sqlite"
$env:LOGLEVEL = "INFO"
$env:ADMINS = ""
$env:SEED_ON_STARTUP = "true"
$env:RELOAD = "true"
```
