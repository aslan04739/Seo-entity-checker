import os
import sys
import csv
import threading
import argparse
import json
import shutil
from urllib.parse import urlparse, urljoin
from pathlib import Path

# Vérification des dépendances
try:
    import requests
    from bs4 import BeautifulSoup
    from google.cloud import language_v1
except ImportError as e:
    print("ERREUR CRITIQUE : Bibliothèques manquantes.")
    print(f"Détail : {e}")
    print("Veuillez lancer : pip install google-cloud-language beautifulsoup4 requests customtkinter")
    sys.exit(1)

# --- Settings & Config ---
CONFIG_DIR = Path.home() / ".seo_crawler"
CONFIG_FILE = CONFIG_DIR / "config.json"
APP_DIR = Path(__file__).resolve().parent
CONFIG_DIR.mkdir(exist_ok=True)
MIN_SALIENCE = 0.001
DEBUG_DIR = CONFIG_DIR / "debug"
DEBUG_DIR.mkdir(exist_ok=True)

def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except:
            return {}
    return {}

def save_config(config):
    try:
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
    except:
        pass

CONFIG = load_config()


def resolve_default_creds_path():
    candidates = []

    configured = CONFIG.get("creds_path")
    if configured:
        candidates.append(Path(configured).expanduser())

    candidates.extend([
        APP_DIR / "credentials.json",
        CONFIG_DIR / "credentials.json",
        Path.cwd() / "credentials.json",
    ])

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return str(candidate)
    return None


def promote_to_canonical_creds(source_path: str):
    if not source_path:
        return None

    source = Path(source_path).expanduser()
    if not source.exists() or not source.is_file():
        return None

    canonical = CONFIG_DIR / "credentials.json"
    try:
        if source.resolve() != canonical.resolve():
            shutil.copy2(source, canonical)
        return str(canonical)
    except Exception:
        return str(source)

# --- LOGIC CLASS (Coeur du programme) ---
class SEOLogic:
    @staticmethod
    def normalize_url(url: str) -> str:
        parsed = urlparse(url)
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc
        path = parsed.path.replace('//', '/')
        return f"{scheme}://{netloc}{path}"

    @staticmethod
    def fetch_content(url):
        text, _html = SEOLogic.fetch_content_and_html(url)
        return text

    @staticmethod
    def fetch_content_and_html(url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9"
            }
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            if response.status_code != 200:
                return None, response.text if response.text else None
            
            soup = BeautifulSoup(response.text, "html.parser")
            # Nettoyage du bruit (scripts, styles, footer...)
            for tag in soup(["script", "style", "noscript", "iframe"]):
                tag.decompose()
            for div in soup.find_all("div", class_=["cookie", "banner", "gdpr"]):
                div.decompose()

            # Prefer visible content blocks to avoid nav-heavy pages
            title = soup.title.get_text(strip=True) if soup.title else ""
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag and meta_tag.get("content"):
                meta_desc = meta_tag.get("content").strip()
            headings = " ".join(h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"]))
            body_blocks = " ".join(
                el.get_text(" ", strip=True)
                for el in soup.find_all(["p", "li"])
            )

            text = " ".join([title, meta_desc, headings, body_blocks]).strip()
            text = " ".join(text.split())

            # Fallback: if aggressive cleanup removes most content, retry with minimal cleanup
            if len(text) < 200:
                soup_fallback = BeautifulSoup(response.text, "html.parser")
                for tag in soup_fallback(["script", "style", "noscript", "iframe"]):
                    tag.decompose()
                body = soup_fallback.body.get_text(separator=' ') if soup_fallback.body else soup_fallback.get_text(separator=' ')
                text = " ".join(body.split())

            return text[:10000], response.text # Limite pour réduire les coûts API
        except Exception:
            return None, None

    @staticmethod
    def analyze_entities(text_content, source_url, log_callback=None):
        if not text_content: return []
        try:
            client = language_v1.LanguageServiceClient()
            document = language_v1.Document(content=text_content, type_=language_v1.Document.Type.PLAIN_TEXT)
            response = client.analyze_entities(request={"document": document, "encoding_type": language_v1.EncodingType.UTF8})
            
            results = []
            if log_callback:
                log_callback(f"  → NLP returned {len(response.entities)} entities before filtering")
            for entity in response.entities:
                if entity.salience < MIN_SALIENCE:
                    continue
                results.append({
                    "source": source_url,
                    "name": entity.name,
                    "salience": round(entity.salience, 4),
                    "category": language_v1.Entity.Type(entity.type_).name
                })
            return results
        except Exception as e:
            msg = f"Google NLP Error on {source_url}: {e}"
            if log_callback:
                log_callback(msg)
            else:
                print(msg)
            return []

    @staticmethod
    def crawl(seed_url, max_pages, max_depth, log_callback=print):
        seed = SEOLogic.normalize_url(seed_url)
        try:
            domain = urlparse(seed).netloc
        except:
            return []
            
        visited = set()
        queue = [(seed, 0)]
        found_pages = []

        while queue and len(found_pages) < max_pages:
            url, depth = queue.pop(0)
            
            if url in visited or depth > max_depth: continue
            
            # Protection contre les URLs infinies (Crawler Trap)
            if url.count("http") > 1: continue

            visited.add(url)
            found_pages.append(url)
            log_callback(f"Crawling: {url} (Depth {depth})")

            try:
                resp = requests.get(url, timeout=5, headers={"User-Agent": "SEO-Bot/1.0"})
                if resp.status_code != 200: continue
                
                soup = BeautifulSoup(resp.content, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith(("mailto:", "tel:", "#", "javascript:")): continue
                    
                    candidate = urljoin(url, href)
                    if urlparse(candidate).netloc != domain: continue
                    
                    cleaned = SEOLogic.normalize_url(candidate.split("#")[0])
                    
                    if cleaned not in visited and cleaned not in [q[0] for q in queue]:
                         if cleaned.count("http") == 1:
                            queue.append((cleaned, depth + 1))
            except Exception:
                pass
        
        return found_pages

# --- GUI SECTION (Interface Graphique) ---
def create_icon_image():
    """Create a simple in-memory icon without file dependencies"""
    try:
        from PIL import Image, ImageDraw
        import io
        
        # Create 256x256 icon
        img = Image.new('RGB', (256, 256), color='#1f6aa5')
        draw = ImageDraw.Draw(img)
        
        # Draw magnifying glass shape
        draw.ellipse([30, 30, 150, 150], outline='white', width=8)  # Circle
        draw.rectangle([140, 140, 220, 150], fill='white')  # Handle line
        draw.rectangle([140, 145, 220, 155], fill='white')  # Handle
        
        # Draw "S" for SEO
        draw.text((170, 170), "SEO", fill='white', font=None)
        
        return img
    except:
        return None

def run_gui():
    try:
        import customtkinter as ctk
        from tkinter import filedialog, messagebox, simpledialog
    except ImportError:
        print("CustomTkinter introuvable. Installation requise : pip install customtkinter")
        return False

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    class SEOCrawlerApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            # Initialize before any UI references
            self.creds_path = resolve_default_creds_path()
            if self.creds_path:
                self.creds_path = promote_to_canonical_creds(self.creds_path) or self.creds_path
                CONFIG["creds_path"] = self.creds_path
                save_config(CONFIG)
            self.title("SEO Crawler Pro - Easy Everyday Analyzer")
            self.geometry("1000x750")
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(1, weight=1)

            # Try to set icon
            try:
                icon_img = create_icon_image()
                if icon_img:
                    import io
                    from PIL import ImageTk
                    self.icon_photo = ImageTk.PhotoImage(icon_img.resize((64, 64)))
                    self.iconphoto(False, self.icon_photo)
            except:
                pass

            # Sidebar
            self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=10, fg_color=("#f0f0f0", "#1a1a1a"))
            self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=10, pady=10)
            self.sidebar.grid_rowconfigure(10, weight=1)
            
            # Header
            header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(15, 10))
            ctk.CTkLabel(header_frame, text="🔍 SEO Analyzer", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(header_frame, text="Quick & Easy Setup", font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w")

            # === Credentials Section ===
            ctk.CTkLabel(self.sidebar, text="Step 1: Google Credentials", font=ctk.CTkFont(weight="bold")).pack(pady=(15,5), padx=15, anchor="w")
            
            btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            btn_frame.pack(fill="x", padx=15, pady=5)
            ctk.CTkButton(btn_frame, text="📁 Load JSON Key", command=self.load_creds, width=120).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="ℹ️", command=self.show_creds_help, width=40).pack(side="left")
            
            self.lbl_creds = ctk.CTkLabel(self.sidebar, text="✗ No key loaded", text_color="red", font=("Arial", 10, "bold"))
            self.lbl_creds.pack(pady=5, padx=15, anchor="w")

            # === Settings Section ===
            ctk.CTkLabel(self.sidebar, text="Step 2: Configure", font=ctk.CTkFont(weight="bold")).pack(pady=(15,5), padx=15, anchor="w")

            ctk.CTkLabel(self.sidebar, text="Max Pages to Crawl:", font=("Arial", 9)).pack(padx=15, anchor="w")
            self.entry_pages = ctk.CTkEntry(self.sidebar, placeholder_text="5-50 pages")
            self.entry_pages.insert(0, str(CONFIG.get("max_pages", 10)))
            self.entry_pages.pack(pady=5, padx=15, fill="x")

            ctk.CTkLabel(self.sidebar, text="Crawl Depth:", font=("Arial", 9)).pack(padx=15, anchor="w")
            self.entry_depth = ctk.CTkEntry(self.sidebar, placeholder_text="1-3 levels")
            self.entry_depth.insert(0, str(CONFIG.get("max_depth", 2)))
            self.entry_depth.pack(pady=5, padx=15, fill="x")

            # === Presets ===
            ctk.CTkLabel(self.sidebar, text="Quick Presets:", font=ctk.CTkFont(weight="bold", size=9)).pack(pady=(10,5), padx=15, anchor="w")
            preset_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            preset_frame.pack(padx=15, fill="x")
            ctk.CTkButton(preset_frame, text="🏃 Quick (3pg)", command=lambda: self.set_preset(3, 1), width=100).pack(side="left", padx=2)
            ctk.CTkButton(preset_frame, text="⚙️ Normal (10pg)", command=lambda: self.set_preset(10, 2), width=100).pack(side="left", padx=2)
            
            # === Action Button ===
            self.btn_run = ctk.CTkButton(
                self.sidebar, 
                text="▶ LAUNCH ANALYSIS", 
                fg_color="green", 
                hover_color="darkgreen",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.start_thread,
                height=50
            )
            self.btn_run.pack(pady=20, padx=15, fill="x")
            
            # Progress
            self.progress = ctk.CTkProgressBar(self.sidebar)
            self.progress.set(0)
            self.progress.pack(pady=10, padx=15, fill="x")
            self.lbl_progress = ctk.CTkLabel(self.sidebar, text="Ready", font=("Arial", 9), text_color="gray")
            self.lbl_progress.pack(anchor="w", padx=15)

            # === Recent URLs ===
            ctk.CTkLabel(self.sidebar, text="Recent URLs:", font=ctk.CTkFont(weight="bold", size=9)).pack(pady=(15,5), padx=15, anchor="w")
            recent = CONFIG.get("recent_urls", [])
            for url in recent[-3:]:
                btn = ctk.CTkButton(
                    self.sidebar, 
                    text=f"📌 {url[:30]}...", 
                    command=lambda u=url: self.entry_url.delete(0, "end") or self.entry_url.insert(0, u),
                    fg_color="#333333",
                    hover_color="#555555",
                    font=("Arial", 8)
                )
                btn.pack(pady=2, padx=15, fill="x")

            # === Main Content Area ===
            main_frame = ctk.CTkFrame(self, fg_color="transparent")
            main_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=10, pady=10)
            main_frame.grid_columnconfigure(0, weight=1)

            # URL Input with label
            url_label = ctk.CTkLabel(main_frame, text="Target Website URL:", font=ctk.CTkFont(weight="bold"))
            url_label.pack(anchor="w", pady=(0, 5))
            
            self.entry_url = ctk.CTkEntry(main_frame, placeholder_text="https://www.example.com", height=40, font=("Arial", 12))
            self.entry_url.pack(fill="x", pady=(0, 15))
            self.entry_url.bind("<Return>", lambda e: self.start_thread())

            # Tabs: Info & Log
            tabview = ctk.CTkTabview(main_frame)
            tabview.pack(fill="both", expand=True)
            tabview.add("📊 Analysis Log")
            tabview.add("ℹ️ Help & Tips")
            tabview.add("⚙️ Settings")

            # Log tab
            self.log_box = ctk.CTkTextbox(tabview.tab("📊 Analysis Log"))
            self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
            self.log("Welcome! 👋 Follow these steps:\n1. Load your Google Cloud JSON key\n2. Enter a website URL\n3. Click LAUNCH ANALYSIS\n\nNeed help? Check the 'Help & Tips' tab.")

            # Help tab
            help_text = ctk.CTkTextbox(tabview.tab("ℹ️ Help & Tips"))
            help_text.insert("0.0", """🎯 HOW TO USE:
            
1. GET GOOGLE CLOUD CREDENTIALS:
   - Go to Google Cloud Console
   - Create a new project
   - Enable "Cloud Natural Language API"
   - Create a Service Account JSON key
   - Download and load it here

2. ENTER WEBSITE:
   - Full URL starting with https://
   - Example: https://www.bbc.com

3. CONFIGURE:
   - Max Pages: 5-50 (more = slower)
   - Depth: 1-2 (site structure levels)

4. LAUNCH & WAIT:
   - Watch progress bar
   - Check log for updates
   - Download CSV when done

💡 TIPS:
   - Use "Quick" preset for testing
   - Large sites take longer
   - CSV output includes: URL, Entity, Importance, Type""")
            help_text.configure(state="disabled")
            help_text.pack(fill="both", expand=True, padx=5, pady=5)

            # Settings tab
            settings_text = ctk.CTkTextbox(tabview.tab("⚙️ Settings"))
            settings_text.insert("0.0", f"""📋 CURRENT CONFIGURATION:

Max Pages: {CONFIG.get("max_pages", 10)}
Crawl Depth: {CONFIG.get("max_depth", 2)}
Credentials: {self.get_creds_display()}

🔧 To change settings:
   1. Update values in main interface
   2. They auto-save on analysis start

📁 Config Location:
   {CONFIG_DIR}

🗑️ CLEAR SETTINGS:
   Delete the folder above and restart""")
            settings_text.configure(state="disabled")
            settings_text.pack(fill="both", expand=True, padx=5, pady=5)

            if self.creds_path and os.path.exists(self.creds_path):
                self.update_creds_label()
                self.set_creds_env()

        def set_creds_env(self):
            if self.creds_path and os.path.exists(self.creds_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.creds_path
                return True
            return False

        def set_preset(self, pages, depth):
            self.entry_pages.delete(0, "end")
            self.entry_pages.insert(0, str(pages))
            self.entry_depth.delete(0, "end")
            self.entry_depth.insert(0, str(depth))
            self.lbl_progress.configure(text=f"Preset: {pages} pages, depth {depth}")

        def show_creds_help(self):
            messagebox.showinfo(
                "Google Cloud Setup", 
                """📖 How to get your credentials:

1. Visit: https://console.cloud.google.com
2. Create a new project
3. Search for "Natural Language API"
4. Enable it
5. Go to Credentials → Create Service Account
6. Download the JSON key
7. Click 'Load JSON Key' and select it

More help: https://cloud.google.com/natural-language/docs/quickstart"""
            )

        def get_creds_display(self):
            if self.creds_path:
                return os.path.basename(self.creds_path)
            return "None"

        def log(self, msg):
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="normal")

        def update_creds_label(self):
            self.lbl_creds.configure(
                text=f"✓ {os.path.basename(self.creds_path)}", 
                text_color="green"
            )

        def load_creds(self):
            f = filedialog.askopenfilename(
                filetypes=[("JSON", "*.json")],
                title="Select Google Cloud Credentials JSON"
            )
            if f:
                self.creds_path = promote_to_canonical_creds(f) or f
                self.set_creds_env()
                CONFIG["creds_path"] = self.creds_path
                save_config(CONFIG)
                self.update_creds_label()
                self.log(f"✓ Credentials loaded: {os.path.basename(self.creds_path)}")

        def start_thread(self):
            if not self.creds_path or not os.path.exists(self.creds_path):
                messagebox.showerror("Error", "⚠️ Please load a valid Google Cloud JSON credentials file!")
                return
            self.set_creds_env()
            
            url = self.entry_url.get().strip()
            if not url:
                messagebox.showerror("Error", "⚠️ Please enter a website URL!")
                return
            
            if not url.startswith("http"):
                url = "https://" + url
                self.entry_url.delete(0, "end")
                self.entry_url.insert(0, url)
            
            try:
                pages = int(self.entry_pages.get())
                depth = int(self.entry_depth.get())
            except ValueError:
                messagebox.showerror("Error", "⚠️ Pages and Depth must be numbers!")
                return
            
            # Save to recent
            recent = CONFIG.get("recent_urls", [])
            if url in recent:
                recent.remove(url)
            recent.insert(0, url)
            CONFIG["recent_urls"] = recent[-10:]
            CONFIG["max_pages"] = pages
            CONFIG["max_depth"] = depth
            save_config(CONFIG)
            
            # Ask where to save
            save_path = filedialog.asksaveasfilename(
                defaultextension=".csv", 
                filetypes=[("CSV Files", "*.csv")],
                initialfile=f"seo_audit_{url.split('//')[1][:20]}.csv"
            )
            
            if not save_path: 
                return

            self.btn_run.configure(state="disabled", text="⏳ Running...")
            self.progress.set(0)
            self.log_box.delete("1.0", "end")
            
            threading.Thread(
                target=self.process, 
                args=(url, pages, depth, save_path), 
                daemon=True
            ).start()

        def process(self, url, pages, depth, save_path):
            try:
                self.log(f"🚀 Starting crawl on {url}...\n")
                
                # Crawl
                found_urls = SEOLogic.crawl(url, pages, depth, self.log)
                self.log(f"\n✓ Found {len(found_urls)} pages. Starting NLP analysis...\n")
                
                # Analyze
                results = []
                total = len(found_urls)
                for i, u in enumerate(found_urls):
                    self.lbl_progress.configure(text=f"Analyzing {i+1}/{total}")
                    self.log(f"[{i+1}/{total}] Analyzing: {u}")
                    txt, html = SEOLogic.fetch_content_and_html(u)
                    if txt:
                        self.log(f"  → Extracted {len(txt)} characters of text")
                        data = SEOLogic.analyze_entities(txt, u, self.log)
                        results.extend(data)
                        self.log(f"  → Found {len(data)} entities")
                        if not data:
                            debug_base = DEBUG_DIR / (urlparse(u).netloc.replace(":", "_") + "_" + str(i+1))
                            try:
                                if html:
                                    (debug_base.with_suffix(".html")).write_text(html, encoding="utf-8")
                                (debug_base.with_suffix(".txt")).write_text(txt, encoding="utf-8")
                                self.log(f"  → Debug saved: {debug_base.with_suffix('.txt').name}")
                            except Exception:
                                pass
                    else:
                        self.log(f"  → Could not fetch content")
                    self.progress.set((i+1)/total)
                
                # Save
                if results:
                    try:
                        with open(save_path, "w", newline="", encoding="utf-8") as f:
                            writer = csv.DictWriter(f, fieldnames=["source", "name", "salience", "category"])
                            writer.writeheader()
                            writer.writerows(results)
                        self.log(f"\n✅ SUCCESS! Results saved to:\n{save_path}")
                        self.log(f"\n📊 Total entities found: {len(results)}")
                        messagebox.showinfo("✅ Done!", f"Analysis complete!\n\nFound {len(results)} entities\n\nSaved to:\n{os.path.basename(save_path)}")
                    except Exception as e:
                        self.log(f"\n❌ Save error: {e}")
                else:
                    self.log("\n⚠️ No entities found. Try a different URL or check content.")
            except Exception as e:
                self.log(f"\n❌ Error: {e}")
            finally:
                self.btn_run.configure(state="normal", text="▶ LAUNCH ANALYSIS")
                self.lbl_progress.configure(text="Ready")

    app = SEOCrawlerApp()
    app.mainloop()
    return True


# --- CLI SECTION (Ligne de commande) ---
def run_cli():
    parser = argparse.ArgumentParser(description="SEO Crawler CLI")
    parser.add_argument("--url", help="URL cible", required=True)
    parser.add_argument("--creds", help="Chemin vers clé JSON", required=True)
    parser.add_argument("--pages", type=int, default=5)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--out", default="report.csv")
    args = parser.parse_args()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.creds
    print(f"Mode CLI : Crawl de {args.url}...")
    
    urls = SEOLogic.crawl(args.url, args.pages, args.depth)
    print(f"{len(urls)} pages trouvées.")
    
    results = []
    for u in urls:
        print(f"Analyse : {u}")
        txt, _html = SEOLogic.fetch_content_and_html(u)
        if txt:
            results.extend(SEOLogic.analyze_entities(txt, u, print))
            
    if results:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["source", "name", "salience", "category"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Sauvegardé dans {args.out}")

# --- POINT D'ENTREE ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli()
    else:
        success = run_gui()
        if not success:
            print("\nEchec GUI. Utilisez le mode commande :")
            print("python analyze2.py --url https://site.com --creds key.json")