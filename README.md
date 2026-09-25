This is the source code to my site https://parth-shettiwar.github.io/. Template from Jon Barron.

## Local preview

This is a static HTML/CSS site, with no build step or package installation.
Open `index.html` in a browser, or run from the repository root:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Then visit http://127.0.0.1:8000.

## Checks

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

Check the page at desktop and mobile widths when changing the layout.
The tests cover local assets, navigation, markup, accessibility basics, and résumé content.

## Content

Edit `index.html` for the introduction, experience, and projects; edit `stylesheet.css`
for styling. The image-and-text project layout and existing project assets are retained.

The current refresh uses the supplied résumé text. The existing `data2/Parth_CV.pdf`
has not been replaced, and its link is explicitly labeled “Earlier CV (PDF).”
Replace it with the latest PDF before relabeling it as the current résumé.
