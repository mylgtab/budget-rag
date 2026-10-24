# What’s new in Grafana v12.1

It’s 12.1 time! We’re really excited about GA for a new alert rule page that makes it easier to find what you need quickly, as well as the regression analysis transformation, helping you predict future data values or estimate missing data points that might not be exactly represented in the original dataset. Also, visualization actions now support custom variables. When triggered, actions prompt you to input whatever custom variable was defined, allowing you to tailor requests in real time without modifying dashboard configuration. This is super helpful for when you’re triggering alerts, filtering API calls, or sending user-defined parameters to external systems. And you can try out Grafana Advisor, which automatically detects plugin, data source, and SSO issues, keeping your Grafana instance healthy and secure.

Speaking of security, Grafana now supports Entra Workload Identity, simplifying OAuth and increasing security for instances using Microsoft Azure. Thanks to community contributor mehighlow for this feature!

We have one more community contributor to thank for this release. Chris Hodges delivered server-configurable quick time ranges for dashboards. Now you can define custom time range presets for the time picker on dashboards, perfect for teams that routinely analyze specific, context-driven time windows.

Keep reading to learn about what else we have in store for 12.1.

For even more detail about all the changes in this release, refer to the changelog. For the specific steps we recommend when you upgrade to v12.1, check out our Upgrade Guide.