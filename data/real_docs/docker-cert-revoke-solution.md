This guide provides steps to address a recent issue affecting some macOS users of Docker Desktop. The issue may prevent Docker Desktop from starting and in some cases, may also trigger inaccurate malware warnings. For more details about the incident, see the blog post.

> [!NOTE]
>
> Docker Desktop versions 4.28 and earlier are not impacted by this issue. 

## Available solutions

There are a few options available depending on your situation:

### Upgrade to Docker Desktop version 4.37.2 (recommended)

The recommended way is to upgrade to the latest Docker Desktop version which is version 4.37.2. 

If possible, update directly through the app. If not, and you’re still seeing the malware pop-up, follow the steps below:

1. Kill the Docker process that cannot start properly:
 [code example]
 
2. Make sure the malware pop-up is permanently closed. 

3. Download and install version 4.37.2.

4. Launch Docker Desktop. A privileged pop-up message displays after 5 to 10 seconds.

5. Enter your password.

You should now see the Docker Desktop Dashboard.

> [!TIP]
>
> If the malware pop-up persists after completing these steps and Docker is in the Trash, try emptying the Trash and rerunning the steps.

### Install a patch if you have version 4.32 - 4.36

If you can’t upgrade to the latest version and you’re seeing the malware pop-up, follow the steps below:

1. Kill the Docker process that cannot start properly:
 [code example]

2. Make sure the malware pop-up is permanently closed.

3. Download and install the patched installer that matches your current base version. For example if you have version 4.36.0, install 4.36.1.

4. Launch Docker Desktop. A privileged pop-up message displays after 5 to 10 seconds.

5. Enter your password.

You should now see the Docker Desktop Dashboard.

> [!TIP]
>
> If the malware pop-up persists after completing these steps and Docker is in the Trash, try emptying the Trash and rerunning the steps.

## MDM script

If you are an IT administrator and your developers are seeing the malware pop-up:

1. Make sure your developers have a re-signed version of Docker Desktop version 4.32 or later.
2. Run the following script:

 [code example]

## Homebrew casks

If you installed Docker Desktop using Homebrew casks, the recommended solution is to perform a full reinstall to resolve the issue.

To reinstall Docker Desktop, run the following commands in your terminal:

[code example]

These commands will update Homebrew and completely reinstall Docker Desktop, ensuring you have the latest version with the fix applied.