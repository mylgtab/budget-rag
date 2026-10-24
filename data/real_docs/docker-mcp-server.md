The Docker Hub MCP Server is a Model Context Protocol (MCP) server that
interfaces with Docker Hub APIs to make rich image metadata accessible to LLMs,
enabling intelligent content discovery and repository management.

For more information about MCP concepts and how MCP servers work, see the Docker MCP Catalog and Toolkit overview page.

## Key features

- Advanced LLM context: Docker's MCP Server provides LLMs with detailed, structured context for Docker Hub images, enabling smarter, more relevant recommendations for developers, whether they're choosing a base image or automating CI/CD workflows.
- Natural language image discovery: Developers can find the right container image using natural language, no need to remember tags or repository names. Just describe what you need, and Docker Hub will return images that match your intent.
- Simplified repository management: Hub MCP Server enables agents to manage repositories through natural language fetching image details, viewing stats, searching content, and performing key operations quickly and easily.

## Install Docker Hub MCP server

1. In Docker Desktop, select MCP Toolkit and select the Profiles tab,
 then select Create profile to create a new profile, or select an existing
 profile to use.
2. Select the Catalog tab, search for Docker Hub , and select Add to 
 to add it to your profile.
3. Select the Profiles tab, select the profile you added Docker Hub to, and
 select the configuration icon on the Docker Hub MCP server. Enter your Docker
 Hub username and personal access token (PAT).
4. Under the Clients section of the same profile, if you already have a
 client connected it connects automatically. Otherwise, select the plus icon
 to add a client.

For more details on setting up profiles and connecting clients, see
Get started with Docker MCP Toolkit.

## Use Claude Desktop as a client

1. Add the Docker Hub MCP Server configuration to your claude_desktop_config.json :

 
 

 [code example]

 Where :
 - /FULL/PATH/TO/YOUR/docker-hub-mcp-server is the complete path to where you cloned the repository

 
 

 [code example]

 Where :
 - YOUR_DOCKER_HUB_USERNAME is your Docker Hub username.
 - YOUR_DOCKER_HUB_PERSONAL_ACCESS_TOKEN is Docker Hub personal access token
 - /FULL/PATH/TO/YOUR/docker-hub-mcp-server is the complete path to where you cloned the repository

 
 

1. Save the configuration file and completely restart Claude Desktop for the changes to take effect.

## Usage with Visual Studio Code

1. Add the Docker Hub MCP Server configuration to your User Settings (JSON)
 file in Visual Studio Code. You can do this by opening the Command Palette and
 typing Preferences: Open User Settings (JSON) .

 
 

 [code example]

 Where :
 - /FULL/PATH/TO/YOUR/docker-hub-mcp-server is the complete path to where you cloned the repository

 
 

 [code example]

 Where :
 - YOUR_DOCKER_HUB_USERNAME is your Docker Hub username.
 - YOUR_DOCKER_HUB_PERSONAL_ACCESS_TOKEN is Docker Hub personal access token
 - /FULL/PATH/TO/YOUR/docker-hub-mcp-server is the complete path to where you cloned the repository

 
 

1. Open the Command Palette and type MCP: List Servers .
1. Select docker-hub and select Start Server .

## Using other clients

To integrate the Docker Hub MCP Server into your own development
environment, see the source code and installation instructions on the
 hub-mcp GitHub repository.

## Usage examples

This section provides task-oriented examples for common operations with Docker Hub
tools.

### Finding images

[code example]

### Repository management

[code example]

### Pull/push images

[code example]

### Tag management

[code example]

### Docker Hardened Images

[code example]
> [!NOTE]
> To access Docker Hardened Images, a subscription is required. If you're interested in using Docker Hardened Images, visit Docker Hardened Images.

## Reference

This section provides a comprehensive listing of the tools you can find
in the Docker Hub MCP Server.

### Docker Hub MCP server tools

Tools to interact with your Docker repositories and discover content on Docker Hub.

| Name | Description |

| check-repository | Check repository |
| check-repository-tag | Check repository tag |
| check-repository-tags | Check repository tags |
| create-repository | Creates a new repository |
| docker-hardened-images | Lists available Docker Hardened Images in specified namespace |
| get-namespaces | Get organizations/namespaces for a user |
| get-repository-dockerfile | Gets Dockerfile for repository |
| get-repository-info | Gets repository info |
| list-repositories-by-namespace | Lists repositories under namespace |
| list-repository-tags | List repository tags |
| read-repository-tag | Read repository tag |
| search | Search content on Docker Hub |
| set-repository-dockerfile | Sets Dockerfile for repository |
| update-repository-info | Updates repository info |