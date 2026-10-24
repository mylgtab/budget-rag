Insights shows organization administrators how people in their organization
use Docker Desktop. Use it to track adoption, spot version and platform
patterns, and see where builds, containers, images, and extensions are in
use.

> [!TIP]
>
> After
> upgrading to Docker Business,
> you must reach out to your Docker account team to enable Insights for
> your organization.

## Prerequisites

To use Insights, you must meet the following requirements:

- A Docker Business subscription
- Administrators must
 enforce sign-in
 for users
- Docker Desktop users must have
 Send usage
 statistics
 enabled ( analyticsEnabled ). You can set this for every user through
 Settings
 Management.

## View Insights {#view-insights-for-organization-users}

1. Sign in to Docker Home and select your
 organization.
1. Select Docker Desktop , then Desktop insights .
1. Select a time period: 1 Week , 1 Month , or 3 Months . Data
 may be delayed 24–48 hours. Last updated shows the sync date.

## Export Docker Desktop user data

1. Sign in to Docker Home and select your
 organization.
1. Select Docker Desktop , then Desktop insights .
1. Select Export Docker Desktop users . The CSV file downloads
 automatically. It includes the standard
 member CSV fields,
 plus these Insights columns:

 | Column | Description |
 | :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
 | Last Logged-in Date | Last browser sign-in to Docker Hub or Docker Home |
 | Docker Desktop Version | Last Docker Desktop version the user ran |
 | Last Seen Date | Last time the user ran Docker Desktop |
 | Opted Out Analytics | Whether the user turned off Send usage statistics |

## Reference

The Insights dashboard is organized into sections that capture each area of
Docker Desktop activity. Refer to these tables when a value looks
unexpected, when you need to explain a metric to someone else, or when
you're deciding which section answers a question about adoption, build
health, or image usage.

The Docker Desktop users section shows how many people in your organization
run Docker Desktop and how that number changes over time. Use it to measure
adoption and to find users missing from the active counts. Active counts
include only users who send analytics.

| Data | Description |
| :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Active members | Users who used Docker Desktop and signed in with a licensed account in your organization, or with an email address from a domain associated with your organization. |
| Total org members | Users who have used Docker Desktop, regardless of their Insights activity. |
| Members opted out of analytics | Organization members who opted out of sending analytics. |
| Registered users | Users linked to unassociated machines whose email addresses Docker captured, and those emails are outside your organization's domain. |
| Active users (graph) | Total active users over time. |

The Builds section shows how often users build images, how long builds take,
and how many succeed. Use it to spot slow or failing builds across the
organization and to gauge how much of your Docker Desktop usage is build
activity.

| Data | Description |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Average build per user | Average builds per active user. A build includes any time a user runs one of: docker buildx bake , docker buildx build , docker buildx f , docker builder build , docker builder f , docker compose build , or docker image build . |
| Average build time | Average build time per build. |
| Build success rate | Percentage of builds that exited normally. A failed build is any build that exits abnormally. |
| Total builds (graph) | Successful builds versus failed builds over time. |

The Containers section shows how many containers active users run and how
that activity trends over time. Use it to see how heavily your organization
relies on Docker Desktop for running workloads, not only for building them.

| Data | Description |
| :------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Total containers run | Containers run by active users in the Docker Desktop GUI, with docker run , or with docker compose . |
| Average number of containers run | Average containers run per active user. |
| Containers run by active users (graph) | Containers run over time by active users. |

The Docker Desktop usage section shows which versions, operating systems,
and interfaces your users run. Use it to plan upgrades, find users on
outdated versions, and understand whether your organization works mainly
through the CLI or the GUI.

| Data | Description |
| :-------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Most used version | Most used Docker Desktop version in your organization. |
| Most used OS | Most used operating system. |
| Versions by active users (graph) | Active users per Docker Desktop version. See the Docker Desktop release notes. |
| Interface by active users (graph) | Active users by interface. A CLI user has run a docker command. A GUI user has used the Docker Desktop graphical interface. |

The Docker Hub images section shows which images your users pull and push,
and how often. Use it to see which images matter most to your organization
and to confirm that users pull from the sources you expect. Image data
covers Docker Hub only. Third-party registries and mirrors are excluded.

| Data | Description |
| :----------------- | :------------------------------------------------------------------------------------------------------ |
| Total pulled images | Images pulled by active users. |
| Total pushed images | Images pushed. |
| Top pulled images | Top images pulled, and how many times each was pulled. |

The Extensions section shows how widely Docker Desktop extensions are used
in your organization and which ones users install most. Use it to find
popular tools worth supporting and to spot extensions you did not
expect.

| Data | Description |
| :---------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| Percentage of org with extensions installed | Percentage of users with at least one extension installed. |
| Top extensions installed in the organization | Top extensions installed, and how many users installed each one. |

## Next steps

- Activity logs for a
 record of organization and repository changes.
- Insights FAQs
 to troubleshoot missing data.