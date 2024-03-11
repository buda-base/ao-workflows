  #!/usr/bin/env bash
  # Set up docker compose
  # Copy secret files locally for assumption into secrets.
  # DO NOT ADD THESE FILES TO SOURCE CONTROL (they're in .gitignore, but still)

  mkdir  -p .secrets || exit 1
  cp -v ~/.config/bdrc/docker/* .secrets || exit 1
  ./extract-section.pl ~/.aws/credentials default  > .secrets/aws-credentials || exit 1


