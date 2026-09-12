# Shengling Shi — academic website

A complete static academic website for GitHub Pages, migrated from the Shi Group Google Site. It includes About, Research, Publications, Team, Teaching, and Join us pages; responsive layouts; and research videos.

## Preview the finished website

Open `dist/index.html` in a browser after extracting this package. The separate `Shengling-Shi-Website-Preview.html` is a self-contained preview of all six pages, including the media, and can be opened directly.

## Publish on GitHub Pages

1. Create a repository named `YOUR-USERNAME.github.io` for your main academic website. A repository with another name also works; links are relative, so the site supports project subpaths.
2. Upload the contents of this project to its `main` branch. Include `.github/workflows/pages.yml`, `assets`, `content`, `build.py`, and `validate.py`. The generated `dist` folder does not need to be committed.
3. In the repository, open **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
4. Open **Actions → Publish academic website → Run workflow**. Future commits to `main` automatically rebuild and publish the website.
5. GitHub shows the live address under **Settings → Pages** after deployment completes.

If your repository uses a branch other than `main`, update the branch name in `.github/workflows/pages.yml`. If you already have a website at your intended repository, review the new version before replacing it.

GitHub's instructions: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Update content

Most updates require editing only the two JSON files. You can edit them directly on GitHub using its pencil button and commit the changes.

| What to change | Where |
| --- | --- |
| Biography, email, profile links | `content/site.json` |
| Research descriptions and figures | `research` in `content/site.json` |
| News | `news` in `content/site.json`, newest first |
| Team members and alumni | `members` and `alumni` in `content/site.json` |
| Courses and positions | `teaching` and `opportunities` in `content/site.json` |
| Publications | `content/publications.json` |
| Videos | `videos` in `content/site.json` and files in `assets/videos/` |
| Typography, colors, spacing | `assets/style.css` |
| Page layout | `build.py` |

All text content is rendered into ordinary HTML. Visitors can read every page without JavaScript; JavaScript adds the mobile menu and optional externally hosted video players. There are no analytics, external fonts, package dependencies, or third-party scripts. External embeds, if configured, load only after the viewer presses play.

### Add a publication

Add an entry to `content/publications.json`. Keep commas between entries and use double quotes. The page groups papers by type, sorts each type by year, and highlights S. Shi in the author list.

```json
{
  "title": "Your paper title",
  "authors": "S. Shi, A. Collaborator, and B. Collaborator",
  "citation": "Journal or conference, 2026.",
  "year": 2026,
  "topic": "Learning-Based Control",
  "kind": "Journal Papers",
  "links": [{"label": "arXiv", "url": "https://arxiv.org/abs/YOUR-PAPER-ID"}]
}
```

Supported `kind` values: `Journal Papers`, `Conference Proceedings`, and `Submitted Papers`. Submitted papers appear under “Preprints.” The homepage currently highlights the first three publication entries.

### Add or replace a video

For a native player, put an H.264 MP4 in `assets/videos/` and a poster image in `assets/images/`, then add an entry:

```json
{
  "title": "Your research demo",
  "description": "A short description of what the viewer is seeing.",
  "type": "mp4",
  "src": "assets/videos/demo.mp4",
  "poster": "assets/images/demo.jpg"
}
```

Native videos support controls, fullscreen, inline mobile playback, and optional captions. They do not autoplay, and `preload="none"` avoids downloading them until needed. Use `captions` to add WebVTT tracks:

```json
"captions": [{"src": "assets/videos/demo-en.vtt", "language": "en", "label": "English"}]
```

For a longer video, use YouTube or Google Drive instead:

```json
{
  "title": "Your demo",
  "description": "Description of the demonstration.",
  "type": "youtube",
  "id": "YOUR-YOUTUBE-VIDEO-ID",
  "poster": "assets/images/demo.jpg"
}
```

For Drive, use `"type": "drive"` and the file ID from its sharing URL. Its sharing settings must allow visitors to view it. Research currently displays the first two videos; the Team page displays videos referenced by `bachelor_projects[].video_index`. To show further research demos, change the `SITE['videos'][:2]` selection in `build.py`.

## Build locally

Python 3.10 or newer is sufficient; there is nothing to install.

```bash
python3 build.py
python3 validate.py
```

Then open `dist/index.html`. All normal page links and local media work from the filesystem. Optionally serve `dist` with any static web server.

## Content and review notes

- Content was migrated from https://sites.google.com/view/shenglingshi/about and its Research, Publication, Team, Teaching, and Open Position pages on 12 September 2026.
- The original portrait and research figures were reused. The three videos came from the original website and were optimized for web delivery. Keep your original recordings separately for archival quality.
- Final publication details for the certainty-equivalence MPC, state-action CBF, suboptimality analysis, and data-informativity papers were updated using the TU Delft Research Portal: https://research.tudelft.nl/en/persons/s-shi-2/ . Other bibliographic details retain the source site's records.
- Check current member affiliations, preprint status, and openings before launch. The supplied site stated that there were no open PhD or postdoctoral positions; this has been retained. News dates reflect the source site.
- The source site listed the same five names for both 2026 bachelor groups. Both projects and their videos are retained, but the duplicated rosters were omitted pending clarification.
- Only Shengling's portrait is used; several student image URLs were unavailable during migration. No substitute portraits were generated.
- Your GitHub username and live URL have not been assumed. No custom domain or canonical URL has been hard-coded.
- The site has been built and checked for local file and anchor integrity. GitHub publication requires a connected account and a successful Pages deployment. Browser playback and responsive visual QA have not been performed in this environment.

The content and supplied research media remain the property of their respective owners. No blanket reuse license is applied to the research assets.
