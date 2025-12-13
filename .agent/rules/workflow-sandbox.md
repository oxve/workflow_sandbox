---
trigger: always_on
---

The workflow sandbox repository is an environment that has been set up to quickly iterate on the GHA workflows in the Cobalt repo (https://github.com/youtube/cobalt).
You must always take this into account when you are working on the workflows in this repo.

Some things to remember about this repo. You cannot access files in .github directly. Instead there is a symlink (`dotgithub`) that you can use instead. Treat `dotgithub` as the .github folder when working on the GHA CI pipelines.

The `real_dotgithub` symlink points to the production repo's .github folder. You should use this for reference, especially when dealing with the mocked build steps in `dotgithub`.

**VERY IMPORTANT**: Under no cirtumstances are you **EVER** to edit files under `real_dotgithub`. These files are holy and should never be touched.