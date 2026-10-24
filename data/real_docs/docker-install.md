The Docker Scout CLI plugin comes pre-installed with Docker Desktop.

If you run Docker Engine without Docker Desktop,
Docker Scout doesn't come pre-installed,
but you can install it as a standalone binary.

## Installation script

To install the latest version of the plugin, run the following commands:

[code example]

> [!NOTE]
>
> Always examine scripts downloaded from the internet before running them
> locally. Before installing, make yourself familiar with potential risks and
> limitations of the convenience script.

## Manual installation

1. Download the latest release from the releases page.
2. Create a subdirectory under $HOME/.docker called scout .

 [code example]

3. Extract the archive and move the docker-scout binary to the $HOME/.docker/scout directory.
4. Make the binary executable: chmod +x $HOME/.docker/scout/docker-scout .
5. Add the scout subdirectory to your .docker/config.json as a plugin directory:

 [code example]

 Substitute with your username on the system.

 > [!NOTE]
 > The path for cliPluginsExtraDirs must be an absolute path.

1. Download the latest release from the releases page.
2. Create a subdirectory under $HOME/.docker called scout .

 [code example]

3. Extract the archive and move the docker-scout binary to the $HOME/.docker/scout directory.
4. Make the binary executable:

 [code example]

5. Authorize the binary to be executable on macOS:

 [code example]

6. Add the scout subdirectory to your .docker/config.json as a plugin directory:

 [code example]

 Substitute with your username on the system.

 > [!NOTE]
 > The path for cliPluginsExtraDirs must be an absolute path.

1. Download the latest release from the releases page.
2. Create a subdirectory under %USERPROFILE%/.docker called scout .

 [code example]

3. Extract the archive and move the docker-scout.exe binary to the %USERPROFILE%\.docker\scout directory.
4. Add the scout subdirectory to your .docker\config.json as a plugin directory:

 [code example]

 Substitute with your username on the system.

 > [!NOTE]
 > The path for cliPluginsExtraDirs must be an absolute path.

## Container image

The Docker Scout CLI plugin is also available as a container image.
Use the docker/scout-cli to run docker scout commands without installing the CLI plugin on your host.

[code example]

## GitHub Action

The Docker Scout CLI plugin is also available as a GitHub action.
You can use it in your GitHub workflows to automatically analyze images and evaluate policy compliance with each push.

Docker Scout also integrates with many more CI/CD tools, such as Jenkins, GitLab, and Azure DevOps.
Learn more about the integrations available for Docker Scout.