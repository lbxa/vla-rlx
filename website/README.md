# Thesis website

The website source and manuscript were restored from `gh-pages` at commit
`a80959a4923e075c30036377826545698081f2c6`. `main` is now the source for
[vla.lbxa.net](https://vla.lbxa.net/).

## Deployment

The GitHub Actions workflow in `.github/workflows/pages.yml` builds `website/`
and deploys automatically on pushes to `main`. Manual workflow runs also deploy
only when run against `main`. The `github-pages` environment allows deployments
only from `main`.

Keep website content and `public/files/thesis.pdf` on `main`. Use `dev` for work
in progress and merge ready changes into `main` to publish them.

The [research README](../README.md) and
[protocol and evidence record](../docs/reproduction-status.md) document the
research audit. Restoring the website does not resolve the audit's open questions.

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
