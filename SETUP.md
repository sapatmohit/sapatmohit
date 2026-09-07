# SYS/78 — setup

A branching text adventure as a GitHub profile. Five rooms, four routes, two
endings written (two left for you), a live vitals panel that a robot refreshes
every six hours, and a wall visitors can carve their name into with one click.

---

## 1. Make the repo

Create a **public** repo named *exactly* your GitHub username. That's what makes
it a profile repo. Drop these files in at the root and push to `main`.

## 2. Replace the placeholders

```bash
grep -rl 'YOUR_' . | xargs sed -i 's/YOUR_USERNAME/yourhandle/g'
```

Then do the rest by hand, since they're prose and deserve better than sed:

| placeholder | where | what it wants |
|---|---|---|
| `YOUR_USERNAME` | everywhere | your GitHub handle |
| `YOUR_HANDLE` | `rooms/comms.md` | your socials |
| `YOUR_CITY`, `YOUR_THING`, `YOUR_COMPANY` | `rooms/logs.md` | entry 088 |
| `project-alpha/beta/gamma` | `rooms/vault.md` | three real repos |
| the whole Armory table | `rooms/armory.md` | your actual tools, honestly rated |
| `you@example.com` | `rooms/comms.md` | your email |

The writing is doing most of the work here, so rewrite the prose in your own
voice. Keep the split: **the machine speaks in caps, humans speak in
lowercase.** That contrast is the whole visual grammar.

## 3. Turn on write access for Actions

**Settings → Actions → General → Workflow permissions → Read and write
permissions.** Both workflows commit to the repo; neither works without this.
Also confirm **Settings → General → Features → Issues** is checked, or the
Wall's button opens nothing.

## 4. Prime the vitals panel

```bash
python3 scripts/status.py && git add -A && git commit -m "vitals" && git push
```

After that, `.github/workflows/vitals.yml` handles it on a 6-hour cron. It
reads real numbers out of your git history — last commit, total commits, repo
age — and the core temperature genuinely drops if you stop committing for a
week. The panel telling a visitor the station has gone cold is more interesting
than a panel that always says everything's fine, so leave that behaviour in.

## 5. Test the Wall

Click the carve button in `rooms/wall.md` yourself. An issue opens with a
pre-filled title, the Action strips the title down to letters and numbers,
prepends it to the wall, commits, and closes the issue with a link. Takes about
a minute.

The sanitizer in `scripts/carve.py` is the security boundary — issue titles are
untrusted input from anyone on the internet. It allows `A-Z a-z 0-9 . _ -` and
spaces, caps at 24 characters, and the workflow passes the title through an env
var rather than shell interpolation. Don't loosen either of those.

---

## Things that will confuse you later

**The boot animation doesn't replay.** It's a one-shot CSS animation, so it
plays on page load and then the cursor blinks forever. If you edit `boot.svg`
and GitHub shows the old one, it's the camo image cache — bump the reference to
`assets/boot.svg?v=2`.

**Scheduled workflows get switched off after 60 days** on repos with no human
activity. Bot commits don't reliably count. If the vitals go stale, hit **Run
workflow** on the Actions tab to wake it up.

**Fonts.** GitHub proxies your SVG through camo, which won't fetch a webfont, so
the SVGs use the system monospace stack. That's why the terminal look comes from
letter-spacing, bloom, and scanlines rather than a pixel font — a real pixel
typeface would need to be embedded as base64 or converted to paths.

**Relative links** between rooms work fine in the rendered README. Keep the
`rooms/` structure or fix every link.

## Two endings are missing

`rooms/core.md` and `rooms/gameover.md` are endings 1 and 2. The README promises
four and says one of them is a lie. That's a deliberate hook — write ending 3
and 4 yourself, hide the entrance somewhere unmarked, and don't link it from the
Lobby. The best one is the one nobody has found yet.
