# Legacia RO Wiki

Player guide for Legacia RO (pre-renewal): rates, Autohunt, Weapon Mastery, daily content, bosses, WoE, VIP, events and every Prontera NPC.

The whole wiki is one page, `index.html`, with no build step. Edit it and push to `main`.

## Publishing to the Legacia website (automatic)

`.github/workflows/deploy.yml` uploads `index.html` to the web host over FTP on every push to `main`
(and by hand from the Actions tab, "Deploy to web host" > "Run workflow").

Set it up once in Settings > Secrets and variables > Actions:

- Secrets: `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD` (the same details WinSCP uses).
- Variable: `FTP_DIR`, the folder to upload into, e.g. `domains/<your domain>/public_html/wiki`.
  The wiki is then at `https://<your domain>/wiki/`.
- Optional variable: `FTP_PROTOCOL` = `ftps` if your host needs it (default `ftp`).

Until these are set, the workflow skips the upload with a warning.

## Publishing with GitHub Pages (optional)

Settings > Pages > Build and deployment > Source: **Deploy from a branch**, Branch: **main**, folder **/ (root)**.
The site is then at `https://mjonrest.github.io/legacia-wiki/`.

## Sources

Content comes from the server repository (`mjonrest/legacia-RO`): `npc/miracle/*`, `npc/custom/*`, `conf/battle/*.conf` and the db files.
Update the page when those systems change (rates, autohunt, WoE schedule, VIP, events).
