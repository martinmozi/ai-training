#!/usr/bin/env bash
# PreToolUse (Read|Edit|Write): agent nemá čítať ani meniť súbory s tajomstvami.
path=$(jq -r '.tool_input.file_path // empty')
case "$(basename "$path")" in
  .env|.env.*|*.pem|*.key|id_rsa*|credentials*|secrets.*)
    case "$path" in *.example|*.sample|*.template) exit 0 ;; esac
    echo "Súbor $path môže obsahovať tajomstvá, nečítaj ho ani nemeň. Ak potrebuješ názvy premenných, použi .env.example." >&2
    exit 2
    ;;
esac
exit 0
