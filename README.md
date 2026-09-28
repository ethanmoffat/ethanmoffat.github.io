# ethanmoffat.github.io

Landing page for the eolib documentation sites, published at https://ethanmoffat.github.io/.

| Path | Site |
|---|---|
| `/eolib-cpp/` | [eolib-cpp](https://github.com/ethanmoffat/eolib-cpp) API reference, published by its Pages workflow |
| `/eolib-dotnet/` | [eolib-dotnet](https://github.com/ethanmoffat/eolib-dotnet) API reference, published by its Pages workflow |
| `/eolib-go/` | Redirects to [pkg.go.dev](https://pkg.go.dev/github.com/ethanmoffat/eolib-go/v3) |

GitHub Pages serves each project's site under its repository name, so only the landing page and the eolib-go redirect
live here. The Pages workflow deploys `site/` on every push to master, and every Monday.

The third-party libraries section is generated from the "Libraries" section of the
[eo-protocol README](https://github.com/cirras/eo-protocol#libraries) by `scripts/update-libraries.py`, which the
workflow runs before each deployment. Each library links to its docs: the URL in `libraries.json` if there is one,
otherwise the homepage of its GitHub repository. The generated section is committed too, so the page works without
running the script. To update and preview it locally:

```sh
python3 scripts/update-libraries.py
python3 -m http.server 8000 --directory site
```
