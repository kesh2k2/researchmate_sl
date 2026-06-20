import streamlit as st
import pandas as pd
import numpy as np
import re
import time
import io
from datetime import datetime

import pingouin as pg
import plotly.express as px
px.defaults.template = "plotly_white"
import statsmodels.api as sm

from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import het_breuschpagan


# ==========================================================
# APP CONFIG
# ==========================================================
st.set_page_config(
    page_title="ResearchMate SL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.45rem;
        font-weight: 900;
        margin-bottom: 0rem;
        letter-spacing: -0.5px;
    }

    .sub-title {
        font-size: 1rem;
        color: #666;
        margin-top: 0rem;
        margin-bottom: 0.7rem;
    }

    .dev-badge {
        padding: 0.65rem 0.9rem;
        border-radius: 0.9rem;
        background: linear-gradient(90deg, #f8f8ff, #eeeeff);
        border: 1px solid #dedcff;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .card {
        padding: 1.1rem;
        border-radius: 1rem;
        border: 1px solid #e6e6e6;
        background: #ffffff;
        box-shadow: 0px 2px 14px rgba(0,0,0,0.045);
        margin-bottom: 1rem;
    }

    .step-box {
        padding: 1rem;
        border-radius: 0.9rem;
        border-left: 5px solid #4f46e5;
        background: #f8f8ff;
        margin-bottom: 1rem;
    }

    .warning-box {
        padding: 1rem;
        border-radius: 0.9rem;
        border-left: 5px solid #f59e0b;
        background: #fffbeb;
        margin-bottom: 1rem;
    }

    .success-box {
        padding: 1rem;
        border-radius: 0.9rem;
        border-left: 5px solid #10b981;
        background: #ecfdf5;
        margin-bottom: 1rem;
    }

    .small-muted {
        color: #666;
        font-size: 0.92rem;
    }

    div.stButton > button:first-child {
        border-radius: 0.75rem;
        font-weight: 800;
        padding: 0.55rem 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================================
# DARK MODE + MOBILE VISIBILITY FIX
# ==========================================================
st.markdown("""
<style>
    /* Force app to stay readable even when phone/browser is in dark mode */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    .main,
    .block-container {
        background-color: #f8fbff !important;
        color: #0f172a !important;
    }

    /* Main text visibility */
    h1, h2, h3, h4, h5, h6,
    p, span, label, div,
    .stMarkdown,
    .stText,
    .stCaption,
    .stWrite {
        color: #0f172a !important;
    }

    /* Your custom boxes */
    .main-title {
        color: #0f172a !important;
    }

    .sub-title {
        color: #334155 !important;
    }

    .dev-badge {
        background: linear-gradient(90deg, #eff6ff, #ecfdf5) !important;
        border: 1px solid #bfdbfe !important;
        color: #0f172a !important;
    }

    .card {
        background: #ffffff !important;
        border: 1px solid #dbeafe !important;
        color: #0f172a !important;
    }

    .card h3,
    .card h4,
    .card p {
        color: #0f172a !important;
    }

    .step-box {
        background: #eff6ff !important;
        border-left: 5px solid #38bdf8 !important;
        color: #0f172a !important;
    }

    .warning-box {
        background: #fff7ed !important;
        border-left: 5px solid #f59e0b !important;
        color: #0f172a !important;
    }

    .success-box {
        background: #ecfdf5 !important;
        border-left: 5px solid #10b981 !important;
        color: #0f172a !important;
    }

    .small-muted {
        color: #475569 !important;
    }

    /* Sidebar visibility */
    [data-testid="stSidebar"] {
        background-color: #e0f2fe !important;
        color: #0f172a !important;
    }

    [data-testid="stSidebar"] * {
        color: #0f172a !important;
    }

    /* Inputs, multiselects, selectboxes, uploader */
    input,
    textarea,
    select,
    [data-baseweb="select"],
    [data-baseweb="base-input"],
    [data-baseweb="tag"],
    [data-testid="stFileUploader"],
    [data-testid="stTextInput"],
    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"],
    [data-testid="stNumberInput"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    [data-baseweb="tag"] {
        background-color: #bbf7d0 !important;
        color: #064e3b !important;
    }

    /* Buttons */
    div.stButton > button:first-child,
    .stDownloadButton > button {
        background-color: #38bdf8 !important;
        color: #ffffff !important;
        border: none !important;
    }

    div.stButton > button:first-child:hover,
    .stDownloadButton > button:hover {
        background-color: #0ea5e9 !important;
        color: #ffffff !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #dbeafe !important;
        border-radius: 14px !important;
        padding: 12px !important;
        color: #0f172a !important;
    }

    [data-testid="stMetric"] * {
        color: #0f172a !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        color: #0f172a !important;
    }

    [data-testid="stAlert"] * {
        color: #0f172a !important;
    }

    /* Tables/dataframes */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #dbeafe !important;
        border-radius: 12px !important;
    }

    [data-testid="stExpander"] * {
        color: #0f172a !important;
    }

    /* Plotly chart container */
    .js-plotly-plot,
    .plot-container,
    .svg-container {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    /* Mobile optimization */
    @media screen and (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }

        .main-title {
            font-size: 1.7rem !important;
            line-height: 1.2 !important;
        }

        .sub-title {
            font-size: 0.9rem !important;
        }

        .dev-badge,
        .card,
        .step-box,
        .warning-box,
        .success-box {
            padding: 0.85rem !important;
            border-radius: 0.75rem !important;
        }

        h1 {
            font-size: 1.55rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        h3 {
            font-size: 1.15rem !important;
        }

        p, span, label, div {
            font-size: 0.92rem !important;
        }

        [data-testid="stMetric"] {
            padding: 0.8rem !important;
        }

        div.stButton > button:first-child,
        .stDownloadButton > button {
            width: 100% !important;
        }
    }

    /* Explicit dark mode override */
    @media (prefers-color-scheme: dark) {
        .stApp,
        [data-testid="stAppViewContainer"],
        .main,
        .block-container {
            background-color: #f8fbff !important;
            color: #0f172a !important;
        }

        .card,
        .step-box,
        .dev-badge,
        [data-testid="stExpander"],
        [data-testid="stMetric"] {
            color: #0f172a !important;
        }

        .card *,
        .step-box *,
        .dev-badge *,
        [data-testid="stExpander"] *,
        [data-testid="stMetric"] * {
            color: #0f172a !important;
        }
    }
</style>
""", unsafe_allow_html=True)



# ==========================================================
# SESSION STATE
# ==========================================================
def init_session_state():
    defaults = {
        "df_work": None,
        "file_signature": None,
        "generated_variables": {},
        "summaries": [],
        "splash_loaded": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def show_splash_screen():
    if not st.session_state["splash_loaded"]:
        splash = st.empty()

        with splash.container():
            st.markdown("<div class='main-title'>📊 ResearchMate SL</div>", unsafe_allow_html=True)
            st.markdown("<div class='sub-title'>Sinhala-friendly Research Data Analysis Assistant</div>", unsafe_allow_html=True)
            st.markdown("<div class='dev-badge'>Developed by <b>Akesh De Jayathunga</b></div>", unsafe_allow_html=True)

            progress = st.progress(0, text="Application loading...")

            # Fast loading animation
            for i in range(0, 101, 10):
                time.sleep(0.25)
                progress.progress(i, text=f"Loading modules... {i}%")

        splash.empty()
        st.session_state["splash_loaded"] = True


def safe_var_name(name: str) -> str:
    cleaned = name.strip().lower()
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    if not cleaned:
        cleaned = "construct"

    return f"{cleaned}_mean"


def get_numeric_columns(df: pd.DataFrame) -> list:
    return df.select_dtypes(include=[np.number]).columns.tolist()


def get_generated_columns() -> list:
    if "generated_variables" not in st.session_state:
        return []

    return [
        col for col in st.session_state["generated_variables"].keys()
        if st.session_state["df_work"] is not None and col in st.session_state["df_work"].columns
    ]


def get_raw_numeric_columns(df: pd.DataFrame) -> list:
    generated_cols = get_generated_columns()
    return [col for col in get_numeric_columns(df) if col not in generated_cols]


def format_generated_column(col: str) -> str:
    meta = st.session_state["generated_variables"].get(col, {})
    construct = meta.get("construct", col)
    return f"{construct}  →  {col}"


def apply_reverse_coding(data: pd.DataFrame, reverse_items: list, likert_max: int) -> pd.DataFrame:
    data = data.copy()

    for col in reverse_items:
        if col in data.columns:
            data[col] = (likert_max + 1) - data[col]

    return data


def clean_numeric_data(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    data = df[cols].copy()

    for c in cols:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    return data.dropna()


def prepare_validity_data(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data = data.replace([np.inf, -np.inf], np.nan).dropna()

    constant_cols = [col for col in data.columns if data[col].nunique() <= 1]

    if constant_cols:
        data = data.drop(columns=constant_cols)

    if data.shape[1] < 3:
        raise ValueError(
            "Validity test එකට usable items 3ක්වත් ඕන. Constant / invalid columns remove වුණා."
        )

    if data.shape[0] < 5:
        raise ValueError(
            "Validity test එකට valid responses ප්‍රමාණය අඩුයි. Missing values check කරන්න."
        )

    return data


# ==========================================================
# MANUAL VALIDITY FUNCTIONS - NO factor_analyzer NEEDED
# ==========================================================
def calculate_kmo_manual(data: pd.DataFrame):
    corr = data.corr().values

    if not np.all(np.isfinite(corr)):
        raise ValueError("Correlation matrix එක valid නැහැ. Missing / constant columns check කරන්න.")

    inv_corr = np.linalg.pinv(corr)

    partial_corr = np.zeros_like(corr)

    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            if i == j:
                partial_corr[i, j] = 0
            else:
                denom = np.sqrt(inv_corr[i, i] * inv_corr[j, j])

                if denom == 0 or not np.isfinite(denom):
                    partial_corr[i, j] = 0
                else:
                    partial_corr[i, j] = -inv_corr[i, j] / denom

    corr_no_diag = corr.copy()
    np.fill_diagonal(corr_no_diag, 0)

    corr_sq = corr_no_diag ** 2
    partial_sq = partial_corr ** 2

    item_num = np.sum(corr_sq, axis=0)
    item_den = item_num + np.sum(partial_sq, axis=0)

    kmo_per_item = np.divide(
        item_num,
        item_den,
        out=np.zeros_like(item_num),
        where=item_den != 0
    )

    total_num = np.sum(corr_sq)
    total_den = total_num + np.sum(partial_sq)

    if total_den == 0:
        kmo_model = 0
    else:
        kmo_model = total_num / total_den

    return kmo_per_item, kmo_model


def calculate_bartlett_manual(data: pd.DataFrame):
    n, p = data.shape
    corr = data.corr().values

    sign, logdet = np.linalg.slogdet(corr)

    if sign <= 0 or not np.isfinite(logdet):
        det_corr = np.linalg.det(corr)

        if det_corr <= 0 or not np.isfinite(det_corr):
            det_corr = np.finfo(float).eps

        logdet = np.log(det_corr)

    chi_square = -(n - 1 - ((2 * p + 5) / 6)) * logdet
    df_bartlett = (p * (p - 1)) / 2
    p_value = stats.chi2.sf(chi_square, df_bartlett)

    return chi_square, p_value


def varimax_rotation(loadings, gamma=1.0, q=20, tol=1e-6):
    p, k = loadings.shape
    rotation_matrix = np.eye(k)
    previous_value = 0

    for _ in range(q):
        rotated_loadings = np.dot(loadings, rotation_matrix)

        u, s, vh = np.linalg.svd(
            np.dot(
                loadings.T,
                rotated_loadings ** 3 - (gamma / p) * np.dot(
                    rotated_loadings,
                    np.diag(np.diag(np.dot(rotated_loadings.T, rotated_loadings)))
                )
            )
        )

        rotation_matrix = np.dot(u, vh)
        current_value = np.sum(s)

        if previous_value != 0 and current_value / previous_value < 1 + tol:
            break

        previous_value = current_value

    return np.dot(loadings, rotation_matrix)


def efa_manual(data: pd.DataFrame, n_factors: int, rotation=True):
    corr = data.corr().values

    if not np.all(np.isfinite(corr)):
        raise ValueError("EFA සඳහා correlation matrix එක valid නැහැ.")

    eigen_values, eigen_vectors = np.linalg.eigh(corr)

    sorted_indices = np.argsort(eigen_values)[::-1]
    eigen_values = eigen_values[sorted_indices]
    eigen_vectors = eigen_vectors[:, sorted_indices]

    n_factors = min(n_factors, data.shape[1])

    selected_eigen_values = np.clip(eigen_values[:n_factors], a_min=0, a_max=None)
    selected_eigen_vectors = eigen_vectors[:, :n_factors]

    loadings = selected_eigen_vectors * np.sqrt(selected_eigen_values)

    if rotation and n_factors > 1:
        loadings = varimax_rotation(loadings)

    loadings_df = pd.DataFrame(
        loadings,
        index=data.columns,
        columns=[f"Factor {i+1}" for i in range(n_factors)]
    )

    return eigen_values, loadings_df


def create_mean_variable(df: pd.DataFrame, construct_name: str, items: list, reverse_items: list, likert_max: int) -> str:
    mean_col = safe_var_name(construct_name)

    data = df[items].copy()

    for c in items:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    data = apply_reverse_coding(data, reverse_items, likert_max)

    df[mean_col] = data.mean(axis=1)

    st.session_state["generated_variables"][mean_col] = {
        "construct": construct_name,
        "items": items,
        "reverse_items": reverse_items,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return mean_col


def reliability_label(alpha: float) -> tuple:
    if alpha >= 0.90:
        return (
            "Excellent Reliability ✅",
            "මේ scale එකේ Reliability එක ඉතාමත් හොඳයි. Items එකිනෙකට consistent විදිහට measure වෙලා තියෙනවා.",
            "success"
        )
    elif alpha >= 0.80:
        return (
            "Good Reliability ✅",
            "Reliability එක හොඳ මට්ටමක තියෙනවා. Research analysis සඳහා scale එක භාවිතා කරන්න සුදුසුයි.",
            "success"
        )
    elif alpha >= 0.70:
        return (
            "Acceptable Reliability ✅",
            "Cronbach’s Alpha value එක 0.70ට වැඩි නිසා Reliability එක acceptable. Analysis සඳහා භාවිතා කරන්න පුළුවන්.",
            "info"
        )
    elif alpha >= 0.60:
        return (
            "Questionable Reliability ⚠️",
            "Reliability එක ටිකක් අඩුයි. Reverse coding, confusing wording, weak items වගේ දේවල් check කරන්න.",
            "warning"
        )
    else:
        return (
            "Poor Reliability ❌",
            "Reliability එක acceptable level එකට නැහැ. Coding problems හෝ unrelated items තියෙන්න පුළුවන්.",
            "error"
        )


def kmo_label(kmo_value: float) -> tuple:
    if kmo_value >= 0.90:
        return "Excellent KMO ✅", "KMO value එක ඉතාමත් හොඳයි. Data එක Factor Analysis සඳහා ඉතාම suitable.", "success"
    elif kmo_value >= 0.80:
        return "Great KMO ✅", "KMO value එක හොඳ මට්ටමක තියෙනවා. Validity testing සඳහා data එක suitable.", "success"
    elif kmo_value >= 0.70:
        return "Good KMO ✅", "KMO value එක හොඳයි. Factor Analysis කරන්න පුළුවන්.", "success"
    elif kmo_value >= 0.60:
        return "Acceptable KMO ✅", "KMO value එක 0.60ට වැඩි නිසා Factor Analysis සඳහා acceptable.", "info"
    elif kmo_value >= 0.50:
        return "Weak KMO ⚠️", "KMO value එක weak. Items අතර relationship එක තව improve වෙන්න ඕන.", "warning"
    else:
        return "Poor KMO ❌", "KMO value එක 0.50ට අඩුයි. Factor Analysis සඳහා data එක suitable නැහැ.", "error"


def descriptive_level(mean_value: float) -> tuple:
    if mean_value <= 2.33:
        return "Low level", "අඩු මට්ටමක තියෙනවා"
    elif mean_value <= 3.66:
        return "Moderate level", "මධ්‍යස්ථ මට්ටමක තියෙනවා"
    else:
        return "High level", "ඉහළ මට්ටමක තියෙනවා"


def correlation_strength(r: float) -> str:
    abs_r = abs(r)

    if abs_r >= 0.70:
        return "strong"
    elif abs_r >= 0.40:
        return "moderate"
    elif abs_r >= 0.20:
        return "weak"
    else:
        return "very weak"


def show_status(status_type: str, title: str, message: str):
    if status_type == "success":
        st.success(title)
    elif status_type == "warning":
        st.warning(title)
    elif status_type == "error":
        st.error(title)
    else:
        st.info(title)

    st.write(message)


def build_construct_inputs(prefix: str, raw_numeric_cols: list, title: str):
    st.markdown(f"#### {title}")

    name = st.text_input(
        f"{title} name",
        key=f"{prefix}_name",
        placeholder="Example: Working Memory"
    )

    items = st.multiselect(
        f"{title} items select කරන්න",
        raw_numeric_cols,
        key=f"{prefix}_items"
    )

    reverse = st.multiselect(
        f"{title} reverse-coded items select කරන්න",
        items,
        key=f"{prefix}_reverse"
    )

    return name, items, reverse


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ResearchMate_Data")

    return output.getvalue()


def add_summary(test_name: str, title: str, summary_text: str, metrics: dict = None):
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_name": test_name,
        "title": title,
        "summary_text": summary_text,
        "metrics": metrics or {}
    }

    st.session_state["summaries"].append(entry)


def build_all_summaries_text() -> str:
    summaries = st.session_state.get("summaries", [])

    if not summaries:
        return "No summaries generated yet."

    parts = []
    parts.append("ResearchMate SL - Analysis Summary Report")
    parts.append("Developed by Akesh De Jayathunga")
    parts.append("=" * 60)

    for i, s in enumerate(summaries, start=1):
        parts.append(f"\n{i}. {s['test_name']} - {s['title']}")
        parts.append(f"Time: {s['time']}")

        if s["metrics"]:
            parts.append("Metrics:")
            for k, v in s["metrics"].items():
                parts.append(f"- {k}: {v}")

        parts.append("Interpretation:")
        parts.append(s["summary_text"])
        parts.append("-" * 60)

    return "\n".join(parts)


def display_latest_summary():
    summaries = st.session_state.get("summaries", [])

    if summaries:
        latest = summaries[-1]

        with st.expander("📌 Latest Test Summary", expanded=True):
            st.write(f"**{latest['test_name']} - {latest['title']}**")
            st.write(latest["summary_text"])

            st.download_button(
                "Download this summary as TXT",
                data=f"{latest['test_name']} - {latest['title']}\n\n{latest['summary_text']}",
                file_name=f"{latest['test_name'].lower().replace(' ', '_')}_summary.txt",
                mime="text/plain"
            )


def descriptive_guideline_box():
    guide_text = """
    **Descriptive Statistics use කරන නිවැරදි flow එක**

    1. ඔයාගේ variable / construct එකේ නම දාන්න.  
       Example: Working Memory

    2. ඒ variable එක measure කරන questionnaire items select කරන්න.  
       Example: WM_1, WM_2, WM_3, WM_4, WM_5, WM_6

    3. Reverse-coded items තියෙනවා නම් ඒවා select කරන්න.

    4. System එක automatically mean variable එකක් හදයි.  
       Example: Working Memory → working_memory_mean

    5. පස්සේ Correlation Analysis සහ Regression Analysis වලදී use කරන්න පුළුවන් වෙන්නේ මේ generated mean variables විතරයි.

    මේක SPSS එකේ Transform → Compute Variable කරනවා වගේමයි.
    """

    if hasattr(st, "popover"):
        with st.popover("📘 Descriptive Statistics use කරන විදිහ බලන්න"):
            st.markdown(guide_text)
    else:
        with st.expander("📘 Descriptive Statistics use කරන විදිහ බලන්න", expanded=True):
            st.markdown(guide_text)


# ==========================================================
# SPLASH SCREEN
# ==========================================================
show_splash_screen()


# ==========================================================
# HEADER
# ==========================================================
st.markdown("<div class='main-title'>📊 ResearchMate SL</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>SPSS-style Research Data Analysis with Sinhala Interpretation</div>", unsafe_allow_html=True)
st.markdown("<div class='dev-badge'>Developed by <b>Akesh De Jayathunga</b></div>", unsafe_allow_html=True)


# ==========================================================
# SIDEBAR
# ==========================================================
st.sidebar.title("📊 ResearchMate SL")
st.sidebar.caption("Sinhala-friendly analysis assistant")

page = st.sidebar.radio(
    "කරන්න ඕන Test එක තෝරන්න",
    [
        "Home",
        "Reliability Test",
        "Validity Test",
        "Descriptive Statistics",
        "Correlation Analysis",
        "Regression Analysis",
        "Generated Variables",
        "All Test Summaries"
    ]
)

st.sidebar.divider()

likert_max = st.sidebar.selectbox(
    "Likert scale maximum value",
    [5, 7],
    index=0
)

show_preview = st.sidebar.toggle(
    "Show uploaded data preview",
    value=True
)

st.sidebar.markdown("""
<div class='small-muted'>
Tip: 1 = Strongly Disagree, 5 = Strongly Agree වගේ coded data වලට මේ app එක work කරනවා.
</div>
""", unsafe_allow_html=True)


# ==========================================================
# FILE UPLOAD
# ==========================================================
uploaded_file = st.file_uploader(
    "Excel / CSV file එක upload කරන්න",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    try:
        file_signature = f"{uploaded_file.name}_{uploaded_file.size}"

        if st.session_state["file_signature"] != file_signature:
            with st.spinner("File එක load වෙනවා..."):
                if uploaded_file.name.lower().endswith(".csv"):
                    df_loaded = pd.read_csv(uploaded_file)
                else:
                    df_loaded = pd.read_excel(uploaded_file)

                st.session_state["df_work"] = df_loaded.copy()
                st.session_state["file_signature"] = file_signature
                st.session_state["generated_variables"] = {}
                st.session_state["summaries"] = []

        st.success("File එක successfully upload වුණා ✅")

    except Exception as e:
        st.error(f"File එක read කරන්න බැරි වුණා: {e}")

df = st.session_state["df_work"]

if df is not None and show_preview:
    with st.expander("Uploaded Data Preview", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])
        c3.metric("Numeric Columns", len(get_numeric_columns(df)))
        c4.metric("Generated Mean Variables", len(get_generated_columns()))


# ==========================================================
# HOME PAGE
# ==========================================================
if page == "Home":
    st.markdown("""
    <div class='card'>
        <h3>Welcome 👋</h3>
        <p>
        ResearchMate SL කියන්නේ SPSS output තේරුම් ගන්න අමාරු students ලාට Sinhala interpretation එක්ක
        research analysis කරගන්න හදපු assistant tool එකක්.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='card'>
            <h4>🔁 Reliability</h4>
            <p>Cronbach’s Alpha, item-total correlation, alpha if item deleted.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='card'>
            <h4>✅ Validity</h4>
            <p>KMO, Bartlett’s Test, EFA, factor loading suggestions.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='card'>
            <h4>📈 Regression</h4>
            <p>Multiple IVs, multiple DVs, hypothesis decisions, assumption checks.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='step-box'>
    <b>Recommended Workflow</b><br>
    1. Reliability Test → raw scale items select කරන්න<br>
    2. Validity Test → raw scale items select කරන්න<br>
    3. Descriptive Statistics → construct names + items select කරන්න. System එක mean variables හදයි<br>
    4. Correlation Analysis → generated mean variables විතරක් use කරන්න<br>
    5. Regression Analysis → generated mean variables විතරක් use කරන්න<br>
    6. All Test Summaries → final summary report එක ගන්න<br>
    </div>
    """, unsafe_allow_html=True)

    st.warning(
        "මෙය statistical guidance tool එකක්. Final research decision එක supervisor / lecturer guidance එක්ක verify කරන එක හොඳයි."
    )


# ==========================================================
# RELIABILITY TEST
# ==========================================================
elif page == "Reliability Test":
    st.subheader("🔁 Reliability Test - Cronbach’s Alpha")

    st.markdown("""
    <div class='step-box'>
    <b>Benchmark Values</b><br>
    0.90 or above → Excellent Reliability<br>
    0.80 - 0.89 → Good Reliability<br>
    0.70 - 0.79 → Acceptable Reliability<br>
    0.60 - 0.69 → Questionable Reliability<br>
    Below 0.60 → Poor Reliability<br><br>
    සාමාන්‍යයෙන් Cronbach’s Alpha value එක 0.70ට වැඩි නම් acceptable කියලා සලකන්න පුළුවන්.
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("මුලින් Excel / CSV file එක upload කරන්න.")

    else:
        raw_numeric_cols = get_raw_numeric_columns(df)

        selected_items = st.multiselect(
            "Reliability test එකට raw items select කරන්න",
            raw_numeric_cols
        )

        reverse_items = st.multiselect(
            "Reverse-coded items select කරන්න",
            selected_items
        )

        if st.button("Run Reliability Test", type="primary"):
            if len(selected_items) < 2:
                st.error("Reliability test එකට අඩුම තරමේ items 2ක්වත් select කරන්න.")

            else:
                try:
                    with st.spinner("Reliability test එක run වෙනවා..."):
                        data = clean_numeric_data(df, selected_items)
                        data = apply_reverse_coding(data, reverse_items, likert_max)

                        alpha, _ = pg.cronbach_alpha(data=data)
                        alpha = float(round(alpha, 3))

                        diagnostics = []
                        total_score = data.sum(axis=1)

                        for item in selected_items:
                            item_series = data[item]
                            total_without_item = total_score - item_series

                            try:
                                item_total_corr = item_series.corr(total_without_item)
                            except Exception:
                                item_total_corr = np.nan

                            if len(selected_items) > 2:
                                try:
                                    alpha_deleted, _ = pg.cronbach_alpha(
                                        data=data.drop(columns=[item])
                                    )
                                except Exception:
                                    alpha_deleted = np.nan
                            else:
                                alpha_deleted = np.nan

                            diagnostics.append({
                                "Item": item,
                                "Item-Total Correlation": round(item_total_corr, 3) if pd.notna(item_total_corr) else np.nan,
                                "Alpha if Item Deleted": round(alpha_deleted, 3) if pd.notna(alpha_deleted) else np.nan
                            })

                        diag_df = pd.DataFrame(diagnostics)

                    m1, m2 = st.columns(2)
                    m1.metric("Cronbach’s Alpha", alpha)
                    m2.metric("Valid Responses Used", data.shape[0])

                    title, msg, status_type = reliability_label(alpha)
                    show_status(status_type, title, msg)

                    st.subheader("Item Diagnostics")
                    st.dataframe(diag_df, use_container_width=True)

                    fig = px.bar(
                        diag_df,
                        x="Item",
                        y="Alpha if Item Deleted",
                        title="Alpha if Item Deleted"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    weak_items = diag_df[diag_df["Item-Total Correlation"] < 0.30]["Item"].tolist()
                    improve_items = diag_df[diag_df["Alpha if Item Deleted"] > alpha]["Item"].tolist()
                    negative_items = diag_df[diag_df["Item-Total Correlation"] < 0]["Item"].tolist()

                    st.subheader("Suggestions")

                    suggestions = []

                    if not weak_items and not improve_items and alpha >= 0.70:
                        st.success("Major issue එකක් detect වෙන්නේ නැහැ. Reliability එක acceptable / good මට්ටමක තියෙනවා.")
                        suggestions.append("Major issue එකක් detect වෙන්නේ නැහැ. Reliability එක acceptable / good මට්ටමක තියෙනවා.")
                    else:
                        if negative_items:
                            text = f"Negative item-total correlation තියෙන items: {', '.join(negative_items)}. Reverse coding හෝ item wording check කරන්න."
                            st.warning(text)
                            suggestions.append(text)

                        if weak_items:
                            text = f"Item-total correlation 0.30ට අඩු items: {', '.join(weak_items)}. මේ items weak වෙන්න පුළුවන්."
                            st.warning(text)
                            suggestions.append(text)

                        if improve_items:
                            text = f"මේ items remove කළාම alpha improve වෙන්න පුළුවන්: {', '.join(improve_items)}. Remove කිරීමට පෙර theory එක check කරන්න."
                            st.info(text)
                            suggestions.append(text)

                    summary_text = (
                        f"Cronbach’s Alpha value එක {alpha}. {msg} "
                        f"Valid responses {data.shape[0]}ක් use කරලා තියෙනවා. "
                        f"Suggestions: {' '.join(suggestions) if suggestions else 'No major suggestion.'}"
                    )

                    add_summary(
                        "Reliability Test",
                        "Cronbach’s Alpha",
                        summary_text,
                        metrics={
                            "Cronbach’s Alpha": alpha,
                            "Valid Responses": data.shape[0],
                            "Items": len(selected_items)
                        }
                    )

                    display_latest_summary()

                except Exception as e:
                    st.error(f"Reliability test එක run කරන්න බැරි වුණා: {e}")


# ==========================================================
# VALIDITY TEST
# ==========================================================
elif page == "Validity Test":
    st.subheader("✅ Validity Test - KMO, Bartlett’s Test & EFA")

    st.markdown("""
    <div class='step-box'>
    <b>Benchmarks</b><br>
    KMO ≥ 0.60 → Factor Analysis සඳහා acceptable<br>
    Bartlett’s Test p-value &lt; 0.05 → variables අතර meaningful relationship තියෙනවා<br>
    Factor Loading ≥ 0.40 → සාමාන්‍යයෙන් acceptable loading එකක් ලෙස ගන්න පුළුවන්
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("මුලින් Excel / CSV file එක upload කරන්න.")

    else:
        raw_numeric_cols = get_raw_numeric_columns(df)

        selected_items = st.multiselect(
            "Validity test එකට raw items select කරන්න",
            raw_numeric_cols
        )

        reverse_items = st.multiselect(
            "Reverse-coded items select කරන්න",
            selected_items
        )

        if len(selected_items) >= 3:
            max_factors = min(6, max(1, len(selected_items) - 1))

            if max_factors == 1:
                n_factors = 1
                st.info("Selected items ගණන අනුව EFA factor count එක 1 ලෙස set කරලා තියෙනවා.")
            else:
                n_factors = st.selectbox(
                    "EFA සඳහා factor count එක",
                    list(range(1, max_factors + 1)),
                    index=0
                )
        else:
            n_factors = 1
            st.info("Validity test එක run කරන්න අඩුම තරමේ items 3ක්වත් select කරන්න.")

        if st.button("Run Validity Test", type="primary"):
            if len(selected_items) < 3:
                st.error("Validity test එකට අඩුම තරමේ items 3ක්වත් select කරන්න.")

            else:
                try:
                    with st.spinner("Validity test එක run වෙනවා..."):
                        data = clean_numeric_data(df, selected_items)
                        data = apply_reverse_coding(data, reverse_items, likert_max)
                        data = prepare_validity_data(data)

                        kmo_all, kmo_model = calculate_kmo_manual(data)
                        chi_square_value, p_value = calculate_bartlett_manual(data)

                        eigen_values, loadings = efa_manual(
                            data=data,
                            n_factors=n_factors,
                            rotation=True
                        )

                        kmo_items_df = pd.DataFrame({
                            "Item": data.columns.tolist(),
                            "KMO per Item": np.round(kmo_all, 3)
                        })

                    c1, c2, c3 = st.columns(3)

                    c1.metric("KMO Value", round(float(kmo_model), 3))
                    c2.metric("Bartlett p-value", round(float(p_value), 4))
                    c3.metric("Chi-Square", round(float(chi_square_value), 3))

                    title, msg, status_type = kmo_label(float(kmo_model))
                    show_status(status_type, title, msg)

                    bartlett_message = ""

                    if p_value < 0.05:
                        bartlett_message = "Bartlett’s Test significant. p-value එක 0.05ට අඩු නිසා variables අතර meaningful relationship එකක් තියෙනවා."
                        st.success("Bartlett’s Test Significant ✅")
                        st.write(bartlett_message)
                    else:
                        bartlett_message = "Bartlett’s Test significant නැහැ. p-value එක 0.05ට වැඩි නිසා variables අතර relationship එක weak වෙන්න පුළුවන්."
                        st.error("Bartlett’s Test Not Significant ❌")
                        st.write(bartlett_message)

                    st.subheader("KMO per Item")
                    st.dataframe(kmo_items_df, use_container_width=True)

                    st.subheader("Scree Plot")

                    eigen_df = pd.DataFrame({
                        "Factor Number": list(range(1, len(eigen_values) + 1)),
                        "Eigenvalue": eigen_values
                    })

                    fig = px.line(
                        eigen_df,
                        x="Factor Number",
                        y="Eigenvalue",
                        markers=True,
                        title="Scree Plot / Eigenvalues"
                    )

                    fig.add_hline(y=1, line_dash="dash")
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Factor Loadings")
                    st.dataframe(loadings.round(3), use_container_width=True)

                    max_loading = loadings.abs().max(axis=1)
                    low_loading_items = max_loading[max_loading < 0.40].index.tolist()
                    weak_kmo_items = kmo_items_df[kmo_items_df["KMO per Item"] < 0.50]["Item"].tolist()

                    st.subheader("Suggestions")

                    suggestions = []

                    if kmo_model >= 0.60 and p_value < 0.05 and not low_loading_items and not weak_kmo_items:
                        text = "Validity indicators acceptable මට්ටමක තියෙනවා. Major issue එකක් detect වෙන්නේ නැහැ."
                        st.success(text)
                        suggestions.append(text)
                    else:
                        if kmo_model < 0.60:
                            text = "Overall KMO 0.60ට අඩුයි. Items අතර shared variance අඩු වෙන්න පුළුවන්."
                            st.warning(text)
                            suggestions.append(text)

                        if p_value >= 0.05:
                            text = "Bartlett’s Test significant නැහැ. Variables අතර correlation structure එක weak වෙන්න පුළුවන්."
                            st.warning(text)
                            suggestions.append(text)

                        if weak_kmo_items:
                            text = f"Low item KMO තියෙන items: {', '.join(weak_kmo_items)}"
                            st.info(text)
                            suggestions.append(text)

                        if low_loading_items:
                            text = f"Factor loading 0.40ට අඩු items: {', '.join(low_loading_items)}. Remove කිරීමට පෙර theory එක check කරන්න."
                            st.info(text)
                            suggestions.append(text)

                    summary_text = (
                        f"KMO value එක {round(float(kmo_model), 3)}. {msg} "
                        f"Bartlett p-value එක {round(float(p_value), 4)}. {bartlett_message} "
                        f"Suggestions: {' '.join(suggestions) if suggestions else 'No major suggestion.'}"
                    )

                    add_summary(
                        "Validity Test",
                        "KMO, Bartlett’s Test & EFA",
                        summary_text,
                        metrics={
                            "KMO": round(float(kmo_model), 3),
                            "Bartlett p-value": round(float(p_value), 4),
                            "Chi-Square": round(float(chi_square_value), 3),
                            "Factors": n_factors
                        }
                    )

                    display_latest_summary()

                except Exception as e:
                    st.error(f"Validity test එක run කරන්න බැරි වුණා: {e}")


# ==========================================================
# DESCRIPTIVE STATISTICS
# ==========================================================
elif page == "Descriptive Statistics":
    st.subheader("📌 Descriptive Statistics & Mean Variable Generation")

    descriptive_guideline_box()

    st.markdown("""
    <div class='step-box'>
    මෙතන raw questionnaire items select කළාම system එකම mean variable එකක් හදලා analysis කරයි.<br>
    Example: Working Memory → <b>working_memory_mean</b><br><br>
    මේ generated mean variables තමයි Correlation Analysis සහ Regression Analysis වලදී use වෙන්නේ.
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("මුලින් Excel / CSV file එක upload කරන්න.")

    else:
        raw_numeric_cols = get_raw_numeric_columns(df)

        if not raw_numeric_cols:
            st.error("Raw numeric questionnaire items detect වෙලා නැහැ.")

        else:
            number_of_constructs = st.number_input(
                "Analyze කරන්න variables / constructs ගණන",
                min_value=1,
                max_value=15,
                value=1,
                step=1
            )

            constructs = []

            for i in range(int(number_of_constructs)):
                with st.expander(f"Variable / Construct {i+1}", expanded=True):
                    name, items, reverse = build_construct_inputs(
                        f"desc_{i}",
                        raw_numeric_cols,
                        f"Construct {i+1}"
                    )
                    constructs.append((name, items, reverse))

            if st.button("Generate Mean Variables & Run Descriptive Statistics", type="primary"):
                has_error = False

                for name, items, reverse in constructs:
                    if not name:
                        st.error("හැම construct එකකටම name එකක් දාන්න.")
                        has_error = True

                    if len(items) < 2:
                        st.error(f"{name if name else 'Construct'} සඳහා අඩුම තරමේ items 2ක්වත් select කරන්න.")
                        has_error = True

                if not has_error:
                    try:
                        with st.spinner("Mean variables generate කරලා Descriptive Statistics run වෙනවා..."):
                            generated_cols = []

                            for name, items, reverse in constructs:
                                mean_col = create_mean_variable(
                                    df,
                                    name,
                                    items,
                                    reverse,
                                    likert_max
                                )
                                generated_cols.append((name, mean_col))

                            desc = df[[col for _, col in generated_cols]].describe().T[
                                ["mean", "std", "min", "max"]
                            ]

                            desc = desc.rename(columns={
                                "mean": "Mean",
                                "std": "Std. Deviation",
                                "min": "Minimum",
                                "max": "Maximum"
                            })

                        st.success("Mean variables system එකෙන් generate කරලා Descriptive Statistics run කළා ✅")

                        st.subheader("Generated Mean Variables")
                        gen_table = pd.DataFrame([
                            {
                                "Construct": name,
                                "Generated Variable": col,
                                "Items Used": ", ".join(st.session_state["generated_variables"][col]["items"]),
                                "Reverse Items": ", ".join(st.session_state["generated_variables"][col]["reverse_items"]) if st.session_state["generated_variables"][col]["reverse_items"] else "None"
                            }
                            for name, col in generated_cols
                        ])
                        st.dataframe(gen_table, use_container_width=True)

                        st.subheader("Descriptive Statistics")
                        st.dataframe(desc.round(3), use_container_width=True)

                        chart_df = desc.reset_index().rename(columns={"index": "Variable"})

                        fig = px.bar(
                            chart_df,
                            x="Variable",
                            y="Mean",
                            title="Mean Values by Construct"
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        st.subheader("Sinhala Interpretation")

                        interpretation_lines = []

                        for original_name, mean_col in generated_cols:
                            mean_val = float(desc.loc[mean_col, "Mean"])
                            sd_val = float(desc.loc[mean_col, "Std. Deviation"])
                            level, sinhala = descriptive_level(mean_val)

                            line = (
                                f"{original_name} සඳහා system generated variable එක {mean_col}. "
                                f"Mean value එක {mean_val:.2f}. Standard Deviation එක {sd_val:.2f}. "
                                f"ඒ නිසා මෙය {level} ලෙස සලකන්න පුළුවන්. "
                                f"සරලව කියනවා නම්, මේ variable එක {sinhala}."
                            )

                            interpretation_lines.append(line)
                            st.write(f"✅ **{line}**")

                        add_summary(
                            "Descriptive Statistics",
                            "Mean Variables & Descriptive Results",
                            " ".join(interpretation_lines),
                            metrics={
                                "Generated Variables": len(generated_cols)
                            }
                        )

                        display_latest_summary()

                        st.download_button(
                            "Download dataset with generated mean variables",
                            data=dataframe_to_excel_bytes(df),
                            file_name="researchmate_generated_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    except Exception as e:
                        st.error(f"Descriptive Statistics run කරන්න බැරි වුණා: {e}")


# ==========================================================
# CORRELATION ANALYSIS
# ==========================================================
elif page == "Correlation Analysis":
    st.subheader("🔗 Correlation Analysis")

    st.markdown("""
    <div class='step-box'>
    Correlation Analysis වලදී raw questionnaire items select කරන්න දෙන්නේ නැහැ.<br>
    Descriptive Statistics page එකෙන් generate කරපු mean variables විතරයි මෙතන use කරන්න පුළුවන්.<br><br>
    p-value &lt; 0.05 නම් relationship එක statistically significant ලෙස සලකන්න පුළුවන්.
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("මුලින් Excel / CSV file එක upload කරන්න.")

    else:
        generated_cols = get_generated_columns()

        if len(generated_cols) < 2:
            st.warning(
                "Correlation Analysis කරන්න අඩුම තරමේ generated mean variables 2ක්වත් ඕන. "
                "මුලින් Descriptive Statistics page එකෙන් variables generate කරන්න."
            )

        else:
            method = st.selectbox(
                "Correlation method",
                ["pearson", "spearman"],
                index=0
            )

            selected_vars = st.multiselect(
                "Correlation සඳහා generated mean variables select කරන්න",
                generated_cols,
                default=generated_cols[:2],
                format_func=format_generated_column
            )

            if st.button("Run Correlation Analysis", type="primary"):
                if len(selected_vars) < 2:
                    st.error("Correlation Analysis කරන්න අඩුම තරමේ generated variables 2ක් select කරන්න.")

                else:
                    try:
                        with st.spinner("Correlation Analysis run වෙනවා..."):
                            analysis_data = df[selected_vars].dropna()
                            corr_matrix = analysis_data.corr(method=method)

                            p_matrix = pd.DataFrame(
                                np.ones((len(selected_vars), len(selected_vars))),
                                columns=selected_vars,
                                index=selected_vars
                            )

                            for i, col_i in enumerate(selected_vars):
                                for j, col_j in enumerate(selected_vars):
                                    if i == j:
                                        p_matrix.loc[col_i, col_j] = 0.0
                                    else:
                                        if method == "pearson":
                                            _, p = stats.pearsonr(
                                                analysis_data[col_i],
                                                analysis_data[col_j]
                                            )
                                        else:
                                            _, p = stats.spearmanr(
                                                analysis_data[col_i],
                                                analysis_data[col_j]
                                            )

                                        p_matrix.loc[col_i, col_j] = p

                        st.success("Generated mean variables use කරලා Correlation Analysis run කළා ✅")

                        c1, c2 = st.columns(2)

                        with c1:
                            st.subheader("Correlation Matrix")
                            st.dataframe(corr_matrix.round(3), use_container_width=True)

                        with c2:
                            st.subheader("p-value Matrix")
                            st.dataframe(p_matrix.round(4), use_container_width=True)

                        fig = px.imshow(
                            corr_matrix,
                            text_auto=True,
                            title="Correlation Heatmap",
                            aspect="auto"
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        st.subheader("Sinhala Interpretation")

                        interpretation_lines = []

                        for i in range(len(selected_vars)):
                            for j in range(i + 1, len(selected_vars)):
                                col_i = selected_vars[i]
                                col_j = selected_vars[j]

                                name_i = st.session_state["generated_variables"][col_i]["construct"]
                                name_j = st.session_state["generated_variables"][col_j]["construct"]

                                r = float(corr_matrix.loc[col_i, col_j])
                                p = float(p_matrix.loc[col_i, col_j])

                                if r > 0:
                                    direction = "positive"
                                    direction_si = "එක variable එක වැඩි වෙද්දී අනෙක් variable එකත් වැඩි වෙන ප්‍රවණතාවයක් තියෙනවා"
                                elif r < 0:
                                    direction = "negative"
                                    direction_si = "එක variable එක වැඩි වෙද්දී අනෙක් variable එක අඩු වෙන ප්‍රවණතාවයක් තියෙනවා"
                                else:
                                    direction = "no"
                                    direction_si = "variables දෙක අතර පැහැදිලි relationship එකක් නැහැ"

                                strength = correlation_strength(r)
                                sig_text = "significant" if p < 0.05 else "not significant"
                                icon = "✅" if p < 0.05 else "⚠️"

                                line = (
                                    f"{name_i} සහ {name_j} අතර {method.title()} correlation value එක r = {r:.3f}. "
                                    f"මෙය {strength} {direction} relationship එකක්. "
                                    f"p-value = {p:.4f}. ඒ නිසා relationship එක {sig_text}. "
                                    f"{direction_si}."
                                )

                                interpretation_lines.append(line)
                                st.write(f"{icon} **{line}**")

                        add_summary(
                            "Correlation Analysis",
                            f"{method.title()} Correlation",
                            " ".join(interpretation_lines),
                            metrics={
                                "Method": method,
                                "Variables": len(selected_vars),
                                "Valid Responses": analysis_data.shape[0]
                            }
                        )

                        display_latest_summary()

                    except Exception as e:
                        st.error(f"Correlation Analysis run කරන්න බැරි වුණා: {e}")


# ==========================================================
# REGRESSION ANALYSIS
# ==========================================================
elif page == "Regression Analysis":
    st.subheader("📈 Regression Analysis")

    st.markdown("""
    <div class='step-box'>
    Regression Analysis වලදී raw questionnaire items select කරන්න දෙන්නේ නැහැ.<br>
    Descriptive Statistics page එකෙන් generate කරපු mean variables විතරයි use කරන්න පුළුවන්.<br><br>
    මේ version එක multiple dependent variables සහ multiple independent variables support කරනවා.
    Example: IV එකක් අඩුයි, DVs ගොඩක් තියෙන research එකකටත් suitable.
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("මුලින් Excel / CSV file එක upload කරන්න.")

    else:
        generated_cols = get_generated_columns()

        if len(generated_cols) < 2:
            st.warning(
                "Regression Analysis කරන්න අඩුම තරමේ generated mean variables 2ක්වත් ඕන. "
                "මුලින් Descriptive Statistics page එකෙන් variables generate කරන්න."
            )

        else:
            dv_cols = st.multiselect(
                "Dependent Variable(s) select කරන්න",
                generated_cols,
                format_func=format_generated_column
            )

            available_iv_cols = [c for c in generated_cols if c not in dv_cols]

            iv_cols = st.multiselect(
                "Independent Variable(s) select කරන්න",
                available_iv_cols,
                format_func=format_generated_column
            )

            if st.button("Run Regression Analysis", type="primary"):
                if not dv_cols:
                    st.error("අඩුම තරමේ dependent variable එකක් select කරන්න.")

                elif not iv_cols:
                    st.error("අඩුම තරමේ independent variable එකක් select කරන්න.")

                else:
                    try:
                        all_interpretations = []
                        all_coef_tables = []

                        for dv_col in dv_cols:
                            dv_name = st.session_state["generated_variables"][dv_col]["construct"]

                            reg_data = df[[dv_col] + iv_cols].dropna()

                            if reg_data.shape[0] <= len(iv_cols) + 1:
                                st.error(
                                    f"{dv_name} සඳහා valid responses ප්‍රමාණය regression predictors ගණනට වඩා අඩුයි. "
                                    f"Data rows check කරන්න."
                                )
                                continue

                            y = reg_data[dv_col]
                            X = sm.add_constant(reg_data[iv_cols])

                            with st.spinner(f"{dv_name} සඳහා regression model එක run වෙනවා..."):
                                model = sm.OLS(y, X).fit()
                                predictions = model.predict(X)
                                residuals = model.resid

                            st.markdown(f"---")
                            st.subheader(f"Regression Model for DV: {dv_name}")

                            c1, c2, c3, c4 = st.columns(4)

                            c1.metric("R-Squared", round(float(model.rsquared), 3))
                            c2.metric("Adjusted R-Squared", round(float(model.rsquared_adj), 3))
                            c3.metric("F p-value", round(float(model.f_pvalue), 4))
                            c4.metric("Valid Responses Used", int(reg_data.shape[0]))

                            coef_rows = []

                            coef_rows.append({
                                "DV": dv_name,
                                "IV": "Constant",
                                "Generated IV Column": "const",
                                "Beta": model.params["const"],
                                "p-value": model.pvalues["const"],
                                "Decision": ""
                            })

                            for iv_col in iv_cols:
                                iv_name = st.session_state["generated_variables"][iv_col]["construct"]
                                p_val = float(model.pvalues[iv_col])
                                beta = float(model.params[iv_col])

                                coef_rows.append({
                                    "DV": dv_name,
                                    "IV": iv_name,
                                    "Generated IV Column": iv_col,
                                    "Beta": beta,
                                    "p-value": p_val,
                                    "Decision": "Supported" if p_val < 0.05 else "Not Supported"
                                })

                            coef_df = pd.DataFrame(coef_rows)
                            all_coef_tables.append(coef_df)

                            st.subheader("Regression Coefficients")
                            st.dataframe(coef_df.round(4), use_container_width=True)

                            st.subheader("Hypothesis Interpretation")

                            for iv_col in iv_cols:
                                iv_name = st.session_state["generated_variables"][iv_col]["construct"]

                                beta = float(model.params[iv_col])
                                p_val = float(model.pvalues[iv_col])

                                if beta > 0:
                                    direction = "positive impact"
                                elif beta < 0:
                                    direction = "negative impact"
                                else:
                                    direction = "no clear impact"

                                if p_val < 0.05:
                                    st.success(f"{iv_name} → {dv_name}: Supported ✅")
                                    line = (
                                        f"{iv_name} variable එක {dv_name} variable එකට statistically significant "
                                        f"{direction} එකක් තියෙනවා. Beta = {beta:.3f}, p-value = {p_val:.4f}."
                                    )
                                else:
                                    st.error(f"{iv_name} → {dv_name}: Not Supported ❌")
                                    line = (
                                        f"{iv_name} variable එක {dv_name} variable එකට statistically significant impact එකක් "
                                        f"තියෙනවා කියලා කියන්න බැහැ. Beta = {beta:.3f}, p-value = {p_val:.4f}."
                                    )

                                st.write(line)
                                all_interpretations.append(line)

                            st.subheader("Charts")

                            pred_df = pd.DataFrame({
                                "Actual": y,
                                "Predicted": predictions,
                                "Residuals": residuals
                            })

                            fig_pred = px.scatter(
                                pred_df,
                                x="Predicted",
                                y="Actual",
                                title=f"Actual vs Predicted Values - {dv_name}"
                            )
                            st.plotly_chart(fig_pred, use_container_width=True)

                            fig_resid = px.histogram(
                                pred_df,
                                x="Residuals",
                                title=f"Residual Distribution - {dv_name}"
                            )
                            st.plotly_chart(fig_resid, use_container_width=True)

                            if len(iv_cols) == 1:
                                iv_name = st.session_state["generated_variables"][iv_cols[0]]["construct"]

                                scatter_df = reg_data[[iv_cols[0], dv_col]].copy()
                                scatter_df.columns = [iv_name, dv_name]

                                fig_scatter = px.scatter(
                                    scatter_df,
                                    x=iv_name,
                                    y=dv_name,
                                    trendline="ols",
                                    title=f"Regression Scatter Plot: {iv_name} → {dv_name}"
                                )

                                st.plotly_chart(fig_scatter, use_container_width=True)

                            st.subheader("Regression Assumption Checks")

                            assumption_rows = []

                            dw = durbin_watson(residuals)

                            assumption_rows.append({
                                "Assumption": "Independence of Errors",
                                "Test/Metric": "Durbin-Watson",
                                "Value": round(float(dw), 3),
                                "Guideline": "Around 1.5 - 2.5 is usually acceptable"
                            })

                            if reg_data.shape[0] <= 5000:
                                shapiro_stat, shapiro_p = stats.shapiro(residuals)

                                assumption_rows.append({
                                    "Assumption": "Residual Normality",
                                    "Test/Metric": "Shapiro-Wilk p-value",
                                    "Value": round(float(shapiro_p), 4),
                                    "Guideline": "p > 0.05 suggests residuals are approximately normal"
                                })

                            try:
                                bp_test = het_breuschpagan(residuals, X)

                                assumption_rows.append({
                                    "Assumption": "Homoscedasticity",
                                    "Test/Metric": "Breusch-Pagan p-value",
                                    "Value": round(float(bp_test[1]), 4),
                                    "Guideline": "p > 0.05 suggests constant variance"
                                })
                            except Exception:
                                assumption_rows.append({
                                    "Assumption": "Homoscedasticity",
                                    "Test/Metric": "Breusch-Pagan",
                                    "Value": "Could not calculate",
                                    "Guideline": "Check manually if needed"
                                })

                            st.dataframe(
                                pd.DataFrame(assumption_rows),
                                use_container_width=True
                            )

                            if len(iv_cols) > 1:
                                try:
                                    vif_rows = []
                                    X_no_const = reg_data[iv_cols]

                                    for i, col in enumerate(iv_cols):
                                        vif_rows.append({
                                            "Variable": st.session_state["generated_variables"][col]["construct"],
                                            "Generated Column": col,
                                            "VIF": variance_inflation_factor(X_no_const.values, i)
                                        })

                                    vif_df = pd.DataFrame(vif_rows)

                                    st.markdown("**Multicollinearity - VIF**")
                                    st.dataframe(vif_df.round(3), use_container_width=True)

                                    high_vif = vif_df[vif_df["VIF"] > 5]["Variable"].tolist()

                                    if high_vif:
                                        st.warning(
                                            f"High VIF detect වුණ variables: {', '.join(high_vif)}. "
                                            f"IVs අතර multicollinearity issue එකක් තියෙන්න පුළුවන්."
                                        )
                                    else:
                                        st.success("VIF values acceptable මට්ටමක තියෙනවා.")

                                except Exception as e:
                                    st.warning(f"VIF calculate කරන්න බැරි වුණා: {e}")

                            st.subheader("Model Sinhala Summary")

                            if model.f_pvalue < 0.05:
                                st.success("Overall regression model එක statistically significant ✅")
                                model_line = (
                                    f"{dv_name} සඳහා overall regression model එක statistically significant. "
                                    f"මෙම model එකෙන් {dv_name} variable එකේ variance එකෙන් {model.rsquared * 100:.1f}% පමණ explain කරනවා."
                                )
                            else:
                                st.warning("Overall regression model එක statistically significant නැහැ ⚠️")
                                model_line = (
                                    f"{dv_name} සඳහා overall regression model එක statistically significant නැහැ. "
                                    f"R-Squared value එක {model.rsquared:.3f}."
                                )

                            st.write(model_line)
                            all_interpretations.append(model_line)

                        if all_interpretations:
                            add_summary(
                                "Regression Analysis",
                                "Multiple DV / Multiple IV Regression",
                                " ".join(all_interpretations),
                                metrics={
                                    "DVs": len(dv_cols),
                                    "IVs": len(iv_cols)
                                }
                            )

                            display_latest_summary()

                        if all_coef_tables:
                            combined_coef = pd.concat(all_coef_tables, ignore_index=True)

                            csv_bytes = combined_coef.to_csv(index=False).encode("utf-8")

                            st.download_button(
                                "Download Regression Coefficients CSV",
                                data=csv_bytes,
                                file_name="researchmate_regression_coefficients.csv",
                                mime="text/csv"
                            )

                    except Exception as e:
                        st.error(f"Regression Analysis run කරන්න බැරි වුණා: {e}")


# ==========================================================
# GENERATED VARIABLES PAGE
# ==========================================================
elif page == "Generated Variables":
    st.subheader("🧮 Generated Mean Variables")

    if df is None:
        st.warning("මුලින් Excel / CSV file එක upload කරන්න.")

    else:
        generated = st.session_state.get("generated_variables", {})

        if not generated:
            st.info(
                "තවම generated mean variables නැහැ. Descriptive Statistics run කළාම variables මෙතන පෙන්වයි."
            )

        else:
            info_rows = []

            for col, meta in generated.items():
                if col in df.columns:
                    info_rows.append({
                        "Generated Variable": col,
                        "Construct": meta["construct"],
                        "Items": ", ".join(meta["items"]),
                        "Reverse Items": ", ".join(meta["reverse_items"]) if meta["reverse_items"] else "None",
                        "Created At": meta.get("created_at", "")
                    })

            st.dataframe(
                pd.DataFrame(info_rows),
                use_container_width=True
            )

            visible_cols = [c for c in generated.keys() if c in df.columns]

            if visible_cols:
                st.subheader("Generated Data Preview")
                st.dataframe(df[visible_cols].head(20), use_container_width=True)

                fig_df = df[visible_cols].mean().reset_index()
                fig_df.columns = ["Generated Variable", "Mean"]

                fig = px.bar(
                    fig_df,
                    x="Generated Variable",
                    y="Mean",
                    title="Generated Mean Variables Overview"
                )
                st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "Download dataset with generated variables",
                data=dataframe_to_excel_bytes(df),
                file_name="researchmate_generated_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# ==========================================================
# ALL TEST SUMMARIES PAGE
# ==========================================================
elif page == "All Test Summaries":
    st.subheader("📋 All Test Summaries")

    summaries = st.session_state.get("summaries", [])

    if not summaries:
        st.info("තවම summaries generate වෙලා නැහැ. Tests run කළාම මෙතන summaries පෙන්වයි.")

    else:
        st.success(f"Generated summaries: {len(summaries)}")

        for i, s in enumerate(summaries, start=1):
            with st.expander(f"{i}. {s['test_name']} - {s['title']} ({s['time']})", expanded=False):
                if s["metrics"]:
                    st.markdown("**Metrics**")
                    st.json(s["metrics"])

                st.markdown("**Sinhala Interpretation / Summary**")
                st.write(s["summary_text"])

        report_text = build_all_summaries_text()

        st.download_button(
            "Download Full Summary Report as TXT",
            data=report_text,
            file_name="researchmate_full_summary_report.txt",
            mime="text/plain"
        )

        summary_rows = []

        for s in summaries:
            row = {
                "Time": s["time"],
                "Test": s["test_name"],
                "Title": s["title"],
                "Summary": s["summary_text"]
            }

            for k, v in s["metrics"].items():
                row[k] = v

            summary_rows.append(row)

        summary_df = pd.DataFrame(summary_rows)

        st.download_button(
            "Download Summary Table as CSV",
            data=summary_df.to_csv(index=False).encode("utf-8"),
            file_name="researchmate_summary_table.csv",
            mime="text/csv"
        )