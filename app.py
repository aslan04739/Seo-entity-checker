import os
import csv
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse, urljoin

import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
from google.cloud import language_v1

# --- Configuration for CustomTkinter ---
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class SEOCrawlerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Google NLP SEO Crawler")
        self.geometry("900x700")

        # Layout Grid Config
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # --- Sidebar (Controls) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SEO Analyzer", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Credentials File
        self.cred_label = ctk.CTkLabel(self.sidebar_frame, text="Credentials JSON:", anchor="w")
        self.cred_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.btn_creds = ctk.CTkButton(self.sidebar_frame, text="Select JSON", command=self.select_credentials)
        self.btn_creds.grid(row=2, column=0, padx=20, pady=5)
        self.lbl_creds_status = ctk.CTkLabel(self.sidebar_frame, text="Not Selected", text_color="red", font=("Arial", 10))
        self.lbl_creds_status.grid(row=3, column=0, padx=20, pady=0)

        # Settings
        self.lbl_pages = ctk.CTkLabel(self.sidebar_frame, text="Max Pages:", anchor="w")
        self.lbl_pages.grid(row=4, column=0, padx=20, pady=(20, 0), sticky="w")
        self.entry_pages = ctk.CTkEntry(self.sidebar_frame)
        self.entry_pages.grid(row=5, column=0, padx=20, pady=5)
        self.entry_pages.insert(0, "10")

        self.lbl_depth = ctk.CTkLabel(self.sidebar_frame, text="Max Depth:", anchor="w")
        self.lbl_depth.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        self.entry_depth = ctk.CTkEntry(self.sidebar_frame)
        self.entry_depth.grid(row=7, column=0, padx=20, pady=5)
        self.entry_depth.insert(0, "1")

        # Action Button
        self.btn_run = ctk.CTkButton(self.sidebar_frame, text="Start Analysis", fg_color="green", hover_color="darkgreen", command=self.start_thread)
        self.btn_run.grid(row=9, column=0, padx=20, pady=20)

        # --- Main Area ---
        
        # URL Input
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        
        self.lbl_url = ctk.CTkLabel(self.url_frame, text="Target URL (Seed):")
        self.lbl_url.pack(side="left", padx=10)
        self.entry_url = ctk.CTkEntry(self.url_frame, placeholder_text="https://example.com")
        self.entry_url.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # Logs / Output
        self.log_textbox = ctk.CTkTextbox(self, width=600)
        self.log_textbox.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")
        self.log("Welcome! Please select your Google Cloud credentials JSON and enter a URL.")

        # Variables
        self.credentials_path = None

    def log(self, message):
        """Helper to append text to the GUI log window safely"""
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")

    def select_credentials(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            self.credentials_path = filename
            self.lbl_creds_status.configure(text=os.path.basename(filename), text_color="green")
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = filename
            self.log(f"Credentials loaded: {filename}")

    def start_thread(self):
        """Run the crawler in a separate thread to keep GUI responsive"""
        if not self.credentials_path:
            messagebox.showerror("Error", "Please select a Google Cloud Credentials JSON file first.")
            return
        
        url = self.entry_url.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        try:
            max_p = int(self.entry_pages.get())
            max_d = int(self.entry_depth.get())
        except ValueError:
            messagebox.showerror("Error", "Pages and Depth must be integers.")
            return

        self.btn_run.configure(state="disabled", text="Running...")
        self.log_textbox.delete("1.0", "end")
        
        # threading ensures the GUI doesn't freeze while crawling
        threading.Thread(target=self.run_process, args=(url, max_p, max_d), daemon=True).start()

    def run_process(self, seed_url, max_pages, max_depth):
        self.log("=" * 40)
        self.log(f"Starting crawl for: {seed_url}")
        self.log("=" * 40)

        all_pages = self.crawl_site(seed_url, max_pages, max_depth)
        self.log(f"\nFound {len(all_pages)} pages to analyze.")

        results = []
        for url in all_pages:
            self.log(f"Analyzing: {url}...")
            content = self.fetch_url_content(url)
            if content:
                entities = self.analyze_seo_text(content, source=url)
                results.extend(entities)
            else:
                self.log(f"Failed to fetch content for {url}")

        if results:
            try:
                # --- FIXED: Save to Downloads folder to avoid Read-Only errors ---
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                filename = os.path.join(downloads_path, "seo_entities_report.csv")

                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["source", "name", "salience", "category"])
                    writer.writeheader()
                    writer.writerows(results)
                
                self.log(f"\nSUCCESS! Results saved to: {filename}")
                messagebox.showinfo("Done", f"Analysis complete!\nSaved to your Downloads folder:\n{filename}")
            except Exception as e:
                self.log(f"Error saving CSV: {e}")
        else:
            self.log("No entities found.")

        self.btn_run.configure(state="normal", text="Start Analysis")

    # --- Logic Methods ---

    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc
        path = parsed.path or "/"
        return f"{scheme}://{netloc}{path}"

    def crawl_site(self, seed_url, max_pages, max_depth):
        seed = self.normalize_url(seed_url)
        try:
            domain = urlparse(seed).netloc
        except:
            self.log("Invalid Seed URL")
            return []
            
        visited = set()
        queue = [(seed, 0)]
        found = []

        while queue and len(found) < max_pages:
            url, depth = queue.pop(0)
            if url in visited or depth > max_depth:
                continue
            visited.add(url)
            found.append(url)

            # Update GUI log
            self.log(f"Crawling: {url} (Depth {depth})")

            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code != 200: continue
                
                soup = BeautifulSoup(resp.content, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith(("mailto:", "tel:", "javascript:", "#")): continue
                    candidate = urljoin(url, href)
                    if urlparse(candidate).netloc != domain: continue
                    
                    cleaned = self.normalize_url(candidate.split("#")[0])
                    if cleaned not in visited and len(found) + len(queue) < max_pages:
                        queue.append((cleaned, depth + 1))
            except Exception as e:
                self.log(f"Error crawling {url}: {e}")
        return found

    def fetch_url_content(self, url):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            return text[:5000]
        except Exception as e:
            return None

    def analyze_seo_text(self, text_content, source="text"):
        try:
            client = language_v1.LanguageServiceClient()
            document = language_v1.Document(content=text_content, type_=language_v1.Document.Type.PLAIN_TEXT)
            response = client.analyze_entities(request={"document": document})

            entities = []
            for entity in response.entities:
                if entity.salience > 0.01:
                    entities.append({
                        "source": source,
                        "name": entity.name,
                        "salience": entity.salience,
                        "category": entity.type_.name,
                    })
            return entities
        except Exception as e:
            self.log(f"API Error: {str(e)}")
            return []

if __name__ == "__main__":
    app = SEOCrawlerApp()
    app.mainloop()