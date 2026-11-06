# Course sandbox

Build from this directory with `docker build --platform linux/amd64 -t IMAGE .`.
Push the image and record its registry digest in the experiment manifest. The
runner rejects mutable tags. `forge-image.yml` provides the same build in GitHub.

Node, Python, Electron, Xvfb, Git, ripgrep, and all app dependencies are available
before the trial starts. Task sandboxes deny network egress. Pi and model
credentials stay in the controller; Pi receives only the remote command tool.
The image contains dependencies, never solution source or held-out graders.

Each launch records its sandbox ID before waiting for readiness. The controller
collects the patch before stopping the sandbox and waits for a terminal state.
The 20-minute server-side lifetime bounds orphaned workers. A failed cleanup or
an uncertain launch requires reconciliation before another campaign can start.
