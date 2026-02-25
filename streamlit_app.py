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
    from google.oauth2 import service_account
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
if "lang" not in st.session_state:
    st.session_state.lang = "en"


TRANSLATIONS = {
    "en": {
        "app_title": "SEO GEO Entity Checker",
        "sidebar_title": "🔍 SEO Local Tool",
        "sidebar_caption": "Quick & Easy Setup",
        "language": "Language",
        "step1": "Step 1: Google Credentials",
        "upload_key": "📁 Upload JSON Key",
        "creds_loaded": "✓ {name} loaded (saved as default)",
        "creds_ready": "✅ Credentials ready",
        "creds_using": "Using: {name}",
        "creds_missing": "❌ No credentials loaded",
        "how_get_creds": "ℹ️ How to get credentials",
        "how_get_creds_content": """
        **📖 How to get your credentials:**

        1. Visit: https://console.cloud.google.com
        2. Create a new project
        3. Search for \"Natural Language API\"
        4. Enable it
        5. Go to Credentials → Create Service Account
        6. Download the JSON key
        7. Upload it here

        [More help](https://cloud.google.com/natural-language/docs/quickstart)
        """,
        "step2": "Step 2: Configure",
        "max_pages": "Max Pages to Crawl:",
        "max_pages_help": "More pages = longer analysis",
        "max_depth": "Crawl Depth:",
        "max_depth_help": "Site structure levels to explore",
        "quick_presets": "Quick Presets",
        "preset_quick": "🏃 Quick (3pg)",
        "preset_normal": "⚙️ Normal (10pg)",
        "target_url": "Target Website URL:",
        "target_url_placeholder": "https://www.example.com",
        "target_url_help": "Full URL starting with https://",
        "tab_analysis": "📊 Analysis",
        "tab_help": "ℹ️ Help & Tips",
        "tab_settings": "⚙️ Settings",
        "launch_analysis": "▶ LAUNCH ANALYSIS",
        "load_creds_first": "⚠️ Please load your Google Cloud JSON credentials first!",
        "enter_url": "⚠️ Please enter a website URL!",
        "analysis_log": "Analysis Log",
        "starting_crawl": "🚀 Starting crawl on {url}...",
        "found_pages": "✓ Found {count} pages. Starting NLP analysis...",
        "analyzing_step": "Analyzing {current}/{total}",
        "analyzing_url": "[{current}/{total}] Analyzing: {url}",
        "entities_found": "  → Found {count} entities",
        "fetch_failed": "  → Could not fetch content",
        "success_done": "✅ SUCCESS! Analysis complete!",
        "success_total": "📊 Total entities found: {count}",
        "success_banner": "✅ Analysis complete! Found {count} entities",
        "summary": "📈 Analysis Summary",
        "metric_total": "Total Entities",
        "metric_unique": "Unique Entities",
        "metric_pages": "Pages Analyzed",
        "metric_avg": "Avg Importance",
        "viz": "📊 Data Visualization",
        "filter": "🔍 Filter & Explore",
        "showing": "Showing {shown} of {total} entities",
        "export": "💾 Export Results",
        "no_entities": "No entities found. Try a different URL or check content.",
        "error_prefix": "Error: {error}",
        "help_content": """
    ### 🎯 HOW TO USE:

    #### 1. GET GOOGLE CLOUD CREDENTIALS:
    - Go to [Google Cloud Console](https://console.cloud.google.com)
    - Create a new project
    - Enable \"Cloud Natural Language API\"
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
    - Use \"Quick\" preset for testing
    - Large sites take longer
    - CSV output includes: URL, Entity, Importance, Type
    """,
        "settings_title": "### 📋 CURRENT CONFIGURATION:",
        "settings_change": "### 🔧 To change settings:",
        "settings_change_steps": "1. Update values in the sidebar\n2. They auto-save on analysis start",
        "config_location": "### 📁 Config Location:",
        "loaded": "Loaded",
        "not_loaded": "Not loaded",
        "clear_session": "🗑️ Clear Session",
    },
    "fr": {
        "app_title": "Vérificateur d'entités SEO GEO",
        "sidebar_title": "🔍 SEO Local Tool",
        "sidebar_caption": "Configuration rapide",
        "language": "Langue",
        "step1": "Étape 1 : Identifiants Google",
        "upload_key": "📁 Importer la clé JSON",
        "creds_loaded": "✓ {name} chargé (enregistré par défaut)",
        "creds_ready": "✅ Identifiants prêts",
        "creds_using": "Utilisé : {name}",
        "creds_missing": "❌ Aucun identifiant chargé",
        "how_get_creds": "ℹ️ Obtenir les identifiants",
        "how_get_creds_content": """
        **📖 Comment obtenir vos identifiants :**

        1. Allez sur : https://console.cloud.google.com
        2. Créez un nouveau projet
        3. Recherchez \"Natural Language API\"
        4. Activez-la
        5. Ouvrez Identifiants → Créer un compte de service
        6. Téléchargez la clé JSON
        7. Importez-la ici

        [Aide supplémentaire](https://cloud.google.com/natural-language/docs/quickstart)
        """,
        "step2": "Étape 2 : Configuration",
        "max_pages": "Nombre max de pages :",
        "max_pages_help": "Plus de pages = analyse plus longue",
        "max_depth": "Profondeur du crawl :",
        "max_depth_help": "Niveaux de structure du site à explorer",
        "quick_presets": "Préréglages rapides",
        "preset_quick": "🏃 Rapide (3p)",
        "preset_normal": "⚙️ Normal (10p)",
        "target_url": "URL du site cible :",
        "target_url_placeholder": "https://www.example.com",
        "target_url_help": "URL complète commençant par https://",
        "tab_analysis": "📊 Analyse",
        "tab_help": "ℹ️ Aide & conseils",
        "tab_settings": "⚙️ Paramètres",
        "launch_analysis": "▶ LANCER L'ANALYSE",
        "load_creds_first": "⚠️ Chargez d'abord vos identifiants JSON Google Cloud !",
        "enter_url": "⚠️ Entrez une URL de site web !",
        "analysis_log": "Journal d'analyse",
        "starting_crawl": "🚀 Démarrage du crawl sur {url}...",
        "found_pages": "✓ {count} pages trouvées. Début de l'analyse NLP...",
        "analyzing_step": "Analyse {current}/{total}",
        "analyzing_url": "[{current}/{total}] Analyse : {url}",
        "entities_found": "  → {count} entités trouvées",
        "fetch_failed": "  → Impossible de récupérer le contenu",
        "success_done": "✅ SUCCÈS ! Analyse terminée !",
        "success_total": "📊 Total d'entités trouvées : {count}",
        "success_banner": "✅ Analyse terminée ! {count} entités trouvées",
        "summary": "📈 Résumé de l'analyse",
        "metric_total": "Entités totales",
        "metric_unique": "Entités uniques",
        "metric_pages": "Pages analysées",
        "metric_avg": "Importance moyenne",
        "viz": "📊 Visualisation des données",
        "filter": "🔍 Filtrer & explorer",
        "showing": "Affichage de {shown} sur {total} entités",
        "export": "💾 Exporter les résultats",
        "no_entities": "Aucune entité trouvée. Essayez une autre URL ou vérifiez le contenu.",
        "error_prefix": "Erreur : {error}",
        "help_content": """
    ### 🎯 MODE D'EMPLOI :

    #### 1. OBTENIR LES IDENTIFIANTS GOOGLE CLOUD :
    - Allez sur [Google Cloud Console](https://console.cloud.google.com)
    - Créez un nouveau projet
    - Activez \"Cloud Natural Language API\"
    - Créez une clé JSON de compte de service
    - Téléchargez et importez-la ici

    #### 2. ENTRER LE SITE WEB :
    - URL complète commençant par https://
    - Exemple : https://www.bbc.com

    #### 3. CONFIGURER :
    - **Pages max** : 5-50 (plus = plus lent)
    - **Profondeur** : 1-2 (niveaux du site)

    #### 4. LANCER ET ATTENDRE :
    - Suivez la barre de progression
    - Consultez le journal
    - Téléchargez le CSV à la fin

    ### 💡 CONSEILS :
    - Utilisez le mode \"Rapide\" pour tester
    - Les gros sites prennent plus de temps
    - Le CSV contient : URL, Entité, Importance, Type
    """,
        "settings_title": "### 📋 CONFIGURATION ACTUELLE :",
        "settings_change": "### 🔧 Modifier les paramètres :",
        "settings_change_steps": "1. Mettez à jour les valeurs dans la barre latérale\n2. Elles sont enregistrées au lancement",
        "config_location": "### 📁 Emplacement de config :",
        "loaded": "Chargés",
        "not_loaded": "Non chargés",
        "clear_session": "🗑️ Vider la session",
    },
    "ar": {
        "app_title": "مدقق كيانات SEO GEO",
        "sidebar_title": "🔍 أداة SEO المحلية",
        "sidebar_caption": "إعداد سريع وسهل",
        "language": "اللغة",
        "step1": "الخطوة 1: بيانات اعتماد Google",
        "upload_key": "📁 رفع مفتاح JSON",
        "creds_loaded": "✓ تم تحميل {name} (محفوظ كافتراضي)",
        "creds_ready": "✅ بيانات الاعتماد جاهزة",
        "creds_using": "المستخدم: {name}",
        "creds_missing": "❌ لم يتم تحميل بيانات اعتماد",
        "how_get_creds": "ℹ️ كيفية الحصول على بيانات الاعتماد",
        "how_get_creds_content": """
        **📖 كيفية الحصول على بيانات الاعتماد:**

        1. انتقل إلى: https://console.cloud.google.com
        2. أنشئ مشروعًا جديدًا
        3. ابحث عن \"Natural Language API\"
        4. قم بتفعيله
        5. اذهب إلى Credentials ← Create Service Account
        6. نزّل مفتاح JSON
        7. ارفعه هنا

        [مساعدة إضافية](https://cloud.google.com/natural-language/docs/quickstart)
        """,
        "step2": "الخطوة 2: الإعداد",
        "max_pages": "الحد الأقصى للصفحات:",
        "max_pages_help": "كلما زاد العدد زاد وقت التحليل",
        "max_depth": "عمق الزحف:",
        "max_depth_help": "مستويات بنية الموقع التي سيتم استكشافها",
        "quick_presets": "إعدادات سريعة",
        "preset_quick": "🏃 سريع (3 صفحات)",
        "preset_normal": "⚙️ عادي (10 صفحات)",
        "target_url": "رابط الموقع المستهدف:",
        "target_url_placeholder": "https://www.example.com",
        "target_url_help": "رابط كامل يبدأ بـ https://",
        "tab_analysis": "📊 التحليل",
        "tab_help": "ℹ️ المساعدة والنصائح",
        "tab_settings": "⚙️ الإعدادات",
        "launch_analysis": "▶ بدء التحليل",
        "load_creds_first": "⚠️ يرجى تحميل بيانات اعتماد Google Cloud JSON أولاً!",
        "enter_url": "⚠️ يرجى إدخال رابط الموقع!",
        "analysis_log": "سجل التحليل",
        "starting_crawl": "🚀 بدء الزحف إلى {url}...",
        "found_pages": "✓ تم العثور على {count} صفحات. بدء تحليل NLP...",
        "analyzing_step": "جاري التحليل {current}/{total}",
        "analyzing_url": "[{current}/{total}] تحليل: {url}",
        "entities_found": "  → تم العثور على {count} كيانات",
        "fetch_failed": "  → تعذر جلب المحتوى",
        "success_done": "✅ نجاح! اكتمل التحليل!",
        "success_total": "📊 إجمالي الكيانات: {count}",
        "success_banner": "✅ اكتمل التحليل! تم العثور على {count} كيانات",
        "summary": "📈 ملخص التحليل",
        "metric_total": "إجمالي الكيانات",
        "metric_unique": "الكيانات الفريدة",
        "metric_pages": "الصفحات المحللة",
        "metric_avg": "متوسط الأهمية",
        "viz": "📊 عرض البيانات",
        "filter": "🔍 التصفية والاستكشاف",
        "showing": "عرض {shown} من أصل {total} كيانات",
        "export": "💾 تصدير النتائج",
        "no_entities": "لم يتم العثور على كيانات. جرّب رابطًا آخر أو تحقق من المحتوى.",
        "error_prefix": "خطأ: {error}",
        "help_content": """
    ### 🎯 طريقة الاستخدام:

    #### 1. الحصول على بيانات اعتماد Google Cloud:
    - اذهب إلى [Google Cloud Console](https://console.cloud.google.com)
    - أنشئ مشروعًا جديدًا
    - فعّل \"Cloud Natural Language API\"
    - أنشئ مفتاح JSON لحساب الخدمة
    - نزّله ثم ارفعه هنا

    #### 2. إدخال الموقع:
    - رابط كامل يبدأ بـ https://
    - مثال: https://www.bbc.com

    #### 3. الإعداد:
    - **الحد الأقصى للصفحات**: من 5 إلى 50
    - **العمق**: من 1 إلى 2

    #### 4. ابدأ وانتظر:
    - راقب شريط التقدم
    - تابع سجل التحليل
    - نزّل ملف CSV عند الانتهاء

    ### 💡 نصائح:
    - استخدم الإعداد السريع للاختبار
    - المواقع الكبيرة تحتاج وقتًا أطول
    - CSV يحتوي: URL، الكيان، الأهمية، النوع
    """,
        "settings_title": "### 📋 الإعدادات الحالية:",
        "settings_change": "### 🔧 لتغيير الإعدادات:",
        "settings_change_steps": "1. حدّث القيم في الشريط الجانبي\n2. يتم حفظها تلقائيًا عند بدء التحليل",
        "config_location": "### 📁 مسار الإعدادات:",
        "loaded": "تم التحميل",
        "not_loaded": "غير محمّلة",
        "clear_session": "🗑️ مسح الجلسة",
    },
}


def t(key: str, **kwargs):
    lang = st.session_state.get("lang", "en")
    value = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        return value.format(**kwargs)
    return value

# --- Config & State ---
CONFIG_DIR = Path.home() / ".seo_crawler"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_CREDS_FILE = CONFIG_DIR / "credentials.json"
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


def apply_credentials(creds_path: Path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path)
    st.session_state.creds_uploaded = True
    st.session_state.creds_path = str(creds_path)


def apply_secrets_credentials():
    try:
        if "google" in st.secrets:
            st.session_state.creds_uploaded = True
            st.session_state.creds_path = "streamlit_secrets"
            return True
    except Exception:
        pass
    return False


@st.cache_resource
def get_language_client():
    service_account_info = None
    try:
        if "google" in st.secrets:
            service_account_info = dict(st.secrets["google"])
    except Exception:
        service_account_info = None

    if service_account_info:
        try:
            if "private_key" in service_account_info:
                service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")
            credentials = service_account.Credentials.from_service_account_info(service_account_info)
            return language_v1.LanguageServiceClient(credentials=credentials)
        except Exception as e:
            st.error(f"Google secrets configuration error: {e}")

    try:
        return language_v1.LanguageServiceClient()
    except Exception as e:
        st.error(f"Google NLP client initialization failed: {e}")
        return None


def try_auto_load_credentials():
    if st.session_state.creds_uploaded:
        return

    if apply_secrets_credentials():
        return

    config = load_config()
    candidates = []

    configured_path = config.get("creds_path")
    if configured_path:
        candidates.append(Path(configured_path).expanduser())

    candidates.extend([
        DEFAULT_CREDS_FILE,
        PROJECT_DIR / "credentials.json",
    ])

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            apply_credentials(candidate)
            config["creds_path"] = str(candidate)
            save_config(config)
            break


try_auto_load_credentials()

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
            client = get_language_client()
            if client is None:
                return []
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
    st.selectbox(
        "🌐 Language",
        options=["English", "Français", "العربية"],
        index={"en": 0, "fr": 1, "ar": 2}.get(st.session_state.lang, 0),
        key="language_selector"
    )

    selected_lang = {"English": "en", "Français": "fr", "العربية": "ar"}[st.session_state.language_selector]
    st.session_state.lang = selected_lang

    rtl = st.session_state.lang == "ar"
    text_align = "right" if rtl else "left"
    direction = "rtl" if rtl else "ltr"

    st.markdown(
        f"""
        <style>
            :root,
            [data-theme="light"],
            [data-theme="dark"] {{
                --text-color: #111111;
                --background-color: #ffffff;
                --secondary-background-color: #f7f7f7;
                --primary-color: #111111;
                color-scheme: light;
            }}
            .stApp {{
                background: #ffffff;
                color: #111111;
            }}
            .main .block-container {{
                max-width: 1160px;
                padding-top: 1.2rem;
                padding-bottom: 2rem;
            }}
            [data-testid="stSidebar"] {{
                background: #ffffff;
                border-right: 1px solid #efefef;
            }}
            [data-testid="stAppViewContainer"],
            [data-testid="stSidebar"],
            [data-testid="stHeader"],
            [data-testid="stToolbar"] {{
                background: #ffffff;
            }}
            .stApp,
            .stApp p,
            .stApp span,
            .stApp div,
            .stApp label,
            .stApp h1,
            .stApp h2,
            .stApp h3,
            .stApp h4,
            .stApp li,
            .stApp a {{
                color: #111111 !important;
            }}
            h1, h2, h3 {{
                letter-spacing: -0.01em;
                font-weight: 600;
            }}
            [data-testid="stMarkdownContainer"] *,
            [data-testid="stMetricLabel"],
            [data-testid="stMetricValue"],
            [data-testid="stMetricDelta"],
            [data-testid="stAlertContent"],
            [data-testid="stDataFrame"] * {{
                color: #111111 !important;
            }}
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] > div,
            .stMultiSelect div[data-baseweb="select"] > div,
            .stNumberInput input {{
                background: #ffffff !important;
                color: #111111 !important;
                border-color: #d9d9d9 !important;
                border-radius: 10px !important;
            }}
            .stTextArea textarea,
            .stTextArea textarea:disabled,
            textarea[disabled] {{
                color: #111111 !important;
                -webkit-text-fill-color: #111111 !important;
                opacity: 1 !important;
                background: #fcfcfc !important;
                border: 1px solid #e6e6e6 !important;
            }}
            .stTextInput input:focus,
            .stTextArea textarea:focus,
            .stSelectbox div[data-baseweb="select"] > div:focus-within,
            .stMultiSelect div[data-baseweb="select"] > div:focus-within {{
                border-color: #111111 !important;
                box-shadow: 0 0 0 1px #111111 inset !important;
            }}
            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder {{
                color: #666666 !important;
            }}
            div[data-baseweb="select"] *,
            div[data-baseweb="input"] *,
            div[data-baseweb="base-input"] * {{
                color: #111111 !important;
            }}
            .stButton > button,
            div[data-testid="stButton"] > button {{
                color: #ffffff !important;
                background: #111111 !important;
                border: 1px solid #111111 !important;
                border-radius: 10px !important;
                transition: all 0.18s ease;
                min-height: 42px;
                font-weight: 600;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
            }}
            .stButton > button *,
            div[data-testid="stButton"] > button * {{
                color: #ffffff !important;
                fill: #ffffff !important;
            }}
            .stDownloadButton > button {{
                color: #111111 !important;
                background: #ffffff !important;
                border: 1px solid #d9d9d9 !important;
                border-radius: 10px !important;
                transition: all 0.18s ease;
                min-height: 42px;
                font-weight: 600;
            }}
            .stButton > button:hover,
            div[data-testid="stButton"] > button:hover {{
                background: #000000 !important;
                border-color: #000000 !important;
                transform: translateY(-1px);
            }}
            .stDownloadButton > button:hover {{
                border-color: #111111 !important;
                transform: translateY(-1px);
            }}
            .stButton > button:disabled,
            div[data-testid="stButton"] > button:disabled {{
                background: #d9d9d9 !important;
                border-color: #d9d9d9 !important;
                color: #666666 !important;
                box-shadow: none !important;
            }}
            .stButton > button:disabled *,
            div[data-testid="stButton"] > button:disabled * {{
                color: #666666 !important;
                fill: #666666 !important;
            }}
            .stTabs [role="tab"] {{
                color: #111111 !important;
            }}
            div[data-testid="stMetricValue"] {{
                color: #111111;
            }}
            .block-container {{
                padding-top: 1.25rem;
            }}
            [data-testid="stMetric"] {{
                background: #fcfcfc;
                border: 1px solid #ececec;
                border-radius: 12px;
                padding: 0.65rem 0.75rem;
            }}
            .stApp,
            [data-testid="stSidebar"] {{
                direction: {direction};
                text-align: {text_align};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title(t("sidebar_title"))
    st.caption(t("sidebar_caption"))
    
    st.divider()
    
    # Step 1: Credentials
    st.subheader(t("step1"))
    
    uploaded_file = st.file_uploader(
        t("upload_key"),
        type="json",
        key="creds_upload"
    )
    
    if uploaded_file:
        # Save persistently for local default use
        with open(DEFAULT_CREDS_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        apply_credentials(DEFAULT_CREDS_FILE)
        config = load_config()
        config["creds_path"] = str(DEFAULT_CREDS_FILE)
        save_config(config)
        st.success(t("creds_loaded", name=uploaded_file.name))
    
    if st.session_state.creds_uploaded:
        st.markdown(t("creds_ready"))
        if st.session_state.creds_path:
            st.caption(t("creds_using", name=Path(st.session_state.creds_path).name))
    else:
        st.markdown(t("creds_missing"))
    
    if st.button(t("how_get_creds")):
        st.info(t("how_get_creds_content"))
    
    st.divider()
    
    # Step 2: Configure
    st.subheader(t("step2"))
    
    max_pages = st.slider(
        t("max_pages"),
        min_value=1,
        max_value=50,
        value=10,
        help=t("max_pages_help")
    )
    
    max_depth = st.slider(
        t("max_depth"),
        min_value=1,
        max_value=3,
        value=2,
        help=t("max_depth_help")
    )
    
    st.divider()
    
    # Presets
    st.subheader(t("quick_presets"))
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("preset_quick"), use_container_width=True):
            st.session_state.max_pages = 3
            st.session_state.max_depth = 1
            st.rerun()
    with col2:
        if st.button(t("preset_normal"), use_container_width=True):
            st.session_state.max_pages = 10
            st.session_state.max_depth = 2
            st.rerun()

# --- MAIN CONTENT ---
st.title(t("app_title"))

# URL Input
url_input = st.text_input(
    t("target_url"),
    placeholder=t("target_url_placeholder"),
    help=t("target_url_help")
)

# Tabs
tab_analysis, tab_help, tab_settings = st.tabs([t("tab_analysis"), t("tab_help"), t("tab_settings")])

with tab_analysis:
    if st.button(t("launch_analysis"), type="primary", use_container_width=True, key="launch_analysis_cta"):
        if not st.session_state.creds_uploaded:
            st.error(t("load_creds_first"))
        elif not url_input.strip():
            st.error(t("enter_url"))
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
                log_container.text_area(t("analysis_log"), value="\n".join(logs), height=300, disabled=True)
            
            log_message(t("starting_crawl", url=url) + "\n")
            
            try:
                # Crawl
                found_urls = SEOLogic.crawl(url, max_pages, max_depth, log_message)
                log_message("\n" + t("found_pages", count=len(found_urls)) + "\n")
                
                # Analyze
                results = []
                total = len(found_urls)
                
                for i, u in enumerate(found_urls):
                    status_text.text(t("analyzing_step", current=i + 1, total=total))
                    log_message(t("analyzing_url", current=i + 1, total=total, url=u))
                    
                    txt = SEOLogic.fetch_content(u)
                    if txt:
                        data = SEOLogic.analyze_entities(txt, u)
                        results.extend(data)
                        log_message(t("entities_found", count=len(data)))
                    else:
                        log_message(t("fetch_failed"))
                    
                    progress_bar.progress((i+1) / total)
                
                # Store results
                st.session_state.analysis_results = results
                
                if results:
                    log_message("\n" + t("success_done"))
                    log_message(t("success_total", count=len(results)))
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    log_container.empty()
                    
                    # Display success
                    st.success(t("success_banner", count=len(results)))
                    
                    # Show statistics
                    st.divider()
                    st.subheader(t("summary"))
                    
                    stats = get_statistics(results)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(t("metric_total"), stats['total_entities'])
                    with col2:
                        st.metric(t("metric_unique"), stats['unique_entities'])
                    with col3:
                        st.metric(t("metric_pages"), stats['pages_analyzed'])
                    with col4:
                        st.metric(t("metric_avg"), f"{stats['avg_salience']:.3f}")
                    
                    st.divider()
                    
                    # Visualizations
                    st.subheader(t("viz"))
                    
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
                    st.subheader(t("filter"))
                    filtered_df = create_entity_filter(results)
                    
                    if filtered_df is not None:
                        st.write(f"**{t('showing', shown=len(filtered_df), total=len(results))}**")
                        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    
                    # Export options
                    st.subheader(t("export"))
                    
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
                    log_message("\n" + t("no_entities"))
                    st.warning(t("no_entities"))
                    
            except Exception as e:
                log_message("\n" + t("error_prefix", error=e))
                st.error(t("error_prefix", error=e))

with tab_help:
    st.markdown(t("help_content"))

with tab_settings:
    st.markdown(f"""
    {t("settings_title")}
    
    - **{t("max_pages")}** {max_pages}
    - **{t("max_depth")}** {max_depth}
    - **Credentials**: {t("loaded") if st.session_state.creds_uploaded else t("not_loaded")}
    
    {t("settings_change")}
    {t("settings_change_steps")}
    
    {t("config_location")}
    `{CONFIG_DIR}`
    """)
    
    if st.button(t("clear_session")):
        st.session_state.clear()
        st.rerun()
