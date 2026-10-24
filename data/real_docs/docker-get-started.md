Use a cloud sandbox to review a project with a coding agent or build and run
an application from a shell, without setting up the project on your computer.

You can complete either workflow in the browser. An optional step shows how
to open the same project in VS Code or Cursor over SSH.

## Before you begin

You need a personal Docker account with an active
Docker Agentic Platform subscription.

Both workflows use a public sample project, so you don't need a GitHub token.

## Choose a workflow

- Use a coding agent to have Claude Code review a sample
 project and save its findings. You need an Anthropic API key.
- Use a shell to build and run the sample application and preview
 it in your browser. You don't need a model provider API key.

## Use a coding agent

Add an Anthropic API key under Secrets or enter it when you launch the
sandbox. Your model provider bills inference separately from Docker's sandbox
compute charges. For other agents and their credentials, see Kits
and Secrets.

### Launch Claude Code

1. Open Docker Agentic Platform and
 select + New sandbox .
2. Choose the Claude Code kit.
3. Add your Anthropic API key if it isn't already saved. Don't enter it in
 the agent's prompt or in a file inside the sandbox.
4. Keep the defaults and select Run .

On your first launch, the default Open network policy permits outbound
access to any host. If you're using a custom policy, make sure it permits
GitHub and your model provider. See Network policies.

When the sandbox is ready, its terminal opens with Claude Code.

### Give the agent a task

Your local files aren't mounted in a cloud sandbox. Ask Claude Code to clone
and review a public sample project:

[code example]

Claude Code summarizes the project in the conversation and saves the review
at /home/agent/workspace/review.md . You can ask follow-up questions or give
it another task in the same session.

Continue to keep your work, or
open the project in your editor.

## Use a shell

### Launch a shell

The Shell kit starts a Bash shell without an agent.

1. Open Docker Agentic Platform and
 select + New sandbox .
2. Open the kit picker and choose shell .
3. If saved secrets or a GitHub token are selected, deselect them for this
 walkthrough. You don't need MCP tools either.
4. In the network policy picker, select Balanced to permit access to
 GitHub, Docker Hub, and npm. Keep the compute and timer defaults and select
 Run .

If you use a custom network policy, make sure it permits GitHub, Docker Hub,
and npm. See Network policies.

When the sandbox is ready, its terminal opens with a Bash shell.

### Build and run an application

Your local files aren't mounted in a cloud sandbox. In the browser terminal,
clone a public sample project:

[code example]

The Shell kit includes Docker Engine. Build the application's container image:

[code example]

The build installs the application's dependencies and compiles it inside the
sandbox. When it finishes, start a container and publish its port:

[code example]

### Preview the application

1. Select Connect on the sandbox's detail page.
2. Under Connect via a Port , enter 3000 and select Open Port .
3. Open the generated URL in your browser.

You should see the Welcome to Docker application. The application runs in the
cloud sandbox, so you can try it without installing Docker or Node.js on your
computer.

The generated URL is public. Close the port in Connect when you've finished
previewing the application.

Continue to keep your work, or
open the project in your editor.

## Keep your work

The cloned project and any files you create are stored in the sandbox. Files
don't sync automatically with your computer or a remote repository. They remain available
when you pause and resume the sandbox, but are lost when you delete it.

To keep files outside the sandbox, use the CLI to
transfer files, or commit
and push changes to a repository. Include a
GitHub credential when launching a sandbox that
needs to push changes.

## Open the project in your editor (optional)

Open the project in VS Code or Cursor over SSH to edit the application. Your
editor runs on your computer, while the files and terminal commands stay in
the cloud sandbox.

1. Install the Docker Sandboxes CLI,
 version 0.45.0 or later.
2. In a terminal on your computer, sign in with the same Docker account you
 used in the Console and configure cloud SSH access:

 [code example]

3. Find your sandbox in the list and copy its sbx_ -prefixed ID. Test the
 connection, replacing with that ID:

 [code example]

 A successful connection opens a shell inside the cloud sandbox. Run exit 
 to return to your computer's terminal.
4. In VS Code, install the
 Remote - SSH extension.
 In Cursor, install its Remote - SSH support.
5. Open your editor's Command Palette and run Remote-SSH: Connect to Host .
 Enter @sbx_cloud , using the same ID as in the SSH command.
6. Open /home/agent/workspace in the remote window. Both workflows clone
 the application into project . The coding agent also saves review.md 
 in the workspace.

The first connection installs the editor's server inside the sandbox.

If you followed the coding agent workflow, download the review run this command in a terminal on your computer:

[code example]

## Pause, keep running, or delete the sandbox

Closing the browser or disconnecting your editor leaves the sandbox running.
Commands and background processes can continue until you pause or delete the
sandbox, or its timer expires. Compute is billed while the sandbox runs, even
when no commands are running.

Return to Sandboxes in the Console and choose what to do next:

- Pause the sandbox to stop compute charges and keep its files. Confirm that
 it is paused in the list. To continue later, reopen the sandbox and resume
 it. Resuming starts a fresh timer with the original duration.
- Leave it running if the agent still has work to do or to keep the application available. Check the expiration
 time: the default Stop action stops the sandbox after one hour, including
 background processes, and keeps its files.
- Delete it when you no longer need it. Push any source changes
 you want to keep first. Deletion removes files stored only in the sandbox.

For more detail, see Lifecycle actions.
To run a task from your own terminal, follow the
cloud CLI walkthrough.
For programmatic workflows, see the
Sandboxes API quickstart.

## Sandbox options

After launch, you can't change the selected credentials, tools, network policies,
or compute size. Configure these options before selecting Run :

| Option | What to choose |

| Agent credentials | Add the API keys or tokens your kit needs. Saved credentials are reused by default; deselect optional credentials you don't want to include. See Secrets. |
| GitHub token | Provide a token for Copilot or for cloning private repositories and pushing changes. Copilot uses the same token for both. Repository access is optional for other agents. See GitHub credential. |
| Network policies | Review the hosts and services the sandbox can reach. See Network policies. |
| MCP tools | Choose the servers your agent can use and authorize them if prompted. See MCP. |
| Compute and platform | Choose CPU and memory resources. Under Platform , use auto or a platform supported by the kit's image. See Sandbox platforms. |
| Timer | Under Run for , choose 1 to 24 hours. Under When the time is up , choose Stop , Delete , or Restart if offered. See Lifecycle actions. |

The launcher remembers your policy selections from the previous launch in the
same browser. Policies marked Always applied are selected automatically.
Review the selected policies before launching. Selecting Balanced alongside
 Open doesn't restrict Open's access; see How policies combine.