import streamlit as st
import csv
import os
import sys
import io
import json
from urllib.parse import urlparse, urljoin
from pathlib import Path
from collections import Counter

# Dependency check
try:
    import requests
    from bs4 import BeautifulSoup
    from google.cloud import language_v1
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError as e:
    st.error(f"Missing dependencies: {e}")
    st.info("Run: pip install google-cloud-language beautifulsoup4 requests streamlit pandas plotly")
    sys.exit(1)

# Page config
st.set_page_config(
    page_title="SEO Crawler Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state FIRST (before any usage)
if "creds_uploaded" not in st.session_state:
    st.session_state.creds_uploaded = False
if "creds_path" not in st.session_state:
    st.session_state.creds_path = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []
if "running" not in st.session_state:
    st.session_state.running = False

# --- Config & State ---
CONFIG_DIR = Path.home() / ".seo_crawler"
CONFIG_FILE = CONFIG_DIR / "config.json"
CONFIG_DIR.mkdir(exist_ok=True)

def load_config():
    if CONFIG_FILE.exists():
        try:
            import json
            return json.loads(CONFIG_FILE.read_text())
        except:
            return {}
    return {}

def save_config(config):
    try:
        import json
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
    except:
        pass

# --- LOGIC CLASS (Core) ---
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
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, "html.parser")
            # Clean noise
            for tag in soup(["script", "style", "nav", "footer", "aside", "iframe", "noscript"]):
                tag.decompose()
            for div in soup.find_all("div", class_=["cookie", "banner", "menu", "header", "gdpr"]):
                div.decompose()
                
            text = soup.get_text(separator=' ')
            text = " ".join(text.split())
            return text[:10000]
        except Exception:
            return None

    @staticmethod
    def analyze_entities(text_content, source_url):
        if not text_content:
            return []
        try:
            client = language_v1.LanguageServiceClient()
            document = language_v1.Document(content=text_content, type_=language_v1.Document.Type.PLAIN_TEXT)
            response = client.analyze_entities(request={"document": document, "encoding_type": language_v1.EncodingType.UTF8})
            
            results = []
            for entity in response.entities:
                if entity.salience < 0.01:
                    continue 
                results.append({
                    "source": source_url,
                    "name": entity.name,
                    "salience": round(entity.salience, 4),
                    "category": language_v1.Entity.Type(entity.type_).name
                })
            return results
        except Exception as e:
            st.error(f"Google NLP Error on {source_url}: {e}")
            return []

    @staticmethod
    def crawl(seed_url, max_pages, max_depth, progress_callback=None):
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
            
            if url in visited or depth > max_depth:
                continue
            
            # Protection against infinite URLs (Crawler Trap)
            if url.count("http") > 1:
                continue

            visited.add(url)
            found_pages.append(url)
            
            if progress_callback:
                progress_callback(f"Crawling: {url} (Depth {depth})")

            try:
                resp = requests.get(url, timeout=5, headers={"User-Agent": "SEO-Bot/1.0"})
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.content, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith(("mailto:", "tel:", "#", "javascript:")):
                        continue
                    
                    candidate = urljoin(url, href)
                    if urlparse(candidate).netloc != domain:
                        continue
                    
                    cleaned = SEOLogic.normalize_url(candidate.split("#")[0])
                    
                    if cleaned not in visited and cleaned not in [q[0] for q in queue]:
                        if cleaned.count("http") == 1:
                            queue.append((cleaned, depth + 1))
            except Exception:
                pass
        
        return found_pages

# --- VISUALIZATION & ANALYSIS FUNCTIONS ---
def create_salience_chart(results):
    """Create salience distribution chart"""
    if not results:
        return None
    
    df = pd.DataFrame(results)
    df_sorted = df.nlargest(15, 'salience')[['name', 'salience']]
    
    fig = px.bar(df_sorted, x='salience', y='name', orientation='h',
                 title='Top 15 Entities by Salience (Importance)',
                 labels={'salience': 'Salience Score', 'name': 'Entity'},
                 color='salience', color_continuous_scale='Viridis')
    fig.update_layout(height=500, showlegend=False)
    return fig

def create_category_chart(results):
    """Create entity category distribution"""
    if not results:
        return None
    
    df = pd.DataFrame(results)
    category_counts = df['category'].value_counts()
    
    fig = px.pie(values=category_counts.values, names=category_counts.index,
                 title='Entity Types Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(height=500)
    return fig

def create_page_stats(results):
    """Create statistics by page"""
    if not results:
        return None
    
    df = pd.DataFrame(results)
    page_counts = df['source'].value_counts().reset_index()
    page_counts.columns = ['URL', 'Entity Count']
    page_counts['Domain'] = page_counts['URL'].apply(lambda x: urlparse(x).netloc)
    
    fig = px.bar(page_counts, x='Domain', y='Entity Count',
                 title='Entities Found Per Page',
                 labels={'Entity Count': 'Number of Entities'},
                 color='Entity Count', color_continuous_scale='Blues')
    fig.update_layout(height=400, xaxis_tickangle=-45)
    return fig

def get_statistics(results):
    """Get detailed statistics"""
    if not results:
        return {}
    
    df = pd.DataFrame(results)
    return {
        'total_entities': len(df),
        'unique_entities': df['name'].nunique(),
        'pages_analyzed': df['source'].nunique(),
        'avg_salience': df['salience'].mean(),
        'max_salience': df['salience'].max(),
        'min_salience': df['salience'].min(),
        'categories': df['category'].nunique(),
        'top_entity': df.nlargest(1, 'salience')['name'].values[0] if len(df) > 0 else 'N/A'
    }

def export_to_json(results):
    """Export results as JSON"""
    return json.dumps(results, indent=2)

def create_entity_filter(results):
    """Create interactive entity filtering"""
    if not results:
        return None
    
    df = pd.DataFrame(results)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_salience = st.slider('Min Salience:', 0.0, 1.0, 0.0, 0.01)
    
    with col2:
        selected_categories = st.multiselect(
            'Entity Types:',
            options=sorted(df['category'].unique()),
            default=sorted(df['category'].unique())
        )
    
    with col3:
        search_term = st.text_input('Search Entity:', placeholder='e.g., Google, New York')
    
    # Apply filters
    filtered_df = df[
        (df['salience'] >= min_salience) &
        (df['category'].isin(selected_categories))
    ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False, na=False)
        ]
    
    return filtered_df.sort_values('salience', ascending=False)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔍 SEO Analyzer")
    st.caption("Quick & Easy Setup")
    
    st.divider()
    
    # Step 1: Credentials
    st.subheader("Step 1: Google Credentials")
    
    uploaded_file = st.file_uploader(
        "📁 Upload JSON Key",
        type="json",
        key="creds_upload"
    )
    
    if uploaded_file:
        # Save temporarily
        creds_path = f"/tmp/{uploaded_file.name}"
        with open(creds_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        st.session_state.creds_uploaded = True
        st.session_state.creds_path = creds_path
        st.success(f"✓ {uploaded_file.name} loaded")
    
    if st.session_state.creds_uploaded:
        st.markdown("✅ Credentials ready")
    else:
        st.markdown("❌ No credentials loaded")
    
    if st.button("ℹ️ How to get credentials"):
        st.info("""
        **📖 How to get your credentials:**
        
        1. Visit: https://console.cloud.google.com
        2. Create a new project
        3. Search for "Natural Language API"
        4. Enable it
        5. Go to Credentials → Create Service Account
        6. Download the JSON key
        7. Upload it here
        
        [More help](https://cloud.google.com/natural-language/docs/quickstart)
        """)
    
    st.divider()
    
    # Step 2: Configure
    st.subheader("Step 2: Configure")
    
    max_pages = st.slider(
        "Max Pages to Crawl:",
        min_value=1,
        max_value=50,
        value=10,
        help="More pages = longer analysis"
    )
    
    max_depth = st.slider(
        "Crawl Depth:",
        min_value=1,
        max_value=3,
        value=2,
        help="Site structure levels to explore"
    )
    
    st.divider()
    
    # Presets
    st.subheader("Quick Presets")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏃 Quick (3pg)", use_container_width=True):
            st.session_state.max_pages = 3
            st.session_state.max_depth = 1
            st.rerun()
    with col2:
        if st.button("⚙️ Normal (10pg)", use_container_width=True):
            st.session_state.max_pages = 10
            st.session_state.max_depth = 2
            st.rerun()

# --- MAIN CONTENT ---
st.title("SEO Crawler Pro - Easy Everyday Analyzer")

# URL Input
url_input = st.text_input(
    "Target Website URL:",
    placeholder="https://www.example.com",
    help="Full URL starting with https://"
)

# Tabs
tab_analysis, tab_help, tab_settings = st.tabs(["📊 Analysis", "ℹ️ Help & Tips", "⚙️ Settings"])

with tab_analysis:
    if st.button("▶ LAUNCH ANALYSIS", type="primary", use_container_width=True):
        if not st.session_state.creds_uploaded:
            st.error("⚠️ Please load your Google Cloud JSON credentials first!")
        elif not url_input.strip():
            st.error("⚠️ Please enter a website URL!")
        else:
            url = url_input.strip()
            if not url.startswith("http"):
                url = "https://" + url
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.empty()
            
            logs = []
            
            def log_message(msg):
                logs.append(msg)
                log_container.text_area("Analysis Log", value="\n".join(logs), height=300, disabled=True)
            
            log_message(f"🚀 Starting crawl on {url}...\n")
            
            try:
                # Crawl
                found_urls = SEOLogic.crawl(url, max_pages, max_depth, log_message)
                log_message(f"\n✓ Found {len(found_urls)} pages. Starting NLP analysis...\n")
                
                # Analyze
                results = []
                total = len(found_urls)
                
                for i, u in enumerate(found_urls):
                    status_text.text(f"Analyzing {i+1}/{total}")
                    log_message(f"[{i+1}/{total}] Analyzing: {u}")
                    
                    txt = SEOLogic.fetch_content(u)
                    if txt:
                        data = SEOLogic.analyze_entities(txt, u)
                        results.extend(data)
                        log_message(f"  → Found {len(data)} entities")
                    else:
                        log_message(f"  → Could not fetch content")
                    
                    progress_bar.progress((i+1) / total)
                
                # Store results
                st.session_state.analysis_results = results
                
                if results:
                    log_message(f"\n✅ SUCCESS! Analysis complete!")
                    log_message(f"📊 Total entities found: {len(results)}")
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    log_container.empty()
                    
                    # Display success
                    st.success(f"✅ Analysis complete! Found {len(results)} entities")
                    
                    # Show statistics
                    st.divider()
                    st.subheader("📈 Analysis Summary")
                    
                    stats = get_statistics(results)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Entities", stats['total_entities'])
                    with col2:
                        st.metric("Unique Entities", stats['unique_entities'])
                    with col3:
                        st.metric("Pages Analyzed", stats['pages_analyzed'])
                    with col4:
                        st.metric("Avg Importance", f"{stats['avg_salience']:.3f}")
                    
                    st.divider()
                    
                    # Visualizations
                    st.subheader("📊 Data Visualization")
                    
                    viz_col1, viz_col2 = st.columns(2)
                    
                    with viz_col1:
                        fig_salience = create_salience_chart(results)
                        if fig_salience:
                            st.plotly_chart(fig_salience, use_container_width=True)
                    
                    with viz_col2:
                        fig_category = create_category_chart(results)
                        if fig_category:
                            st.plotly_chart(fig_category, use_container_width=True)
                    
                    fig_pages = create_page_stats(results)
                    if fig_pages:
                        st.plotly_chart(fig_pages, use_container_width=True)
                    
                    st.divider()
                    
                    # Filtering section
                    st.subheader("🔍 Filter & Explore")
                    filtered_df = create_entity_filter(results)
                    
                    if filtered_df is not None:
                        st.write(f"**Showing {len(filtered_df)} of {len(results)} entities**")
                        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    
                    # Export options
                    st.subheader("💾 Export Results")
                    
                    exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)
                    
                    with exp_col1:
                        # CSV
                        csv_buffer = io.StringIO()
                        writer = csv.DictWriter(csv_buffer, fieldnames=["source", "name", "salience", "category"])
                        writer.writeheader()
                        writer.writerows(results)
                        st.download_button(
                            label="📥 CSV",
                            data=csv_buffer.getvalue(),
                            file_name=f"seo_audit_{urlparse(url).netloc[:20]}.csv",
                            mime="text/csv"
                        )
                    
                    with exp_col2:
                        # JSON
                        json_data = export_to_json(results)
                        st.download_button(
                            label="📥 JSON",
                            data=json_data,
                            file_name=f"seo_audit_{urlparse(url).netloc[:20]}.json",
                            mime="application/json"
                        )
                    
                    with exp_col3:
                        # Excel
                        try:
                            excel_buffer = io.BytesIO()
                            df = pd.DataFrame(results)
                            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                df.to_excel(writer, index=False, sheet_name='Entities')
                            excel_buffer.seek(0)
                            st.download_button(
                                label="📥 Excel",
                                data=excel_buffer.getvalue(),
                                file_name=f"seo_audit_{urlparse(url).netloc[:20]}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        except:
                            st.button("📥 Excel", disabled=True, help="openpyxl not installed")
                    
                    with exp_col4:
                        # Top entities summary
                        if st.button("📋 Summary"):
                            summary = f"""
# SEO Analysis Report
## {url}

### Statistics
- Total Entities: {stats['total_entities']}
- Unique Entities: {stats['unique_entities']}
- Pages Analyzed: {stats['pages_analyzed']}
- Average Salience: {stats['avg_salience']:.4f}
- Top Entity: {stats['top_entity']}

### Top Entities
"""
                            df = pd.DataFrame(results)
                            for idx, row in df.nlargest(10, 'salience').iterrows():
                                summary += f"\n- {row['name']} ({row['category']}) - {row['salience']:.4f}"
                            
                            st.text(summary)
                    
                else:
                    log_message("\n⚠️ No entities found. Try a different URL or check content.")
                    st.warning("No entities found. Try a different URL or check content.")
                    
            except Exception as e:
                log_message(f"\n❌ Error: {e}")
                st.error(f"Error: {e}")

with tab_help:
    st.markdown("""
    ### 🎯 HOW TO USE:
    
    #### 1. GET GOOGLE CLOUD CREDENTIALS:
    - Go to [Google Cloud Console](https://console.cloud.google.com)
    - Create a new project
    - Enable "Cloud Natural Language API"
    - Create a Service Account JSON key
    - Download and upload it here
    
    #### 2. ENTER WEBSITE:
    - Full URL starting with https://
    - Example: https://www.bbc.com
    
    #### 3. CONFIGURE:
    - **Max Pages**: 5-50 (more = slower)
    - **Depth**: 1-2 (site structure levels)
    
    #### 4. LAUNCH & WAIT:
    - Watch progress bar
    - Check log for updates
    - Download CSV when done
    
    ### 💡 TIPS:
    - Use "Quick" preset for testing
    - Large sites take longer
    - CSV output includes: URL, Entity, Importance, Type
    """)

with tab_settings:
    st.markdown(f"""
    ### 📋 CURRENT CONFIGURATION:
    
    - **Max Pages**: {max_pages}
    - **Crawl Depth**: {max_depth}
    - **Credentials**: {'Loaded' if st.session_state.creds_uploaded else 'Not loaded'}
    
    ### 🔧 To change settings:
    1. Update values in the sidebar
    2. They auto-save on analysis start
    
    ### 📁 Config Location:
    `{CONFIG_DIR}`
    """)
    
    if st.button("🗑️ Clear Session"):
        st.session_state.clear()
        st.rerun()
