# Website source status

This checkout contains a research presentation describing 12 tasks and
30 trials per task. It does not match the seven-task, 20-trial page inspected at
[vla.lbxa.net](https://vla.lbxa.net/) on 4 September 2026. Its quantitative claims
and example reproduction commands have not been reconciled with the supplied
results or manuscript. Its relationship to the deployed source revision has not
been established. Locate the current page's source before editing or
deploying it as the thesis site.

The current repository documentation is in the [research README](../README.md).
The [protocol and evidence record](../docs/reproduction-status.md) documents the
5–5–10 trial split and the unresolved score discrepancy. The existing GitHub Pages
workflow builds this directory on pushes to `main`; this audit did not deploy it.

## Original starter instructions

```sh
bun create astro@latest -- --template basics
```

> 🧑‍🚀 **Seasoned astronaut?** Delete this file. Have fun!

## 🚀 Project Structure

Inside of your Astro project, you'll see the following folders and files:

```text
/
├── public/
│   └── favicon.svg
├── src
│   ├── assets
│   │   └── astro.svg
│   ├── components
│   │   └── Welcome.astro
│   ├── layouts
│   │   └── Layout.astro
│   └── pages
│       └── index.astro
└── package.json
```

To learn more about the folder structure of an Astro project, refer to [our guide on project structure](https://docs.astro.build/en/basics/project-structure/).

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `bun install`             | Installs dependencies                            |
| `bun dev`             | Starts local dev server at `localhost:4321`      |
| `bun build`           | Build your production site to `./dist/`          |
| `bun preview`         | Preview your build locally, before deploying     |
| `bun astro ...`       | Run CLI commands like `astro add`, `astro check` |
| `bun astro -- --help` | Get help using the Astro CLI                     |

## 👀 Want to learn more?

Feel free to check [our documentation](https://docs.astro.build) or jump into our [Discord server](https://astro.build/chat).
