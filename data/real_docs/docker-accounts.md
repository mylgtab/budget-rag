## Individual accounts

### What is a Docker ID?

A Docker ID is a username for your Docker account that lets you access Docker
products. To create a Docker ID you need one of the following:

- An email address
- A Google account
- A GitHub account

Your Docker ID must be between 4 and 30 characters long, and can only contain
numbers and lowercase letters. You can't use any special characters or spaces.

For more information, see
Create a Docker account.

### Can I change my Docker ID?

No. You can't change your Docker ID once it's created. If you need a different
Docker ID, you must create a new Docker account with a new Docker ID.

Docker IDs can't be reused after deactivation.

### What if my Docker ID is taken?

All Docker IDs are first-come, first-served except for companies that have a
U.S. Trademark on a username.

If you have a trademark for your Docker ID,
Docker Support can retrieve the
Docker ID for you.

### Why did one of my personal access tokens disappear?

Signing in to Docker Desktop creates an auto-generated personal access
token for CLI authentication. An account can have five of these tokens.
When Docker Desktop creates another one, it deletes the least recently
used auto-generated token. A token that has never been used is ranked
by when it was created. The deleted token is removed from your token
list.

Tokens you create yourself are not deleted this way. They stay in the
list until you delete them. A revoked token stays in the list with a
status of Revoked .

For how these tokens are created and how to tell them apart, see
Auto-generated PATs.

### Why does sign-in fail with "Incorrect authentication credentials"?

 docker login returns Incorrect authentication credentials when the
username and secret don't match a credential that can sign in. The
message is the same when a personal access token is wrong, expired,
inactive, or revoked, and when the username is not the account that
owns the token.

Check the following:

1. The username is the Docker ID of the account that owns the token.
 Use an organization name only with an
 organization access token.
2. You pasted the full token, with no spaces or line breaks. Docker
 shows a token only once. If you no longer have it,
 create a new personal access token.
3. On the Personal access tokens page, find the token and use its
 status:
 - Expired: Create a new token. You can't change the expiration
 date.
 - Inactive: Select Activate .
 - Revoked: The token can't be used again. Delete it and create
 a new one.

## Organizations

### What's an organization name or namespace?

The organization namespace and the organization name are different.

The namespace is the permanent identifier for the organization. Image names
use it as the first part, as in namespace/image:tag . You can't change it,
and it can't match an existing Docker ID.

The organization name is the public name of the organization. You can change
it.

For the fields you set when you create an organization, see
Create a Docker organization.

### How can I see how many active users are in my organization?

If your organization uses a Software Asset Management tool, you can use it to
find out how many users have Docker Desktop installed. If your organization
doesn't use this software, you can run an internal survey
to find out who is using Docker Desktop.

For more information, see
Identify your Docker users and their Docker accounts.

### Do users need to authenticate with Docker before an owner can add them to an organization?

No. Organization owners can invite users with their email addresses, and also
assign them to a team during the invite process.

### Can I force my organization's members to authenticate before using Docker Desktop and are there any benefits?

Yes. You can
enforce sign-in.

Some benefits of enforcing sign-in are:

- Ensures users receive the benefits of your subscription.
- Ensures security features like
 Image Access Management
 and
 Registry Access Management
 are applied.
- Ensures you gain insights into users' activity.

### Can I convert my personal Docker ID to an organization account?

Yes. You can convert your user account to an organization account. Once you
convert a user account into an organization, it's not possible to
revert it to a personal user account.

For prerequisites and instructions, see
Convert an account into an organization.

### Can I convert an individual account that uses single sign-on?

No. Convert shows "Your account uses single sign-on. Contact your
administrator to manage these settings."

### Why can't I sign in after converting my account to an organization?

Converting signs you out and removes your email address from every Docker
account, so you can no longer sign in with it. Sign in with the Docker ID you
named as the owner and select the organization in Docker Home. If you named
someone else as the owner, sign up again and ask that owner to invite you. See
Convert a Docker account to an organization
for the full explanation.

### Do organization invitees take up seats?

Yes. A user invited to an organization will take up one of the provisioned
seats, even if that user hasn’t accepted their invitation yet.

To manage invites, see Manage organization members.

### Do organization owners take a seat?

Yes. Organization owners occupy a seat.

### What is the difference between user, invitee, seat, and member?

- User: Docker user with a Docker ID.
- Invitee: A user that an administrator has invited to join an organization but
 has not yet accepted their invitation.
- Seats: The number of purchased seats in an organization.
- Member: A user who has received and accepted an invitation to join an
 organization. Member can also refer to a member of a team within an
 organization.

### If I have two organizations and a user belongs to both organizations, do they take up two seats?

Yes. In a scenario where a user belongs to two organizations, they take up one
seat in each organization.

### Why is Insights data missing for some users?

Older versions of Docker Desktop may omit some metrics. Update those users to
the latest Docker Desktop release.

For prerequisites and how to open Insights, see
Insights.

### Why are opted-out users missing from Insights?

Insights includes a user only when Send usage statistics 
( analyticsEnabled ) is on. Turn the setting on for users who opted out. At
scale, use
Settings
Management
and set analyticsEnabled to true .

### Why is Docker Engine usage missing from Insights?

Only Docker Desktop sends Insights data. A standalone Docker Engine install
sends none.

### Why are some users excluded from Insights?

Insights includes users who sign in with an account associated with your
organization. To include the rest,
enforce sign-in.

### Why does Insights show no data?

Insights may show no data until you verify your organization's domain.
Verify the
domain.

### Companies

#### Can I use a parent company if some of my organizations don’t have a Docker Business subscription?

Yes, but you can only add organizations with a Docker Business subscription
to a company. For more details, see Add more organizations.

#### What happens if one of my organizations downgrades from Docker Business, but I still need access as a company owner?

To access and manage a nested organization, it must have a Docker Business
subscription. If an organization downgrades from Docker Business, its owner must
manage it outside of the company. For more details, see
Add more organizations.

#### Do company owners occupy a subscription seat?

Company owners don't occupy a seat unless one of the following is true:

- They are added as a member of an organization under your company
- SSO is enabled and the company owner signs in through SSO, which
 automatically adds them as an organization member

When you first create a company, your account is both a company owner and an
organization owner, so it occupies a seat as long as you remain an organization
owner. To free up that seat,
assign another user as the organization owner
and remove yourself from the organization. You keep full administrative access
as a company owner without using a subscription seat.

#### What permissions does the company owner have in the associated/nested organizations?

Company owners can navigate to the Organizations page to view all their
nested organizations in a single location. They can also view or edit
organization members and change single sign-on (SSO) and System for
Cross-domain Identity Management (SCIM) settings. Changes to company settings
impact all users in each organization under the company.

For more information, see Roles and permissions.