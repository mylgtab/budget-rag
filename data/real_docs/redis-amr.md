The @redis/entraid 
package lets you authenticate your app to
Azure Managed Redis (AMR)
using Microsoft Entra ID.
You can authenticate using a system-assigned or user-assigned
managed identity,
a service principal,
an auth code flow,
or a DefaultAzureCredential instance.
The @redis/entraid code fetches and renews the authentication tokens for you automatically.

## Install

Install node-redis and
 @redis/entraid with the following commands:

[code example]

## Create a credentials provider instance

A credentials provider object obtains the authentication credentials you
need when you connect to Redis (see the Connect section below
for a connection example). The EntraIdCredentialsProviderFactory 
class provides a factory method for each type of credentials provider.
Import EntraIdCredentialsProviderFactory with the following code:

[code example]

Then, use the appropriate factory method to create your credentials provider:

- Use createForClientCredentials() 
 to authenticate with a service principal using a client secret.
- Use createForClientCredentialsWithCertificate() 
 to authenticate with a service principal using a certificate.
- Use createForSystemAssignedManagedIdentity() 
 to authenticate with a system-assigned managed identity.
- Use createForUserAssignedManagedIdentity() 
 to authenticate with a user-assigned managed identity.
- Use createForAuthorizationCodeWithPKCE() 
 for interactive authentication flows in user applications.
- Use createForDefaultAzureCredential() 
 to authenticate with Azure Identity's DefaultAzureCredential class.

The sections below describe these factory functions in more detail.

### Provider parameters

All these factory functions receive an object containing the parameters
to create the credentials provider. The object generally contains the following
fields, but specific factory methods add or omit particular parameters:

- clientId: A string containing the client ID.
- scopes: (Optional) A string or an array of strings defining the
 scopes
 you want to apply. Configure your client application to acquire a Microsoft Entra token for scope, https://redis.azure.com/.default or acca5fbb-b7e4-4009-81f1-37e38fd66d78/.default with the
 Microsoft Authentication Library (MSAL). Note that the entra-id-credentials-provider-factory 
 module exports a constant REDIS_SCOPE_DEFAULT for the default scope. See the
 DefaultAzureCredential example below to learn how to use this.
- authorityConfig: (Optional) Authority
 settings. See the authorityConfig section below for a full
 description.
- tokenManagerConfig: An object with fields that specify how to refresh the token.
 See the tokenManagerConfig section below for a full
 description.

#### tokenManagerConfig 

You can configure an authentication token to expire after a certain amount of
time, known as its *lifetime*. You must refresh a token before its lifetime
is over to continue using it (see
Configurable token lifetimes in the Microsoft identity platform
for more information). The tokenManagerConfig object lets you pass parameters to
specify how you want to manage token refreshes. The fields of the object are listed
below:

- expirationRefreshRatio: This is the fraction of the token's lifetime that should
 elapse before a refresh is triggered. For example, a value of 0.75 means the token
 should be refreshed when 75% of its lifetime has elapsed.
- retry: This object specifies the policy to retry refreshing the token if
 an error occurs. It has the following fields:
 - maxAttempts: The maximum number of times to attempt a refresh before
 aborting.
 - initialDelayMs: The delay (in milliseconds) before retrying after the
 first failed attempt.
 - maxDelayMs: The maximum time (in milliseconds) to wait between attempts
 to refresh.
 - backoffMultiplier: The
 exponential backoff
 for the time between attempts to refresh. For example, a value of 2
 will double the delay for each attempt. Use a value of 1 to keep
 the delay roughly constant.
 - jitterPercentage: (Optional) The maximum fraction of the calculated delay time to
 randomly add or subtract. For example, a value of 0.1 will add or subtract
 up to 10% of the delay time. This random component helps to prevent
 repeated collisions between clients that have the same retry settings.
 - isRetryable: (Optional) This specifies a function with the signature 
 (error, attempt) => boolean 
 where error is the error object from
 a failed attempt and attempt is the number of attempts previously made.
 This function classifies errors from the identity provider as 
 retryable (returning true ) or non-retryable (returning false ).
 Implement your own custom logic here to determine if a token refresh failure
 should be retried, based on the type of error. For example, a refresh failure
 caused by a transient network error would probably succeed eventually if you retry
 it, but an invalid certificate is generally a fatal error. If you don't supply a custom
 function in this parameter, the default behavior is to retry all types of errors.

#### authorityConfig 

The authorityConfig object has a type field that can take any of
the string values default, multi-tenant, or custom. If you use
 multi-tenant then you must also supply a tenantId field containing
the tenant ID string:

[code example]

If you use custom then you must also supply an authorityUrl 
containing the authority URL string:

[code example]
See Microsoft's Authority
docs for more information.

### Authenticate with a service principal

Use the createForClientCredentials() factory function to create a
credentials provider that authenticates to AMR using a
service principal (see the
Microsoft documentation to learn more about service principals).

You will need the following details of your service principal to make the connection:

- Client ID
- Client secret
- Tenant ID

The example below shows how to call createForClientCredentials(). Note that the
parameter object includes an extra field here for the
client secret.

[code example]

If you want to authenticate using a service principal with a certificate,
use createForClientCredentialsWithCertificate() to create the credentials
provider. This is similar to createForClientCredentials() but it takes
a clientCertificate parameter object instead of the clientSecret parameter.
This object has the following string fields:

- x5c: X.509 certificate.
- privateKey: The certificate's private key.
- thumbprintSha256: (Optional) SHA-256 hash of the certificate.

The example below shows how to call createForClientCredentialsWithCertificate() and
demonstrates the retry parameter in tokenManagerConfig:

[code example]

### Authenticate with a managed identity

You can authenticate to AMR using a managed identity (see the
Microsoft documentation to learn more about managed identities).

For a system-assigned managed identity, use the createForSystemAssignedManagedIdentity() factory function as shown in the example below:

[code example]

For a user-assigned managed identity, use createForUserAssignedManagedIdentity().
Here, the parameter object includes an extra field for
the user-assigned client ID.

[code example]

### Auth code flow with PKCE

*Auth code flow with Proof Key for Code Exchange (PKCE)* lets a client app
authenticate for access to web APIs and other restricted resources. This
requires a redirect URI to return control to your app after authentication.
See
Microsoft identity platform and OAuth 2.0 authorization code flow
for more information.

Use the createForAuthorizationCodeWithPKCE() factory method to use auth code flow
with PKCE. The example below shows the extra field redirectUri in the parameter
object:

[code example]

### Authenticate with DefaultAzureCredential {#def-az-cred}

The
 DefaultAzureCredential 
class in @azure/identity is designed for use during development. It simplifies
authentication by automatically trying different credentials until one succeeds.
See DefaultAzureCredential overview
in the Microsoft docs for more information.

The example below shows how to use createForDefaultAzureCredential():

[code example]

Note that when you use createForDefaultAzureCredential(), you must:

- Create your own instance of DefaultAzureCredential.
- Pass the same parameters to the factory method that you would use with the getToken() 
 method:
 - scopes: The Redis scope (use the exported REDIS_SCOPE_DEFAULT constant).
 - options: Any other options for the getToken() method.

## Connect

When you have created your credential provider instance, you are ready to
connect to AMR.
The example below shows how to pass the instance as a parameter to the standard
 createCluster() connection method.

[code example]

## RESP2 PUB/SUB limitations

If you are using the
RESP2
protocol, you should
be aware that pub/sub can
cause complications with reauthentication.

After a connection enters PUB/SUB mode, the socket is blocked and can't process
out-of-band commands like AUTH. This means that
connections in PUB/SUB mode can't be reauthenticated when the tokens are refreshed.
As a result, PUB/SUB connections will be evicted by the Redis proxy when their tokens expire. 
You must reconnect with fresh tokens when this happens.

## Note about transactions

If you use
transactions
in code that also uses token-based authentication, ensure that you use
the node-redis client multi/exec API rather than explicit commands to create
each transaction (see
Execute a transaction
for an example of correct usage).
This is because the token manager might attempt to reauthenticate while your code
issues the separate transaction commands, which will interfere with the transaction.
The transaction API handles this case for you safely.