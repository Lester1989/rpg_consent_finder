# TODOs

* [ ] Tutorial or explanation
* [ ] Tests
* [ ] Localisation
* [ ] Group creation
* [ ] Consent Sheet Saving
* [ ] Consent Sheet Viewing
* [ ] Consent Sheet Reuse
* [ ] Group summary
* [ ] Commenting

# Environment Variables

DB_CONNECTION_STRING used to connect to the database. Default is `sqlite:///db/database.sqlite`.
LOGLEVEL used to set the loglevel. Default is `INFO`.
GOOGLE_CLIENT_ID used to authenticate with Google. Default is `...`.
GOOGLE_CLIENT_SECRET used to authenticate with Google. Default is `...`.
DISCORD_CLIENT_ID used to authenticate with Discord. Default is `...`.
DISCORD_CLIENT_SECRET used to authenticate with Discord. Default is `...`.
BASE_URL used to set the base url. Default is `http://localhost:8080`.
ADMINS comma separated list of user ids that are admins. Default is no admin.
SEED_ON_STARTUP used to seed the database on startup. Default is `False`.
RELOAD used to reload the server on code changes. Default is `False`.

# User Stories
## GENERAL: new User
As a new User of the plattform I want to create a Consent Sheet I can then use for all Groups.

## Call To Action
The Discord Bot/ or any User creates an Invite Link. The User needs to authenticate (SSO) with Discord or Google.
On first Login a Nickname needs to be set. The User is then redirected to their Home Page.

## Home Page
The User is presented with a list of all Consent Sheets they created:
* [x] The User can see details for a Consent Sheet.
* [x] The User can delete a Consent Sheet, if it is not the gm_sheet of a group.
* [x] The User can also create a new Consent Sheet.
The User can also see a list of all Groups they are part of:
* [x] The User can see details for a Group.
* [x] The User can leave a Group. (if not the creator)
* [x] The User can delete a Group. (if the creator)
* [x] The User can create a new Group.
* [x] The User can join a Group with a code.
* [x] The User can be removed from a Group by the creator.

## Consentsheet Details
The User has a Preview and an Edit view.
There also exists a Groups Tab, where the User can (un-)assign the Sheet to a group.

## Consent Sheet Creation
The user is presented with a form to fill out. Each entry is filled by default with `unkown`. Additional to the selection a textinput can be enabled to give specifics to each topic. Also each entry is acompanied by an info-icon to further explain the topic. The sheet is saved on each interaction/focus change and is created on first display with defaults. Additional to all entries specific to any topic the user can provide a general comment. The User can also provide a Name for the Consent Sheet.

---
..WIP..
---
```
## Consent Sheet Sharing
The use can **enable** a publicly available link to the Consent sheet. This Link is also provided as QR Code and the Bot can provide that Link. Default is **disabled**. Two calls to Action are provided below the Consent Sheet if viewed without being logged in:
1. Create Account with default Consent Sheet
2. Create Account with this Consent Sheet as starting point

## GENERAL: Group Creation
As a GM I want to provide a Consent Sheet what I am ready to cover in my Game and tally the consent of what my players are ready to have covered.

## Create a Group
When logged in (after CTA and Account creation), on my Consentsheet I can create a group and either use my consent sheet or start with a default one. Then I can modify that sheet like a normal consent sheet, with a hint that I should provide details for the `maybe` topics and should avoid `unkown` topics. Those are only warnings and could be ignored. My Group also need a Name and can have a Description.

## Group List
When logged in I can see a list of all my groups (groups created by me highlighted) and can click on them to see the details.

## Group Details
When I click on a group I can see the details of the group. I can see the name, description and the tallied consent sheet with a number of users tallied.

Groups I created are editable. Groups I joined can be left.

Each group has a share code that allows other users to join. Additionally public consent sheet can be imported without having the user join the group. this import is a snapshot where an anonymous sheet is created. Anonymous sheets can be removed by the creator of the group.

```