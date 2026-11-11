#!/bin/bash
# Optional step of deploy/run.sh: deploy small PRIVATE apps that live in their
# own private repos but have no deploy secret of their own yet.
#
# For each app: sync /var/www/<app> from its private repo with a VPS-local,
# read-only Deploy Key, then run that repo's own deploy/run.sh. The app's
# config (secret) comes from this repo's Actions secrets via the environment.
#
# This repo is PUBLIC and so are its Actions logs: never print a secret here,
# never `set -x`. Only the PUBLIC half of a deploy key is ever printed.
#
# deploy/run.sh calls this as a separate process and ignores its exit code, so
# a failure here never breaks the main site deploy.
set -uo pipefail

deploy_private_app() {
    local name="$1" repo="$2"
    local dir="/var/www/$name"
    local key="/root/.ssh/${name}_deploy_ed25519"

    echo "── private app: $name ──"

    # Read-only Deploy Key, generated on the VPS once. Its private half never
    # leaves the VPS; the public half must be added to the repo as a
    # read-only Deploy Key.
    if [ ! -f "$key" ]; then
        mkdir -p /root/.ssh && chmod 700 /root/.ssh
        ssh-keygen -q -t ed25519 -N "" -C "vps-${name}-readonly" -f "$key" || return 1
        echo "🔑 Created $key"
    fi
    ssh-keygen -F github.com >/dev/null 2>&1 || ssh-keyscan -H github.com >> /root/.ssh/known_hosts 2>/dev/null

    export GIT_SSH_COMMAND="ssh -i $key -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15"
    local ok=1
    if [ -d "$dir/.git" ]; then
        git -C "$dir" fetch -q origin main && git -C "$dir" reset -q --hard origin/main || ok=0
    else
        git clone -q "git@github.com:${repo}.git" "$dir" || ok=0
    fi
    unset GIT_SSH_COMMAND
    if [ "$ok" != 1 ]; then
        echo "⚠️  $name: cannot pull $repo. Add this PUBLIC key to it as a read-only Deploy Key:"
        cat "${key}.pub"
        return 1
    fi
    echo "📥 $name at $(git -C "$dir" rev-parse --short HEAD)"

    (cd "$dir" && ./deploy/run.sh)
}

status=0

# Resume review (private, token-gated). REVIEW_TOKEN comes from this repo's
# Actions secret; empty = not configured, skip.
if [ -n "${REVIEW_TOKEN:-}" ]; then
    export REVIEW_TOKEN
    deploy_private_app resume-review prabhanshu11/resume-review || status=1
else
    echo "── private app: resume-review skipped (no REVIEW_TOKEN) ──"
fi

exit $status
