# What’s new in Grafana v12.0

Welcome to Grafana 12.0! We have a _lot_ to share. This release marks general availability for Grafana Drilldown (previously Explore Metrics, Logs, and Traces), Grafana-managed alerts and recording rules, Cloud migration, and plugin management tooling. You can also try new preview and experimental tools: Sync your dashboards directly to a GitHub repository with Git Sync, and try our new Terraform provider and CLI. Add tabs, new layouts and conditional logic to your dashboards, and load tables and geomaps far faster. Join and transform data limitlessly from multiple sources with SQL Expressions. In Grafana Cloud and Enterprise, sync your users and teams instantly from your SAML identity provider using SCIM (the System for Cross-Domain Identity Management). Lastly, don't forget to try on one of several new color themes for the user interface.

Read on to learn about these and more improvements to Grafana!

For even more detail about all the changes in this release, refer to the changelog. For the specific steps we recommend when you upgrade to v12.0, check out our Upgrade Guide.

## Breaking changes in Grafana v12.0

For Grafana v12.0, we've also provided a list of breaking changes to help you upgrade with greater confidence. For our purposes, a breaking change is any change that requires users or operators to do something. This includes:

- Changes in one part of the system that could cause other components to fail
- Deprecations or removal of a feature
- Changes to an API that could break automation
- Changes that affect some plugins or functions of Grafana
- Migrations that can’t be rolled back

For each change, the provided information:

- Helps you determine if you’re affected
- Describes the change or relevant background information
- Guides you in how to mitigate for the change or migrate
- Provides more learning resources