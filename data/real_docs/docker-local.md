The sbx policy command manages the local policy on your machine. The local
policy contains network access rules. Rules apply to all sandboxes on the
machine when you use the global scope, or to a single sandbox when scoped by
name.

Local policy interacts with organization governance as follows:

- No org governance: the local policy controls what sandboxes can access.
- Org governance active: only organization allow rules grant access, so
 local allow rules are inactive and can't expand what the organization permits.
 Local deny rules are still evaluated, so you can restrict access further than
 the organization policy does. To list inactive rules, run
 sbx policy ls --include-inactive. See
 Monitoring.

See Organization policies for how organization governance
works.

For domain patterns, wildcards, CIDR ranges, and filesystem path syntax, see
Policy concepts.

## Default preset

Outbound TCP traffic passes through a proxy on your host, which enforces access
rules on every connection. Non-HTTP TCP traffic, including SSH, can be allowed
with a hostname rule (for example, sbx policy allow network "myhost:22" ) or an
address-based rule. UDP requires the experimental feature and policy rules
described in Allow outbound UDP. ICMP is blocked.

If you haven't chosen a default preset, the CLI prompts you before it runs a
sandbox. Running sbx policy reset clears the preset and prompts you to choose
again:

[code example]

| Preset | Description |

| Open | All outbound TCP traffic is allowed. Equivalent to adding a wildcard allow rule with sbx policy allow network " ". |
| Balanced | Default deny, with a baseline allowlist covering AI provider APIs, package managers, code hosts, container registries, and common cloud services. |
| Locked Down | No baseline allow rules. Destinations need an allow rule from you or a kit. |

Presets initialize the global policy. Built-in agent kits and other kits can
add per-sandbox allow rules, including under Locked Down ( deny-all ). The
preset isn't an explicit deny rule that overrides those allowances.

Under Balanced and Locked Down, a sandbox request that no rule matches
is blocked and asks for your approval instead of being denied outright, so you
can open access to each destination as a sandbox needs it. See
Approval-required access.

To inspect the rules a kit adds to a sandbox, run:

[code example]

To block a destination allowed by a kit, add an explicit deny rule:

[code example]

Deny rules take precedence over allow rules. See
Policy precedence.

The Balanced preset's baseline allowlist is a good starting point for most
workflows. Run sbx policy ls to see exactly which rules it includes.

> [!NOTE]
> If your organization manages sandbox policies centrally, organization rules
> take precedence over the preset you select here. See
> Organization policies.

### Non-interactive environments

In non-interactive environments such as CI pipelines or headless servers, the
interactive prompt can't be displayed. Use sbx policy init to set the
preset before running any other sbx commands:

[code example]

Available values are allow-all, balanced, and deny-all.

## Managing rules

A rule covers a destination host. It can also name HTTP methods and paths to
narrow the match to part of that host.

### Network rules

Use sbx policy allow and
 sbx policy deny to add or restrict access
on top of the active preset. Changes take effect immediately. Rules apply to
all sandboxes by default:

[code example]

Pass --sandbox to scope a rule to one sandbox:

[code example]

As of v0.38.0, you can also set per-sandbox deny rules at creation time with
 --deny-network on sbx create or sbx run, instead of adding them after the
fact:

[code example]

Pass the flag multiple times to deny more than one host. Rules added this way
appear in sbx policy ls and can be removed with
 sbx policy rm network --sandbox --resource.

Specify multiple hosts in one command with a comma-separated list:

[code example]

Remove a rule by resource or by rule ID:

[code example]

To remove a sandbox-scoped rule, pass --sandbox:

[code example]

### HTTP method and path rules

Add --method to an allow or deny rule to match specific HTTP methods on a
host, and --path to restrict it to part of the host's URL space:

[code example]

Quote the path so your shell doesn't expand the wildcard. Pass several methods
as a comma-separated list:

[code example]

 --method ANY matches every HTTP method, and --path defaults to / when
you omit it:

[code example]

 ANY can't be combined with specific methods, and a path without a method is
rejected. Pass a method, or use ANY when you mean every method.

Method names are case-insensitive. The accepted values are GET, HEAD,
 POST, PUT, PATCH, DELETE, OPTIONS, CONNECT, and TRACE.

A path must start with / and be canonical. It can't contain a query string, a
fragment, percent-encoding, control characters, surrounding whitespace,
repeated or trailing slashes, or dot segments such as. and... Each rule
takes one path. Repeating --path keeps only the last value, and a comma is
read as part of the path, so add a separate rule for each path:

[code example]

Hosts follow the same patterns as network rules and can include a port. Write
the host on its own, without a scheme, so an HTTP rule takes api.example.com 
rather than https://api.example.com.

A local HTTP rule takes a hostname. To match an IP address or a CIDR range,
add a plain network rule for that destination instead.

Deny rules take the same flags, which is the usual way to carve a method or
path out of a broader allow:

[code example]

For how the two layers combine, see
HTTP rules.

Remove an HTTP rule by naming the same qualifiers you added it with, or by
rule ID:

[code example]

List HTTP rules with --type http, or see them alongside network rules in a
wide listing, where the METHOD and PATH columns are empty for rules that
match a whole host:

[code example]

> [!NOTE]
> sbx policy check network and sbx policy log don't evaluate or display
> HTTP methods and paths. A check reports the decision for the host, which can
> differ from the decision for a specific method and path on that host.

## Inspecting rules

To inspect which policies are active and where they come from, use
 sbx policy ls. Use --source to filter by origin ( local, org, kit ),
 --decision to filter by outcome ( allow, deny ), and --wide for
rule-level detail including rule IDs. To inspect a single policy or rule in
full, use sbx policy inspect. See
Monitoring.

### Allow outbound UDP

Outbound UDP is experimental and disabled by default. Turn on experimental
features and UDP egress before adding UDP allow rules:

[code example]

Local allow rules apply to TCP by default. Use --protocol udp for UDP or
 --protocol tcp,udp for both. Deny rules apply to both protocols by default.
Use --protocol to restrict a deny rule to one protocol.

UDP follows the same organization and local policy precedence as TCP. It is
refused when the destination requires an HTTP, SOCKS5, system, or PAC-selected
proxy, because those proxies can't carry UDP. ICMP remains blocked.

UDP to local-network destinations is blocked before any policy is evaluated,
so no allow rule can permit it, including one that allows all hosts. This
covers multicast, link-local, and unspecified addresses, 255.255.255.255,
and the broadcast addresses of the host's networks. As a result, discovery
protocols that use multicast, such as mDNS and SSDP, don't work from a
sandbox. UDP to host.docker.internal isn't affected. The network log records
these connections under the rule.

Inspect UDP rules or check a destination:

[code example]

The CLI warns if you save a UDP rule while UDP egress is disabled.

## Testing policy

Before running a sandbox, you can check whether the current policy would allow
a network request with sbx policy check network:

[code example]

The output reports Allowed or Denied, along with governance and context
details. A denied check returns a non-zero exit status.

The target can be a hostname, a host:port pair, an IP address, or a URL.
Bare hostnames and IP addresses are evaluated against port 443. This is useful
for verifying custom rules or checking what the Locked Down preset blocks
before you start an agent.

A check never creates an approval request. A destination that a sandbox would
ask you to approve shows as Denied:, with a Reason: line of
 no matching allow rule (default deny), or approval required by policy under
organization governance.

To check policy in the context of a specific sandbox:

[code example]

### Resetting

To remove all custom rules and start fresh with a new preset, use
 sbx policy reset:

[code example]

This deletes the local policy store, restarts the daemon, and prompts you to
choose a new preset. Running sandboxes stop when the daemon shuts down. Pass
 --force to skip the confirmation prompt:

[code example]

## Troubleshooting

### Local allow rules have no effect

If rules you add with sbx policy allow don't change sandbox behavior, your
organization likely has governance enabled. Run sbx policy ls to check: if
the summary block contains Governance: Managed by,
org governance is active. When it's active, local allow rules are inactive.
You can't use them to loosen restrictions the org policy imposes.

Inactive allow rules are hidden from sbx policy ls by default; run
 sbx policy ls --include-inactive to see them with an inactive status in
the STATUS column.

When organization governance is active, only organization allow rules can grant
access. Ask your admin to update the organization policy if you need access to
an additional resource. Local deny rules remain active, so you can use
 sbx policy deny to restrict access further.

### A domain is still blocked after adding an allow rule

If a domain remains blocked after you add a local allow rule, your organization
likely enforces governance, which makes local allow rules inactive. Run sbx
policy ls to check whether org governance is active; if the output starts with
a Governance: status line showing Managed by, it is. Add
 --include-inactive to confirm your rule shows an inactive status. If so,
the block can only be lifted by updating the org policy in Docker Home or via
the API.

### An HTTP method or path is blocked on an allowed host

A host that a network rule allows can still have individual methods or paths
denied by an HTTP rule. Run sbx policy ls --type http to see which HTTP rules
apply. sbx policy check network reports the decision for the host only, so it
shows a host as allowed even when the specific request is denied. See
HTTP method and path rules.

### A request is blocked with "Approval required"

The destination needs your confirmation. Either no allow or deny rule matches
it and your machine isn't under organization governance, or an organization
policy allows it but requires approval first.

Run sbx policy approval ls to see the pending request and respond to it with
 sbx policy approval respond. Approving applies to later requests, not the one
that was blocked, so run the operation again afterward. See
Respond to an approval request.