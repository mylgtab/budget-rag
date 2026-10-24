> [!WARNING]
>
> Uninstalling Docker Desktop destroys Docker containers, images, volumes, and
> other Docker-related data local to the machine, and removes the files generated
> by the application. To preserve important data before uninstalling, refer to the back up and restore data section.

#### From the GUI

1. From the Windows Start menu, select Settings > Apps > Apps & features .
2. Select Docker Desktop from the Apps & features list and then select Uninstall .
3. Select Uninstall to confirm your selection.

#### From the CLI

1. Locate the installer:
 [code example]
2. Uninstall Docker Desktop. 
 - In PowerShell, run:
 [code example]
 - In the Command Prompt, run:
 [code example]

After uninstalling Docker Desktop, some residual files may remain which you can remove manually. These are:

[code example]
 

#### From the GUI

1. Open Docker Desktop. 
2. In the top-right corner of the Docker Desktop Dashboard, select the Troubleshoot icon.
3. Select Uninstall .
4. When prompted, confirm by selecting Uninstall again.

You can then move the Docker application to the trash. 

#### From the CLI

Run:

[code example]

You can then move the Docker application to the trash. 

> [!NOTE]
> You may encounter the following error when uninstalling Docker Desktop using the uninstall command.
>
> [code example]
>
> The operation not permitted error is reported either on the file .com.apple.containermanagerd.metadata.plist or on the parent directory /Users//Library/Containers/com.docker.docker/ . This error can be ignored as you have successfully uninstalled Docker Desktop.
> You can remove the directory /Users//Library/Containers/com.docker.docker/ later by allowing Full Disk Access to the terminal application you are using ( System Settings > Privacy & Security > Full Disk Access ).

After uninstalling Docker Desktop, some residual files may remain which you can remove:

[code example]

To uninstall Docker Desktop for Ubuntu:

1. Remove the Docker Desktop application. Run:

 [code example]

 This removes the Docker Desktop package itself but doesn’t delete all of its files or settings.

2. Manually remove leftover file.

 [code example]

 This removes configuration and data files at $HOME/.docker/desktop , the symlink at /usr/local/bin/com.docker.cli , and purges the remaining systemd service files.

3. Clean up Docker config settings. In $HOME/.docker/config.json , remove the credsStore and currentContext properties.

 These entries tell Docker where to store credentials and which context is active. If they remain after uninstalling Docker Desktop, they may conflict with a future Docker setup.

To uninstall Docker Desktop for Debian, run:

1. Remove the Docker Desktop application:

 [code example]

 This removes the Docker Desktop package itself but doesn’t delete all of its files or settings.

2. Manually remove leftover file.

 [code example]

 This removes configuration and data files at $HOME/.docker/desktop , the symlink at /usr/local/bin/com.docker.cli , and purges the remaining systemd service files.

3. Clean up Docker config settings. In $HOME/.docker/config.json , remove the credsStore and currentContext properties.

 These entries tell Docker where to store credentials and which context is active. If they remain after uninstalling Docker Desktop, they may conflict with a future Docker setup.

To uninstall Docker Desktop for Fedora:

1. Remove the Docker Desktop application. Run:

 [code example]

 This removes the Docker Desktop package itself but doesn’t delete all of its files or settings.

2. Manually remove leftover file.

 [code example]

 This removes configuration and data files at $HOME/.docker/desktop , the symlink at /usr/local/bin/com.docker.cli , and purges the remaining systemd service files.

3. Clean up Docker config settings. In $HOME/.docker/config.json , remove the credsStore and currentContext properties.

 These entries tell Docker where to store credentials and which context is active. If they remain after uninstalling Docker Desktop, they may conflict with a future Docker setup.

To uninstall Docker Desktop for Arch:

1. Remove the Docker Desktop application. Run:

 [code example]

 This removes the Docker Desktop package along with its configuration files and dependencies not required by other packages.

2. Manually remove leftover files.

 [code example]

 This removes configuration and data files at $HOME/.docker/desktop .

3. Clean up Docker config settings. In $HOME/.docker/config.json , remove the credsStore and currentContext properties.

 These entries tell Docker where to store credentials and which context is active. If they remain after uninstalling Docker Desktop, they may conflict with a future Docker setup.