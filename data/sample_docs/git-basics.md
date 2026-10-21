# Git 与协作

Git 是分布式版本控制，每个克隆都有完整历史。
工作区、暂存区、版本库是三个核心区域。
git add 把改动放进暂存区，git commit 把暂存区写成一次提交。
git diff 对比工作区和暂存区，git diff --cached 对比暂存区和版本库。
分支只是指向提交的可移动指针，创建分支几乎没有成本。
HEAD 指向当前分支的最新提交。
merge 保留两条分支的历史，产生一个合并提交。
rebase 把提交搬到新基底上，历史是一条直线但会改写提交号。
不要对已经推送的公共分支做 rebase，会影响其他人。
cherry-pick 把某个提交单独摘到当前分支。
reset --soft 只移动 HEAD，不改工作区和暂存区。
reset --hard 会丢弃工作区和暂存区的改动，慎用。
revert 生成一个反向提交，安全地撤销已推送的内容。
stash 把未提交的改动暂存起来，用于切换任务。
git bisect 用二分查找定位引入 bug 的提交。
远程分支是只读的本地副本，需要 fetch 更新。
pull 等于 fetch 加 merge，pull --rebase 等于 fetch 加 rebase。
tag 用来标记版本，附注 tag 带作者和说明，比轻量 tag 信息更全。
.gitignore 只对未跟踪文件生效，已跟踪的文件要 git rm --cached。
冲突发生在同一文件的同一区域被两条分支修改时。
