#!/bin/bash
# Optional step of deploy/run.sh: deploy small PRIVATE apps that live in their
# own private repos but have no deploy secret of their own yet.
#
# For each app: sync /var/www/<app> from its private repo with a VPS-local,
# read-only Deploy Key, then run that repo's own deploy/run.sh. The app's
# config (secret) comes from this repo's Actions secrets via the environment.
#
# This repo is PUBLIC and so are its Actions logs: never print a secret here,
# never `set -x`. Only the PUBLIC half of a deploy key is ever printed. The
# private app's own deploy output (and git's) goes to a root-only log on the
# VPS, /var/log/private-apps/<app>.log; the Actions log gets one status line.
# The app's deploy runs with `env -i`: only PATH, HOME and the variables that
# app needs, never the other secrets of this deploy (e.g. HABITS_GITHUB_TOKEN).
#
# deploy/run.sh calls this as a separate process and ignores its exit code, so
# a failure here never breaks the main site deploy.
set -uo pipefail

LOG_DIR=/var/log/private-apps

# deploy_private_app <name> <owner/repo> [VAR=value ...]  (vars passed to its deploy only)
deploy_private_app() {
    local name="$1" repo="$2"; shift 2
    local dir="/var/www/$name"
    local key="/root/.ssh/${name}_deploy_ed25519"
    local log="$LOG_DIR/$name.log"

    echo "── private app: $name ──"
    mkdir -p "$LOG_DIR" && chmod 700 "$LOG_DIR"
    ( umask 077; touch "$log" ) && chmod 600 "$log"
    echo "===== $(date -u +%FT%TZ) deploy =====" >> "$log"

    # Read-only Deploy Key, generated on the VPS once. Its private half never
    # leaves the VPS; the public half must be added to the repo as a
    # read-only Deploy Key.
    if [ ! -f "$key" ]; then
        mkdir -p /root/.ssh && chmod 700 /root/.ssh
        ssh-keygen -q -t ed25519 -N "" -C "vps-${name}-readonly" -f "$key" >> "$log" 2>&1 || return 1
        echo "🔑 Created read-only deploy key on the VPS"
    fi
    ssh-keygen -F github.com >/dev/null 2>&1 || ssh-keyscan -H github.com >> /root/.ssh/known_hosts 2>/dev/null

    local gitssh="ssh -i $key -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15"
    local ok=1
    if [ -d "$dir/.git" ]; then
        { GIT_SSH_COMMAND="$gitssh" git -C "$dir" fetch -q origin main && git -C "$dir" reset -q --hard origin/main; } >> "$log" 2>&1 || ok=0
    else
        GIT_SSH_COMMAND="$gitssh" git clone -q "git@github.com:${repo}.git" "$dir" >> "$log" 2>&1 || ok=0
    fi
    if [ "$ok" != 1 ]; then
        echo "⚠️  $name: cannot pull $repo (details in $log). Add this PUBLIC key to it as a read-only Deploy Key:"
        cat "${key}.pub"
        return 1
    fi

    if (cd "$dir" && env -i PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" HOME=/root "$@" ./deploy/run.sh) >> "$log" 2>&1; then
        echo "✅ $name deployed at $(git -C "$dir" rev-parse --short HEAD) (log: $log)"
    else
        echo "⚠️  $name deploy failed at $(git -C "$dir" rev-parse --short HEAD) (details in $log on the VPS)"
        return 1
    fi
}

status=0

# Resume review (private, token-gated). REVIEW_TOKEN comes from this repo's
# Actions secret; empty = not configured, skip.
if [ -n "${REVIEW_TOKEN:-}" ]; then
    deploy_private_app resume-review prabhanshu11/resume-review "REVIEW_TOKEN=$REVIEW_TOKEN" || status=1
else
    echo "── private app: resume-review skipped (no REVIEW_TOKEN) ──"
fi

exit $status
