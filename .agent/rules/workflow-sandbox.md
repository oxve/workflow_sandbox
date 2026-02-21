---
trigger: always_on
---

## The workflow_sandbox repo

The workflow sandbox repository is an experimentation environment that has been set up to quickly iterate on the GHA workflows in the Cobalt repo (https://github.com/youtube/cobalt).

Some things to remember about this repo. You cannot access files in .github directly. Instead there is a symlink (`dotgithub`) that you can use instead. Treat `dotgithub` as the .github folder when working on the GHA CI pipelines.

The `real_dotgithub` symlink points to the production repo's .github folder. You should use this for reference, especially when dealing with the mocked build steps in `dotgithub`.

**VERY IMPORTANT**: Under no cirtumstances are you **EVER** to edit files under `real_dotgithub`. These files are holy and should never be touched.

## Common Instructions

### Testing changes

Always test your changes using local simulation first. Once local testing has verified that the code is working as intended you *MUST* create a pull request and analyze the results of the workflow runs.
