import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import datetime
import streamlit.components.v1 as components
from openai import OpenAI

# ----------------------------------------------------------
#  PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title="Basket Range Analysis",
    page_icon="📊",
    layout="wide",
)

def login_page():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return

    # ---------------------- CSS ----------------------
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

        /* ANIMATED BACKGROUND */
        .stApp {
            background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #0f172a);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Hide standard elements */
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Title Styling */
        .login-title {
            font-family: 'Outfit', sans-serif;
            font-size: 3.5rem;
            font-weight: 800;
            text-align: center;
            background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            line-height: 1.1;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
        }
        
        .login-subtitle {
            font-family: 'Outfit', sans-serif;
            font-size: 1.1rem;
            color: #cbd5e1;
            text-align: center;
            margin-bottom: 2.5rem;
            font-weight: 400;
            letter-spacing: 0.5px;
        }

        /* GLASSMORPHISM FORM CONTAINER */
        [data-testid="stForm"] {
            background: rgba(30, 41, 59, 0.3);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        
        /* Button Styling */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: white !important;
            border: none !important;
            padding: 14px 24px !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            margin-top: 15px;
            letter-spacing: 0.5px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
            filter: brightness(1.1);
        }
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Error message */
        .stAlert {
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #fca5a5;
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------------------- LAYOUT ----------------------
    # Use columns to center content: [Empty, Content, Empty]
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Spacer to push content down slightly
        st.markdown('<div style="height: 15vh;"></div>', unsafe_allow_html=True)
        
        # Title & Subtitle
        st.markdown('<div class="login-title">Basket Range<br>Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">เข้าสู่ระบบเพื่อเริ่มต้นใช้งาน</div>', unsafe_allow_html=True)
        
        # Nested columns to make the form more compact
        # Adjust ratios to match the title width roughly
        c1, c2, c3 = st.columns([1, 2, 1])
        
        with c2:
            # Login Form
            with st.form("login_form"):
                password = st.text_input("Password", type="password", placeholder="ใส่รหัสผ่าน", label_visibility="collapsed")
                submit = st.form_submit_button("เข้าสู่ระบบ")
            
            if submit:
                if password == st.secrets.get("APP_PASSWORD", ""):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Incorrect password")

    st.stop()



# ----------------------------------------------------------
#   Call Login First
# ----------------------------------------------------------
login_page()


# ----------------------------------------------------------
#  GLOBAL STYLE (Dark Professional BI Theme)
# ----------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #020617; /* slate-950 */
        color: #e5e7eb;
    }

    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f9fafb;
        margin-bottom: 0.1rem;
    }

    .sub-header {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-bottom: 1.2rem;
    }

    /* Filter label */
    .stMarkdown h3 {
        color: #e5e7eb;
    }

    /* Run button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #22c55e);
        color: #f9fafb;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 999px;
        font-weight: 600;
        box-shadow: 0 8px 18px rgba(37,99,235,0.35);
        cursor: pointer;
        transition: all 0.15s ease-out;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 24px rgba(37,99,235,0.5);
    }

    /* AI box */
    .ai-summary-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 16px;
        border: 1px solid #334155;
        padding: 1.5rem;
        margin-top: 0.2rem;
        color: #e5e7eb;
        box-shadow: 0 16px 35px rgba(15,23,42,0.7);
        word-wrap: break-word;
        overflow-wrap: break-word;
        overflow: hidden;
    }

    .ai-title {
        color: #38bdf8;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        border-bottom: 2px solid #334155;
        padding-bottom: 0.75rem;
    }
    .ai-title span.icon {
        font-size: 1.3rem;
    }
    .ai-content {
        line-height: 1.8;
        color: #cbd5e1;
        max-width: 100%;
        overflow-wrap: break-word;
        word-break: break-word;
    }
    .ai-content h4 {
        color: #22c55e;
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .ai-content ul {
        margin-left: 1.2rem;
        margin-top: 0.3rem;
    }
    .ai-content li {
        margin-bottom: 0.4rem;
        word-wrap: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------
#  HEADER
# ----------------------------------------------------------
st.markdown('<div class="main-header">📊 Basket Range Analysis</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">วิเคราะห์ยอดขายตามช่วงตะกร้า (Basket Range) เปรียบเทียบช่วงเวลาเดียวกันปีที่แล้ว (SPLY)</div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------
#  FILTER PANEL
# ----------------------------------------------------------
with st.container():
    st.markdown("### 🏷️ Filters")
    st.markdown(
        '<div style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 0.8rem;">'
        '<i>💡 Tip: แยกหลายค่าโดยใช้เครื่องหมาย comma (,) เช่น: TOOTHPASTE, LIQUID SOAP</i>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Row 1: Dates
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.date(2025, 1, 1))
    with col2:
        end_date = st.date_input("End Date", datetime.date(2025, 1, 1))
    
    # Row 2: Filters
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        supplier_code = st.text_input("Supplier Code(s)", "")
    with col4:
        category = st.text_input("Category Name(s)", "")
    with col5:
        subcategory = st.text_input("Sub-Category Name(s)", "")
    with col6:
        brand = st.text_input("Brand Name(s)", "")

    run_btn = st.button("🚀 Run Analysis")

# ----------------------------------------------------------
#  BIGQUERY CLIENT (STREAMLIT CLOUD VERSION WITH ERROR HANDLING)
# ----------------------------------------------------------
@st.cache_resource
def get_bq_client():
    """Get BigQuery client using st.secrets"""
    try:
        # Check if secrets exist
        if "gcp_service_account" not in st.secrets:
            st.error("❌ Missing 'gcp_service_account' in Streamlit secrets")
            st.info("ℹ️ Please add BigQuery credentials in App Settings → Secrets")
            return None
        
        creds_info = st.secrets["gcp_service_account"]
        
        # Validate required fields
        required_fields = ["type", "project_id", "private_key", "client_email"]
        missing_fields = [f for f in required_fields if f not in creds_info]
        if missing_fields:
            st.error(f"❌ Missing fields in gcp_service_account: {missing_fields}")
            return None
        
        credentials = service_account.Credentials.from_service_account_info(creds_info)
        client = bigquery.Client(credentials=credentials, project=creds_info["project_id"])
        return client
        
    except KeyError as e:
        st.error(f"❌ Missing key in secrets: {e}")
        st.info("ℹ️ Check your secrets.toml format in App Settings")
        return None
    except Exception as e:
        st.error(f"❌ BigQuery client error: {type(e).__name__}: {e}")
        st.info("ℹ️ Check if private_key format is correct (should use \\n for newlines)")
        return None

# ----------------------------------------------------------
#  RUN QUERY
# ----------------------------------------------------------
def build_array_literal(values):
    cleaned = [v.strip() for v in values if v.strip() != ""]
    if not cleaned:
        return "[]"
    joined = ",".join(f"'{v}'" for v in cleaned)
    return f"[{joined}]"

def run_query(client, start_date, end_date, supplier_code, category, subcategory, brand):
    start_sply = start_date.replace(year=start_date.year - 1)
    end_sply = end_date.replace(year=end_date.year - 1)

    supplier_codes = supplier_code.split(",") if supplier_code else []
    categories = category.split(",") if category else []
    subcategories = subcategory.split(",") if subcategory else []
    brands = brand.split(",") if brand else []

    supplier_array = build_array_literal(supplier_codes)
    cat_array = build_array_literal(categories)
    subcat_array = build_array_literal(subcategories)
    brand_array = build_array_literal(brands)

    query = f"""
    DECLARE start_2024 DATE DEFAULT '{start_sply}';
    DECLARE end_2024   DATE DEFAULT '{end_sply}';
    DECLARE start_2025 DATE DEFAULT '{start_date}';
    DECLARE end_2025   DATE DEFAULT '{end_date}';

    DECLARE v_supplier_code ARRAY<STRING>;
    DECLARE v_category ARRAY<STRING>;
    DECLARE v_subcategory ARRAY<STRING>;
    DECLARE v_brand ARRAY<STRING>;

    SET v_supplier_code = {supplier_array};
    SET v_category = {cat_array};
    SET v_subcategory = {subcat_array};
    SET v_brand = {brand_array};

    WITH base AS (
        SELECT
            EXTRACT(YEAR FROM a.Date) AS Year,
            a.Date,
            a.DocNo,
            a.CustomerCode,
            COALESCE(a.SaleIncVat,0) AS SaleIncVat,
            ROW_NUMBER() OVER(PARTITION BY a.DocNo) AS BillFlag,
            ROW_NUMBER() OVER(PARTITION BY a.CustomerCode) AS CustFlag
        FROM `commercial-prod-375618.pcb_data_prod.PCB_DATABASE_NFKDB` a
        LEFT JOIN `commercial-prod-375618.pcb_data_prod.PCB_PRODUCT_MASTER` b
            ON a.Barcode = b.Barcode
        WHERE
            (ARRAY_LENGTH(v_supplier_code) = 0 OR b.SupplierCode IN UNNEST(v_supplier_code))
            AND (ARRAY_LENGTH(v_category) = 0 OR b.CategoryName IN UNNEST(v_category))
            AND (ARRAY_LENGTH(v_subcategory) = 0 OR b.SubCategoryName IN UNNEST(v_subcategory))
            AND (ARRAY_LENGTH(v_brand) = 0 OR b.Brand IN UNNEST(v_brand))
            AND (
                a.Date BETWEEN start_2024 AND end_2024
                OR a.Date BETWEEN start_2025 AND end_2025
            )
    ),

    BasketSizeRanges AS (
        SELECT
            Year,
            Date,
            DocNo,
            SUM(SaleIncVat) AS total_sales,
            SUM(CASE WHEN BillFlag = 1 THEN 1 ELSE 0 END) AS Bills,
            SUM(CASE WHEN CustFlag = 1 THEN 1 ELSE 0 END) AS Members,
            CASE
                WHEN SUM(SaleIncVat) < 49 THEN '< 49'
                WHEN SUM(SaleIncVat) BETWEEN 49 AND 98 THEN '49 - 98'
                WHEN SUM(SaleIncVat) BETWEEN 99 AND 148 THEN '99 - 148'
                WHEN SUM(SaleIncVat) BETWEEN 149 AND 198 THEN '149 - 198'
                WHEN SUM(SaleIncVat) BETWEEN 199 AND 248 THEN '199 - 248'
                WHEN SUM(SaleIncVat) BETWEEN 249 AND 298 THEN '249 - 298'
                WHEN SUM(SaleIncVat) BETWEEN 299 AND 348 THEN '299 - 348'
                WHEN SUM(SaleIncVat) BETWEEN 349 AND 398 THEN '349 - 398'
                WHEN SUM(SaleIncVat) BETWEEN 399 AND 448 THEN '399 - 448'
                WHEN SUM(SaleIncVat) BETWEEN 449 AND 498 THEN '449 - 498'
                WHEN SUM(SaleIncVat) BETWEEN 499 AND 548 THEN '499 - 548'
                WHEN SUM(SaleIncVat) BETWEEN 549 AND 598 THEN '549 - 598'
                WHEN SUM(SaleIncVat) BETWEEN 599 AND 648 THEN '599 - 648'
                WHEN SUM(SaleIncVat) BETWEEN 649 AND 698 THEN '649 - 698'
                ELSE '>= 699'
            END AS Basket_Range
        FROM base
        GROUP BY 1,2,3
    ),

    summary AS (
        SELECT
            Year,
            Basket_Range,
            AVG(total_sales) AS ABR,
            SUM(total_sales) AS TotalSales,
            SUM(Bills) AS TotalBills,
            SUM(Members) AS TotalMembers
        FROM BasketSizeRanges
        GROUP BY 1,2
    )

    SELECT * FROM summary
    ORDER BY Basket_Range;
    """

    return client.query(query).to_dataframe()

# ----------------------------------------------------------
#  FILTER METADATA QUERY
# ----------------------------------------------------------
def get_filter_metadata(client, supplier_code, category, subcategory, brand):
    """Fetch metadata about the filters to show confirmation"""
    supplier_codes = supplier_code.split(",") if supplier_code else []
    categories = category.split(",") if category else []
    subcategories = subcategory.split(",") if subcategory else []
    brands = brand.split(",") if brand else []

    supplier_array = build_array_literal(supplier_codes)
    cat_array = build_array_literal(categories)
    subcat_array = build_array_literal(subcategories)
    brand_array = build_array_literal(brands)

    query = f"""
    DECLARE v_supplier_code ARRAY<STRING>;
    DECLARE v_category ARRAY<STRING>;
    DECLARE v_subcategory ARRAY<STRING>;
    DECLARE v_brand ARRAY<STRING>;

    SET v_supplier_code = {supplier_array};
    SET v_category = {cat_array};
    SET v_subcategory = {subcat_array};
    SET v_brand = {brand_array};

    SELECT
        STRING_AGG(DISTINCT SupplierName, ', ') AS SupplierNames,
        STRING_AGG(DISTINCT CONCAT(SupplierCode, ' (', SupplierName, ')'), ', ') AS SupplierDetails,
        STRING_AGG(DISTINCT CategoryName, ', ') AS Categories,
        STRING_AGG(DISTINCT SubCategoryName, ', ') AS SubCategories,
        STRING_AGG(DISTINCT Brand, ', ') AS Brands,
        COUNT(DISTINCT Barcode) AS ProductCount
    FROM `commercial-prod-375618.pcb_data_prod.PCB_PRODUCT_MASTER`
    WHERE
        (ARRAY_LENGTH(v_supplier_code) = 0 OR SupplierCode IN UNNEST(v_supplier_code))
        AND (ARRAY_LENGTH(v_category) = 0 OR CategoryName IN UNNEST(v_category))
        AND (ARRAY_LENGTH(v_subcategory) = 0 OR SubCategoryName IN UNNEST(v_subcategory))
        AND (ARRAY_LENGTH(v_brand) = 0 OR Brand IN UNNEST(v_brand))
    """

    result = client.query(query).to_dataframe()
    if len(result) > 0:
        return result.iloc[0].to_dict()
    return {}

# ----------------------------------------------------------
#  AI INSIGHT
# ----------------------------------------------------------
def generate_ai_insight(df, category, brand):
    try:
        if "OPENAI_API_KEY" not in st.secrets:
            return "⚠️ Missing 'OPENAI_API_KEY' in Streamlit secrets"
        
        api_key = st.secrets["OPENAI_API_KEY"]
        if not api_key or api_key.strip() == "":
            return "⚠️ OPENAI_API_KEY is empty"
            
    except Exception as e:
        return f"⚠️ Error accessing OPENAI_API_KEY: {e}"

    client = OpenAI(api_key=api_key)

    lean_df = df.groupby(["Year", "Basket_Range"]).agg(
        TotalSales=("TotalSales", "sum"),
        TotalBills=("TotalBills", "sum"),
        TotalMembers=("TotalMembers", "sum"),
        ABR=("ABR", "mean")
    ).reset_index()

    prompt = f"""
    บทบาทของคุณ
    คุณคือ Business Data Analyst ที่แม่นยำเรื่อง logic และใช้ภาษาพูดเข้าใจง่าย
    หน้าที่คือสรุป Insight / Action จาก Basket Range สำหรับ Category = {category}, Brand = {brand}

    Data (ใช้ตารางนี้เท่านั้น ห้ามเดาตัวเลขเพิ่มเอง):
    {lean_df.to_string(index=False)}

    --------------------------------
    กติกาการใช้ข้อมูล

    1) เรื่องช่วงเวลา
    - ตารางนี้มี 2 ฝั่ง: SPLY = ปีก่อน, CURRENT = ปีนี้
    - เวลาพูดถึงปี ให้ใช้คำว่า "ปีก่อน (SPLY)" และ "ปีนี้ (CURRENT)" เท่านั้น
    - ถ้าในข้อมูลไม่มีเลขปีชัดเจน ห้ามเดาเลขปีเองเด็ดขาด ห้ามเขียน 2023, 2024, 2025 เอง

    2) นิยามสำคัญ
    - Hero Range = Basket Range ที่มี % SHARE SALES ของปีนี้ (CURRENT) สูงที่สุด
    - Traffic Generator = Basket Range ที่ "ต่ำกว่า Hero Range" และมี % SHARE BILLS ของปีนี้สูง
    - เป้าหมายหลักคือดันลูกค้าจาก Traffic -> Hero และจาก Hero ->ช่วงที่สูงกว่า Hero
    - ห้ามเสนอให้ลูกค้าลดการใช้จ่ายลงไปช่วงราคาที่ต่ำกว่าเดิม

    3) ตัวเลขและหน่วย
    - ยอดขายให้เขียนเป็นหน่วย M THB เช่น 23.9M THB (ปัดทศนิยม 1 ตำแหน่ง)
    - จำนวนบิลให้เขียนเป็น K Bills หรือ M Bills เช่น 145.9K Bills หรือ 1.4M Bills
    - ไม่ต้องแสดงตัวเลขละเอียดทุกจุด เอาแค่ระดับที่เล่าเรื่องได้

    4) สไตล์คำอธิบาย
    - ใช้ภาษาพูดง่าย ๆ เหมือนอธิบายให้คนการตลาดฟัง ไม่ต้องภาษาวิชาการ
    - เน้นสั้น กระชับ เข้าใจง่าย และไปสู่ Action ได้จริง
    - ห้ามใช้ Markdown format ใด ๆ นอกจากหัวข้อและ bullet ตามแบบด้านล่าง
    - ห้ามใช้ตัวหนา ห้ามใช้ตัวเอียง ห้ามใช้สัญลักษณ์ *, **, _, หรือ # เพิ่มเติมนอกเหนือจากที่กำหนด
    ถ้าจะใช้ # ได้เฉพาะขึ้นต้นบรรทัดหัวข้อ "#### Insight", "#### Action", "#### Suggest Basket Size" เท่านั้น

    --------------------------------
    รูปแบบคำตอบ (ต้องใช้โครงนี้เท่านั้น)

    ให้ตอบเป็นภาษาไทย โดยใช้โครงสร้างนี้แบบเป๊ะ ๆ แล้วเติมเนื้อหาต่อท้ายแต่ละบรรทัด
    ห้ามเพิ่มบรรทัดหัวข้ออื่น ห้ามเปลี่ยนข้อความหัวข้อ

    #### Insight
    - Hero Range: อธิบายช่วงราคาไหน ยอดขายประมาณกี่ M THB และคิดเป็นกี่เปอร์เซ็นต์ของยอดขายทั้งหมด
    - Traffic Generator: อธิบายช่วงราคาไหน จำนวนบิลประมาณกี่ K/M Bills และคิดเป็นกี่เปอร์เซ็นต์ของบิลทั้งหมด
    - การเปลี่ยนแปลง: เปรียบเทียบ Hero Range ปีนี้เทียบกับปีก่อน (SPLY) ว่ายอดขายเพิ่มหรือลดประมาณกี่ M THB และมองว่าลูกค้ากองอยู่ช่วงไหนหรือเริ่มขยับขึ้นหรือยัง

    #### Action
    - Action 1 - แนวทางเปลี่ยนลูกค้ากลุ่ม Traffic Generator ให้ปิดบิลขึ้นมาที่ Hero Range (เช่น โปรเติมเงินอีกเล็กน้อยแล้วได้ของแถมหรือส่วนลด)
    - Action 2 - แนวทางดันลูกค้า Hero Range ให้ขยับไปช่วงราคาที่สูงกว่าถัดไป (เช่น จัด bundle หรือ GWP เมื่อยอดถึงช่วงถัดไป)
    - เพิ่มรายละเอียดแต่ละ Action ให้ชัดพอที่ทีมการตลาดเอาไปออกแบบโปรโมชันต่อได้

    #### Suggest Basket Size
    - ตัวเลขที่แนะนำสำหรับทำ GWP: ระบุตัวเลขเดียว เช่น 149 THB
    - เหตุผล: อธิบายสั้น ๆ ว่าเลือกจากราคาเริ่มต้นของ Basket Range ถัดจาก Hero Range และทำไมลูกค้าส่วนใหญ่ยังพอเอื้อมถึง

    สิ้นสุดคำตอบที่หัวข้อ Suggest Basket Size เท่านั้น ไม่ต้องมีข้อความอื่นต่อท้าย
    """


    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "คุณคือผู้เชี่ยวชาญวิเคราะห์ข้อมูลการขาย ตอบแบบ plain text กระชับ"},
                {"role": "user", "content": prompt},
            ],
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ OpenAI error: {e}"


# ----------------------------------------------------------
#  HTML TABLE RENDER (Dark BI Style)
# ----------------------------------------------------------
def format_money(x: float) -> str:
    return f"฿{x:,.0f}"

def format_abr(x: float) -> str:
    return f"฿{x:,.2f}"

def format_pct(x: float) -> str:
    return f"{x:.2f}%"

def format_change(x: float) -> str:
    return f"{x:+.2f}%"

def render_analysis_table(final_df: pd.DataFrame, start_date: datetime.date, end_date: datetime.date):
    current_year = start_date.year
    sply_year = current_year - 1

    sply_start = start_date.replace(year=sply_year).strftime("%d/%m/%Y")
    sply_end = end_date.replace(year=sply_year).strftime("%d/%m/%Y")
    curr_start = start_date.strftime("%d/%m/%Y")
    curr_end = end_date.strftime("%d/%m/%Y")

    # Build complete HTML document with inline CSS
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            body {{ 
                font-family: 'Inter', sans-serif; 
                margin: 0; 
                padding: 8px;
                background: transparent;
            }}
            .analysis-card {{
                background: #020617;
                border-radius: 16px;
                border: 1px solid #1e293b;
                box-shadow: 0 20px 45px rgba(15,23,42,0.7);
                padding: 1.0rem 1.2rem 0.9rem 1.2rem;
            }}
            table.analysis-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.78rem;
            }}
            table.analysis-table thead th {{
                padding: 0.45rem 0.5rem;
                border-bottom: 1px solid #1f2937;
                border-top: 1px solid #1f2937;
                text-align: center;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }}
            .header-basket {{
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                color: #f9fafb;
                text-align: center;
                font-weight: 600;
                font-size: 0.75rem;
            }}
            .header-sply {{
                background: radial-gradient(circle at top left, #facc15 0%, #854d0e 65%);
                color: #fefce8;
                font-weight: 600;
                font-size: 0.75rem;
                text-align: center;
            }}
            .header-current {{
                background: radial-gradient(circle at top left, #22c55e 0%, #065f46 65%);
                color: #ecfdf5;
                font-weight: 600;
                font-size: 0.75rem;
                text-align: center;
            }}
            .header-change {{
                background: radial-gradient(circle at top left, #f97373 0%, #7f1d1d 65%);
                color: #fee2e2;
                font-weight: 600;
                font-size: 0.75rem;
                text-align: center;
            }}
            .sub-header-sply {{
                background: #111827;
                color: #eab308;
                font-weight: 500;
                text-align: right;
            }}
            .sub-header-current {{
                background: #0f172a;
                color: #4ade80;
                font-weight: 500;
                text-align: right;
            }}
            .sub-header-change {{
                background: #111827;
                color: #fecaca;
                font-weight: 500;
                text-align: right;
            }}
            .analysis-table tbody td {{
                padding: 0.40rem 0.55rem;
                border-bottom: 1px solid #1e293b;
                background: #020617;
            }}
            .cell-text-left {{
                text-align: center;
                color: #e5e7eb;
                font-weight: 500;
            }}
            .cell-num {{
                text-align: right;
                color: #e5e7eb;
                font-variant-numeric: tabular-nums;
            }}
            .analysis-table tbody tr.total-row td {{
                background: linear-gradient(90deg, rgba(37,99,235,0.22), rgba(56,189,248,0.05));
                font-weight: 600;
                color: #f9fafb;
                border-top: 1px solid #1d4ed8;
                border-bottom: 1px solid #1d4ed8;
            }}
            .change-cell {{ font-weight: 600; }}
            .chg-pos {{ color: #22c55e; }}
            .chg-neg {{ color: #f97373; }}
            .chg-zero {{ color: #9ca3af; }}
        </style>
    </head>
    <body>
    <div class="analysis-card">
      <table class="analysis-table">
        <thead>
          <tr>
            <th rowspan="2" class="header-basket">BASKET RANGE</th>
            <th colspan="5" class="header-sply">SPLY: {sply_start} - {sply_end}</th>
            <th colspan="5" class="header-current">CURRENT: {curr_start} - {curr_end}</th>
            <th colspan="2" class="header-change">SHARE CHANGE (pp)</th>
          </tr>
          <tr>
            <th class="sub-header-sply">ABR (฿)</th>
            <th class="sub-header-sply">SALES (฿)</th>
            <th class="sub-header-sply">% SHARE SALES</th>
            <th class="sub-header-sply">BILLS</th>
            <th class="sub-header-sply">% SHARE BILLS</th>

            <th class="sub-header-current">ABR (฿)</th>
            <th class="sub-header-current">SALES (฿)</th>
            <th class="sub-header-current">% SHARE SALES</th>
            <th class="sub-header-current">BILLS</th>
            <th class="sub-header-current">% SHARE BILLS</th>

            <th class="sub-header-change">SALES SHARE Δ</th>
            <th class="sub-header-change">BILLS SHARE Δ</th>
          </tr>
        </thead>
        <tbody>
    """

    for idx, row in final_df.iterrows():
        basket = str(idx)
        is_total = basket.upper() == "TOTAL"
        row_class = "total-row" if is_total else ""

        chg_bills = row["ShareChg_Bills_pp"]
        chg_sales = row["ShareChg_Sales_pp"]

        cls_bills = "chg-pos" if chg_bills > 0 else "chg-neg" if chg_bills < 0 else "chg-zero"
        cls_sales = "chg-pos" if chg_sales > 0 else "chg-neg" if chg_sales < 0 else "chg-zero"

        # Get %Share values directly from dataframe
        share_sales_sply = row['ShareSales_SPLY']
        share_sales_curr = row['ShareSales_CURR']
        
        html += f"""
          <tr class="{row_class}">
            <td class="cell-text-left">{basket}</td>

            <td class="cell-num">{format_abr(row['ABR_SPLY'])}</td>
            <td class="cell-num">{format_money(row['TotalSales_SPLY'])}</td>
            <td class="cell-num">{format_pct(share_sales_sply)}</td>
            <td class="cell-num">{row['TotalBills_SPLY']:,.0f}</td>
            <td class="cell-num">{format_pct(row['ShareBills_SPLY'])}</td>

            <td class="cell-num">{format_abr(row['ABR_CURR'])}</td>
            <td class="cell-num">{format_money(row['TotalSales_CURR'])}</td>
            <td class="cell-num">{format_pct(share_sales_curr)}</td>
            <td class="cell-num">{row['TotalBills_CURR']:,.0f}</td>
            <td class="cell-num">{format_pct(row['ShareBills_CURR'])}</td>

            <td class="cell-num change-cell {cls_sales}">{format_change(chg_sales)}</td>
            <td class="cell-num change-cell {cls_bills}">{format_change(chg_bills)}</td>
          </tr>
        """

    html += """
        </tbody>
      </table>
    </div>
    </body>
    </html>
    """

    # Use components.html for better HTML rendering
    components.html(html, height=650, scrolling=True)

# ----------------------------------------------------------
#  FILTER CONFIRMATION CARD
# ----------------------------------------------------------
def render_filter_summary(metadata, start_date, end_date):
    """Render a confirmation card showing what's being analyzed"""
    current_year = start_date.year
    sply_year = current_year - 1
    
    curr_start = start_date.strftime("%d/%m/%Y")
    curr_end = end_date.strftime("%d/%m/%Y")
    sply_start = start_date.replace(year=sply_year).strftime("%d/%m/%Y")
    sply_end = end_date.replace(year=sply_year).strftime("%d/%m/%Y")
    
    # Extract metadata
    suppliers_raw = metadata.get('SupplierNames', '🏪 All Suppliers')
    categories_raw = metadata.get('Categories', 'All Categories')
    subcategories_raw = metadata.get('SubCategories', 'All Sub-Categories')
    brands_raw = metadata.get('Brands', 'All Brands')
    product_count = metadata.get('ProductCount', 0)
    
    # Smart formatting: Show count + samples if too many
    def format_list(value, item_type="items"):
        if not value or value.startswith('All') or value.startswith('🏪'):
            return value
        
        items = [x.strip() for x in value.split(',')]
        count = len(items)
        
        # If many items, show: "X items (Sample1, Sample2, Sample3, ...)"
        if count > 5:
            samples = ', '.join(items[:3])
            return f"{count} {item_type} ({samples}, ...)"
        else:
            # If few items, show all
            return value
    
    suppliers = format_list(suppliers_raw, "Suppliers")
    categories = format_list(categories_raw, "Categories")
    subcategories = format_list(subcategories_raw, "Sub-Categories")
    brands = format_list(brands_raw, "Brands")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 8px;
                background: transparent;
            }}
            .summary-card {{
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-radius: 16px;
                border: 1px solid #334155;
                padding: 1.5rem;
                box-shadow: 0 16px 35px rgba(15,23,42,0.7);
            }}
            .summary-title {{
                color: #38bdf8;
                font-weight: 700;
                font-size: 1.1rem;
                margin-bottom: 1rem;
                border-bottom: 2px solid #334155;
                padding-bottom: 0.75rem;
            }}
            .summary-content {{
                color: #cbd5e1;
                line-height: 1.8;
            }}
            .info-row {{
                margin-bottom: 0.8rem;
            }}
            .info-label {{
                color: #94a3b8;
                font-weight: 600;
                display: block;
                margin-bottom: 0.3rem;
            }}
            .info-value {{
                color: #e2e8f0;
                margin-left: 1.5rem;
                display: block;
                word-wrap: break-word;
                overflow-wrap: break-word;
                white-space: normal;
            }}
            .highlight {{
                color: #22c55e;
                font-weight: 700;
                margin-left: 0.5rem;
            }}
            .period-section {{
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid #334155;
            }}
            .period-item {{
                margin-left: 1.5rem;
                margin-top: 0.5rem;
            }}
            .period-sply {{
                color: #eab308;
                margin-bottom: 0.3rem;
            }}
            .period-current {{
                color: #22c55e;
            }}
        </style>
    </head>
    <body>
    <div class="summary-card">
        <div class="summary-title">
            📋 Analysis Summary
        </div>
        
        <div class="summary-content">
            <div class="info-row">
                <span class="info-label">📊 Suppliers:</span>
                <span class="info-value">{suppliers}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">🏷️ Categories:</span>
                <span class="info-value">{categories}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">📦 Sub-Categories:</span>
                <span class="info-value">{subcategories}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">🎯 Brands:</span>
                <span class="info-value">{brands}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">📦 Total Products (SKUs):</span>
                <span class="highlight">{product_count:,}</span>
            </div>
            
            <div class="period-section">
                <span class="info-label">📅 Period:</span>
                <div class="period-item">
                    <div class="period-sply">
                        <strong>SPLY:</strong> {sply_start} - {sply_end}
                    </div>
                    <div class="period-current">
                        <strong>Current:</strong> {curr_start} - {curr_end}
                    </div>
                </div>
            </div>
        </div>
    </div>
    </body>
    </html>
    """
    
    components.html(html, height=620, scrolling=False)

# ----------------------------------------------------------
#  MAIN
# ----------------------------------------------------------
if run_btn:
    client = get_bq_client()
    if client:
        # Fetch and display filter metadata
        with st.spinner("Loading filter information..."):
            metadata = get_filter_metadata(client, supplier_code, category, subcategory, brand)
            render_filter_summary(metadata, start_date, end_date)
        
        # Run analysis
        with st.spinner("Running analysis..."):
            df = run_query(client, start_date, end_date, supplier_code, category, subcategory, brand)

            current_year = start_date.year
            sply_year = current_year - 1

            df_curr = df[df["Year"] == current_year].set_index("Basket_Range")
            df_sply = df[df["Year"] == sply_year].set_index("Basket_Range")

            merged = pd.merge(
                df_sply,
                df_curr,
                left_index=True,
                right_index=True,
                suffixes=("_SPLY", "_CURR"),
                how="outer",
            ).fillna(0)

            order = [
                "< 49",
                "49 - 98",
                "99 - 148",
                "149 - 198",
                "199 - 248",
                "249 - 298",
                "299 - 348",
                "349 - 398",
                "399 - 448",
                "449 - 498",
                "499 - 548",
                "549 - 598",
                "599 - 648",
                "649 - 698",
                ">= 699",
            ]
            merged.index = pd.Categorical(merged.index, categories=order, ordered=True)
            merged = merged.sort_index()

            total_sales_sply = merged["TotalSales_SPLY"].sum()
            total_bills_sply = merged["TotalBills_SPLY"].sum()

            total_sales_curr = merged["TotalSales_CURR"].sum()
            total_bills_curr = merged["TotalBills_CURR"].sum()

            # Calculate % Share for both periods
            merged["ShareSales_SPLY"] = (
                merged["TotalSales_SPLY"] / total_sales_sply * 100 if total_sales_sply else 0
            )
            merged["ShareSales_CURR"] = (
                merged["TotalSales_CURR"] / total_sales_curr * 100 if total_sales_curr else 0
            )
            merged["ShareBills_SPLY"] = (
                merged["TotalBills_SPLY"] / total_bills_sply * 100 if total_bills_sply else 0
            )
            merged["ShareBills_CURR"] = (
                merged["TotalBills_CURR"] / total_bills_curr * 100 if total_bills_curr else 0
            )

            # Calculate Share Change (percentage points)
            merged["ShareChg_Sales_pp"] = merged["ShareSales_CURR"] - merged["ShareSales_SPLY"]
            merged["ShareChg_Bills_pp"] = merged["ShareBills_CURR"] - merged["ShareBills_SPLY"]

            total_row = pd.DataFrame(
                {
                    "ABR_SPLY": [
                        total_sales_sply / total_bills_sply if total_bills_sply else 0
                    ],
                    "TotalSales_SPLY": [total_sales_sply],
                    "TotalBills_SPLY": [total_bills_sply],
                    "ShareSales_SPLY": [100.0],
                    "ShareBills_SPLY": [100.0],
                    "ABR_CURR": [
                        total_sales_curr / total_bills_curr if total_bills_curr else 0
                    ],
                    "TotalSales_CURR": [total_sales_curr],
                    "TotalBills_CURR": [total_bills_curr],
                    "ShareSales_CURR": [100.0],
                    "ShareBills_CURR": [100.0],
                },
                index=["Total"],
            )

            # For Total row, Share Change is always 0 (100% - 100%)
            total_row["ShareChg_Sales_pp"] = 0.0
            total_row["ShareChg_Bills_pp"] = 0.0

            final_df = pd.concat([merged, total_row])

        st.markdown("""
        <div class="analysis-title" style="margin-top:10px;">
        <span class="icon">📈</span>
        <span>Analysis Report</span>
        </div>
        """, unsafe_allow_html=True)

        render_analysis_table(final_df, start_date, end_date)

        # Generate AI insights first
        with st.spinner("Generating AI insights..."):
            insight = generate_ai_insight(df, category, brand)
        
        # Convert markdown to HTML line by line
        lines = insight.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            # Handle headers - close immediately
            if stripped.startswith('####'):
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                header_text = stripped.replace('####', '').strip()
                formatted_lines.append(f'<h4>{header_text}</h4>')
            
            # Handle bullet points
            elif stripped.startswith('- '):
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                formatted_lines.append(f'<li>{stripped[2:]}</li>')
            
            # Handle regular text
            elif stripped:
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append(f'<p>{stripped}</p>')
        
        # Close any open list
        if in_list:
            formatted_lines.append('</ul>')
        
        insight_html = '\n'.join(formatted_lines)
        
        # Render AI box with components.html
        ai_box_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Inter', sans-serif;
                    background: transparent;
                }}
                .ai-summary-box {{
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    border-radius: 16px;
                    border: 1px solid #334155;
                    padding: 1.5rem;
                    color: #e5e7eb;
                    box-shadow: 0 16px 35px rgba(15,23,42,0.7);
                }}
                .ai-title {{
                    color: #38bdf8;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 1rem;
                    font-size: 1.1rem;
                    border-bottom: 2px solid #334155;
                    padding-bottom: 0.75rem;
                }}
                .ai-content {{
                    line-height: 1.8;
                    color: #cbd5e1;
                }}
                .ai-content h4 {{
                    color: #22c55e;
                    font-size: 0.95rem;
                    font-weight: 600;
                    margin-top: 1rem;
                    margin-bottom: 0.5rem;
                }}
                .ai-content ul {{
                    margin-left: 1.2rem;
                    margin-top: 0.3rem;
                    padding-left: 0;
                }}
                .ai-content li {{
                    margin-bottom: 0.4rem;
                }}
            </style>
        </head>
        <body>
            <div class="ai-summary-box">
                <div class="ai-title">
                    <span>✨</span>
                    <span>AI Summary & Insights</span>
                </div>
                <div class="ai-content">
                    {insight_html}
                </div>
            </div>
        </body>
        </html>
        """
        
        components.html(ai_box_html, height=600, scrolling=True)
