Bake supports the Compose file format
to parse a Compose file and translate each service to a target.

[code example]yaml
# compose.yaml
services:
 addon:
 image: ct-addon:bar
 build:
 context: .
 dockerfile: ./Dockerfile
 args:
 CT_ECR: foo
 CT_TAG: bar
 x-bake:
 tags:
 - ct-addon:foo
 - ct-addon:alp
 platforms:
 - linux/amd64
 - linux/arm64
 cache-from:
 - user/app:cache
 - type=local,src=path/to/cache
 cache-to:
 - type=local,dest=path/to/cache
 pull: true

 aws:
 image: ct-fake-aws:bar
 build:
 dockerfile: ./aws.Dockerfile
 args:
 CT_ECR: foo
 CT_TAG: bar
 x-bake:
 secret:
 - id=mysecret,src=./secret
 - id=mysecret2,src=./secret2
 platforms: linux/arm64
 output: type=docker
 no-cache: true
[code example]console
$ docker buildx bake --print
[code example]json
{
 "group": {
 "default": {
 "targets": ["addon", "aws"]
 }
 },
 "target": {
 "addon": {
 "context": ".",
 "dockerfile": "./Dockerfile",
 "args": {
 "CT_ECR": "foo",
 "CT_TAG": "bar"
 },
 "tags": ["ct-addon:foo", "ct-addon:alp"],
 "cache-from": [
 {
 "ref": "user/app:cache",
 "type": "registry"
 },
 {
 "src": "path/to/cache",
 "type": "local"
 }
 ],
 "cache-to": [
 {
 "dest": "path/to/cache",
 "type": "local"
 }
 ],
 "platforms": ["linux/amd64", "linux/arm64"],
 "pull": true
 },
 "aws": {
 "context": ".",
 "dockerfile": "./aws.Dockerfile",
 "args": {
 "CT_ECR": "foo",
 "CT_TAG": "bar"
 },
 "tags": ["ct-fake-aws:bar"],
 "secret": [
 {
 "id": "mysecret",
 "src": "./secret"
 },
 {
 "id": "mysecret2",
 "src": "./secret2"
 }
 ],
 "platforms": ["linux/arm64"],
 "output": [
 {
 "type": "docker"
 }
 ],
 "no-cache": true
 }
 }
}
 

Complete list of valid fields for x-bake :

- cache-from 
- cache-to 
- contexts 
- no-cache 
- no-cache-filter 
- output 
- platforms 
- pull 
- secret 
- ssh 
- tags