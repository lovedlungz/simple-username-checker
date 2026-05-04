#!/usr/bin/env python3
"""
Username Tracker GUI — double-click to run, no installs needed.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import urllib.request
import urllib.error
import threading
import webbrowser
import json

PLATFORMS = [
    {"name": "Twitter / X",     "cat": "social",       "url": "https://x.com/{u}"},
    {"name": "Instagram",       "cat": "social",       "url": "https://instagram.com/{u}"},
    {"name": "TikTok",          "cat": "social",       "url": "https://tiktok.com/@{u}"},
    {"name": "Facebook",        "cat": "social",       "url": "https://facebook.com/{u}"},
    {"name": "Threads",         "cat": "social",       "url": "https://threads.net/@{u}"},
    {"name": "Bluesky",         "cat": "social",       "url": "https://bsky.app/profile/{u}.bsky.social"},
    {"name": "Mastodon",        "cat": "social",       "url": "https://mastodon.social/@{u}"},
    {"name": "Snapchat",        "cat": "social",       "url": "https://snapchat.com/add/{u}"},
    {"name": "Pinterest",       "cat": "social",       "url": "https://pinterest.com/{u}"},
    {"name": "GitHub",          "cat": "dev",          "url": "https://github.com/{u}"},
    {"name": "GitLab",          "cat": "dev",          "url": "https://gitlab.com/{u}"},
    {"name": "npm",             "cat": "dev",          "url": "https://npmjs.com/~{u}"},
    {"name": "CodePen",         "cat": "dev",          "url": "https://codepen.io/{u}"},
    {"name": "Replit",          "cat": "dev",          "url": "https://replit.com/@{u}"},
    {"name": "Hugging Face",    "cat": "dev",          "url": "https://huggingface.co/{u}"},
    {"name": "Stack Overflow",  "cat": "dev",          "url": "https://stackoverflow.com/users/{u}"},
    {"name": "Dev.to",          "cat": "dev",          "url": "https://dev.to/{u}"},
    {"name": "Hashnode",        "cat": "dev",          "url": "https://hashnode.com/@{u}"},
    {"name": "YouTube",         "cat": "video",        "url": "https://youtube.com/@{u}"},
    {"name": "Twitch",          "cat": "video",        "url": "https://twitch.tv/{u}"},
    {"name": "Rumble",          "cat": "video",        "url": "https://rumble.com/user/{u}"},
    {"name": "Kick",            "cat": "video",        "url": "https://kick.com/{u}"},
    {"name": "LinkedIn",        "cat": "professional", "url": "https://linkedin.com/in/{u}"},
    {"name": "AngelList",       "cat": "professional", "url": "https://angel.co/u/{u}"},
    {"name": "Product Hunt",    "cat": "professional", "url": "https://producthunt.com/@{u}"},
    {"name": "Behance",         "cat": "creative",     "url": "https://behance.net/{u}"},
    {"name": "Dribbble",        "cat": "creative",     "url": "https://dribbble.com/{u}"},
    {"name": "ArtStation",      "cat": "creative",     "url": "https://artstation.com/{u}"},
    {"name": "Flickr",          "cat": "creative",     "url": "https://flickr.com/people/{u}"},
    {"name": "SoundCloud",      "cat": "music",        "url": "https://soundcloud.com/{u}"},
    {"name": "Spotify",         "cat": "music",        "url": "https://open.spotify.com/user/{u}"},
    {"name": "Bandcamp",        "cat": "music",        "url": "https://bandcamp.com/{u}"},
    {"name": "Last.fm",         "cat": "music",        "url": "https://last.fm/user/{u}"},
    {"name": "Medium",          "cat": "writing",      "url": "https://medium.com/@{u}"},
    {"name": "Substack",        "cat": "writing",      "url": "https://{u}.substack.com"},
    {"name": "Tumblr",          "cat": "writing",      "url": "https://{u}.tumblr.com"},
    {"name": "Reddit",          "cat": "writing",      "url": "https://reddit.com/u/{u}"},
    {"name": "Keybase",         "cat": "other",        "url": "https://keybase.io/{u}"},
    {"name": "Patreon",         "cat": "other",        "url": "https://patreon.com/{u}"},
    {"name": "Ko-fi",           "cat": "other",        "url": "https://ko-fi.com/{u}"},
    {"name": "Buy Me a Coffee", "cat": "other",        "url": "https://buymeacoffee.com/{u}"},
    {"name": "Linktree",        "cat": "other",        "url": "https://linktr.ee/{u}"},
    {"name": "Gravatar",        "cat": "other",        "url": "https://gravatar.com/{u}"},
]

CATEGORIES = ["All"] + sorted(set(p["cat"] for p in PLATFORMS))

CAT_COLORS = {
    "social":       "#a78bfa",
    "dev":          "#60a5fa",
    "video":        "#f87171",
    "professional": "#34d399",
    "creative":     "#fbbf24",
    "music":        "#f472b6",
    "writing":      "#94a3b8",
    "other":        "#9ca3af",
}

BG        = "#0f1117"
SURFACE   = "#1a1d27"
SURFACE2  = "#22263a"
ACCENT    = "#7c6af7"
ACCENT2   = "#a78bfa"
TEXT      = "#e2e8f0"
TEXT_DIM  = "#64748b"
BORDER    = "#2d3250"
GREEN     = "#4ade80"
RED       = "#f87171"
YELLOW    = "#facc15"


def build_url(platform, username):
    return platform["url"].replace("{u}", username)


def check_url(url, timeout=6):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        return e.code == 200
    except Exception:
        return None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Username Tracker")
        self.geometry("860x640")
        self.minsize(700, 500)
        self.configure(bg=BG)
        self._results = []
        self._check_var = tk.BooleanVar(value=False)
        self._cat_var = tk.StringVar(value="All")
        self._checking = False
        self._build_ui()

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG, pady=20)
        hdr.pack(fill="x", padx=28)

        tk.Label(hdr, text="Username Tracker", font=("Helvetica", 22, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(hdr, text="Find profile links across 43+ platforms",
                 font=("Helvetica", 11), bg=BG, fg=TEXT_DIM).pack(anchor="w")

        tk.Label(hdr, text="made by h4jv on discord",
                 font=("Helvetica", 9), bg=BG, fg=ACCENT2).pack(anchor="w", pady=(4, 0))

        # ── Search bar ──────────────────────────────────────────
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=28, pady=(0, 12))

        self._entry = tk.Entry(row, font=("Helvetica", 14), bg=SURFACE,
                               fg=TEXT, insertbackground=TEXT,
                               relief="flat", bd=0,
                               highlightthickness=1,
                               highlightbackground=BORDER,
                               highlightcolor=ACCENT)
        self._entry.pack(side="left", fill="x", expand=True, ipady=10, ipadx=10)
        self._entry.bind("<Return>", lambda e: self._run())
        self._entry.insert(0, "")
        self._entry.focus()

        self._btn = tk.Button(row, text="Search", font=("Helvetica", 13, "bold"),
                              bg=ACCENT, fg="white", relief="flat",
                              activebackground=ACCENT2, activeforeground="white",
                              cursor="hand2", padx=22, pady=10,
                              command=self._run)
        self._btn.pack(side="left", padx=(8, 0))

        # ── Filter row ──────────────────────────────────────────
        frow = tk.Frame(self, bg=BG)
        frow.pack(fill="x", padx=28, pady=(0, 6))

        tk.Label(frow, text="Category:", font=("Helvetica", 11),
                 bg=BG, fg=TEXT_DIM).pack(side="left", padx=(0, 8))

        self._cat_btns = {}
        for cat in CATEGORIES:
            color = CAT_COLORS.get(cat.lower(), ACCENT) if cat != "All" else ACCENT
            b = tk.Button(frow, text=cat.capitalize(),
                          font=("Helvetica", 10),
                          bg=SURFACE2, fg=TEXT_DIM,
                          relief="flat", padx=10, pady=4,
                          cursor="hand2",
                          command=lambda c=cat: self._set_cat(c))
            b.pack(side="left", padx=2)
            self._cat_btns[cat] = b
        self._set_cat("All")

        # ── Check toggle ────────────────────────────────────────
        chk_row = tk.Frame(self, bg=BG)
        chk_row.pack(fill="x", padx=28, pady=(0, 10))

        self._chk = tk.Checkbutton(chk_row, text="Live-check URLs (slower)",
                                   variable=self._check_var,
                                   font=("Helvetica", 11),
                                   bg=BG, fg=TEXT_DIM,
                                   selectcolor=SURFACE2,
                                   activebackground=BG,
                                   activeforeground=TEXT)
        self._chk.pack(side="left")

        self._export_btn = tk.Button(chk_row, text="Export JSON",
                                     font=("Helvetica", 10),
                                     bg=SURFACE2, fg=TEXT_DIM,
                                     relief="flat", padx=10, pady=4,
                                     cursor="hand2",
                                     command=self._export,
                                     state="disabled")
        self._export_btn.pack(side="right")

        # ── Status bar ──────────────────────────────────────────
        self._status_var = tk.StringVar(value="Enter a username and press Search")
        tk.Label(self, textvariable=self._status_var,
                 font=("Helvetica", 10), bg=BG, fg=TEXT_DIM,
                 anchor="w").pack(fill="x", padx=28, pady=(0, 6))

        # ── Progress bar ────────────────────────────────────────
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor=SURFACE, background=ACCENT,
                        bordercolor=BG, lightcolor=ACCENT, darkcolor=ACCENT)
        self._progress = ttk.Progressbar(self, style="Custom.Horizontal.TProgressbar",
                                         mode="determinate", length=200)
        self._progress.pack(fill="x", padx=28, pady=(0, 8))
        self._progress.pack_forget()

        # ── Results table ───────────────────────────────────────
        tframe = tk.Frame(self, bg=BG)
        tframe.pack(fill="both", expand=True, padx=28, pady=(0, 16))

        cols = ("platform", "category", "url", "status")
        self._tree = ttk.Treeview(tframe, columns=cols, show="headings",
                                   selectmode="browse")

        style.configure("Treeview",
                         background=SURFACE,
                         foreground=TEXT,
                         rowheight=32,
                         fieldbackground=SURFACE,
                         bordercolor=BORDER,
                         borderwidth=0)
        style.configure("Treeview.Heading",
                         background=SURFACE2,
                         foreground=TEXT_DIM,
                         relief="flat",
                         font=("Helvetica", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        self._tree.heading("platform", text="Platform")
        self._tree.heading("category", text="Category")
        self._tree.heading("url",      text="Profile URL")
        self._tree.heading("status",   text="Status")
        self._tree.column("platform", width=160, anchor="w")
        self._tree.column("category", width=110, anchor="w")
        self._tree.column("url",      width=400, anchor="w")
        self._tree.column("status",   width=90,  anchor="center")

        vsb = ttk.Scrollbar(tframe, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)

        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._tree.tag_configure("found",    foreground=GREEN)
        self._tree.tag_configure("notfound", foreground=RED)
        self._tree.tag_configure("unknown",  foreground=YELLOW)
        self._tree.tag_configure("normal",   foreground=TEXT)
        self._tree.tag_configure("odd",      background=SURFACE)
        self._tree.tag_configure("even",     background="#1e2130")

        self._tree.bind("<Double-1>", self._open_link)
        self._tree.bind("<Return>",   self._open_link)

        tip = tk.Label(self, text="Double-click a row to open the profile in your browser",
                       font=("Helvetica", 9), bg=BG, fg=TEXT_DIM)
        tip.pack(pady=(0, 8))

    def _set_cat(self, cat):
        self._cat_var.set(cat)
        for c, b in self._cat_btns.items():
            if c == cat:
                color = CAT_COLORS.get(c.lower(), ACCENT) if c != "All" else ACCENT
                b.configure(bg=color, fg="white")
            else:
                b.configure(bg=SURFACE2, fg=TEXT_DIM)
        if self._results:
            self._populate(self._results)

    def _run(self):
        if self._checking:
            return
        username = self._entry.get().strip().lstrip("@")
        if not username:
            messagebox.showwarning("No username", "Please enter a username first.")
            return

        cat = self._cat_var.get()
        filtered = [p for p in PLATFORMS if cat == "All" or p["cat"].lower() == cat.lower()]
        results = [{"name": p["name"], "cat": p["cat"],
                    "url": build_url(p, username), "status": None} for p in filtered]

        if self._check_var.get():
            self._checking = True
            self._btn.configure(state="disabled", text="Checking…")
            self._progress.configure(maximum=len(results), value=0)
            self._progress.pack(fill="x", padx=28, pady=(0, 8))
            self._status_var.set(f"Checking {len(results)} platforms…")
            self._tree.delete(*self._tree.get_children())
            threading.Thread(target=self._check_all,
                             args=(results,), daemon=True).start()
        else:
            self._results = results
            self._populate(results)
            self._status_var.set(f"{len(results)} links generated for @{username}")
            self._export_btn.configure(state="normal")

    def _check_all(self, results):
        import concurrent.futures
        done = 0

        def worker(r):
            exists = check_url(r["url"])
            r["status"] = exists
            return r

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            futures = {ex.submit(worker, r): r for r in results}
            for f in concurrent.futures.as_completed(futures):
                f.result()
                done += 1
                self.after(0, self._tick, done, len(results))

        self.after(0, self._done_checking, results)

    def _tick(self, done, total):
        self._progress["value"] = done
        self._status_var.set(f"Checking… {done}/{total}")
        self._populate(self._results if self._results else [])

    def _done_checking(self, results):
        self._results = results
        self._checking = False
        self._btn.configure(state="normal", text="Search")
        self._progress.pack_forget()
        found = sum(1 for r in results if r["status"] is True)
        self._status_var.set(
            f"{len(results)} platforms checked — {found} found, {len(results)-found} not found/unknown"
        )
        self._populate(results)
        self._export_btn.configure(state="normal")

    def _populate(self, results):
        cat = self._cat_var.get()
        filtered = [r for r in results
                    if cat == "All" or r["cat"].lower() == cat.lower()]
        self._tree.delete(*self._tree.get_children())
        for i, r in enumerate(filtered):
            s = r.get("status")
            if s is True:
                status_txt = "✓ Found"
                tag = "found"
            elif s is False:
                status_txt = "✗ Not found"
                tag = "notfound"
            elif s is None and self._check_var.get() and self._checking:
                status_txt = "…"
                tag = "unknown"
            else:
                status_txt = "—"
                tag = "normal"
            row_tag = "odd" if i % 2 == 0 else "even"
            self._tree.insert("", "end",
                               values=(r["name"], r["cat"].capitalize(), r["url"], status_txt),
                               tags=(tag, row_tag))

    def _open_link(self, event=None):
        sel = self._tree.selection()
        if not sel:
            return
        url = self._tree.item(sel[0])["values"][2]
        if url:
            webbrowser.open(url)

    def _export(self):
        if not self._results:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="username_tracker_results.json",
        )
        if not path:
            return
        data = [{"platform": r["name"], "category": r["cat"],
                 "url": r["url"], "status": r.get("status")} for r in self._results]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Exported", f"Results saved to:\n{path}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
