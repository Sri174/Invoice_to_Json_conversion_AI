import streamlit as st
import requests
import json
import os
import time

# --- Configuration ---
_API_BASE = os.getenv("API_URL", "http://200.1.50.232:8001/process")
API_URL = _API_BASE if _API_BASE.endswith("/process") else f"{_API_BASE.rstrip('/')}/process"
st.set_page_config(
    page_title="Invoice Extraction AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for modern styling ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stDownloadButton>button {
        background-color: #2196F3;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stDownloadButton>button:hover {
        background-color: #0b7dda;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .header-text {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- UI Header ---
st.markdown("<h1 class='header-text'>📄 Invoice Extraction AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d; margin-bottom: 2rem;'>Upload an invoice or receipt to automatically extract structured data using our advanced AI.</p>", unsafe_allow_html=True)

# --- Upload Section ---
st.markdown("### 📤 Upload Invoice")
uploaded_file = st.file_uploader("Drag and drop your file here", type=["pdf", "jpg", "jpeg", "png", "bmp", "tiff", "webp"], help="Supports PDF documents and common image formats.")

# --- Processing Logic ---
if uploaded_file is not None:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_btn = st.button("🚀 Process Document", use_container_width=True)
        
    if process_btn:
        with st.spinner("🧠 AI is analyzing and extracting data... Please wait."):
            try:
                # Prepare file for upload
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Start timing
                start_time = time.time()
                
                # Make POST request to API
                response = requests.post(API_URL, files=files)
                response.raise_for_status()  # Raise exception for bad status codes
                
                # Parse results
                result_data = response.json()
                elapsed_time = round(time.time() - start_time, 2)
                
                # Store result in session state to persist across reruns
                st.session_state['result_data'] = result_data
                st.session_state['elapsed_time'] = elapsed_time
                st.session_state['filename'] = uploaded_file.name
                
            except requests.exceptions.ConnectionError:
                st.error(f"🚨 Could not connect to the API. Is the server running on {API_URL}?")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ API Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")

# --- Results Section ---
if 'result_data' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Extraction Results")
    
    st.markdown(f"""
    <div class='success-box'>
        <strong>✅ Successfully processed</strong> {st.session_state['filename']} in {st.session_state['elapsed_time']} seconds.
    </div>
    """, unsafe_allow_html=True)
    
    result_data = st.session_state['result_data']
    
    # Display token usage if available
    usage = result_data.get("_usage_metadata")
    if usage:
        st.info(f"🪙 **Tokens Used:** {usage.get('total_token_count', 0)} (Prompt: {usage.get('prompt_token_count', 0)} | Completion: {usage.get('candidates_token_count', 0)})")
    
    # Download Button
    result_json_str = json.dumps(result_data, indent=4)
    st.download_button(
        label="📥 Download JSON Results",
        data=result_json_str,
        file_name=f"extracted_{st.session_state['filename']}.json",
        mime="application/json",
        use_container_width=True
    )
    
    # Create Tabs for modern presentation
    tab1, tab2 = st.tabs(["📊 Table Structure View", "💻 Raw JSON View"])
    
    with tab1:
        import pandas as pd
        
        # Helper function to flatten nested dictionaries for table display
        def flatten_dict(d, parent_key='', sep=' '):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                new_key = new_key.replace('_', ' ').title()
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list) and all(not isinstance(i, dict) for i in v):
                    val = ", ".join(map(str, v))
                    if val:
                        items.append((new_key, val))
                elif v is not None and v != "":
                    items.append((new_key, v))
            return dict(items)

        # 1. Header Table
        st.markdown("#### 🏢 Header Details")
        header_data = result_data.get("header", {})
        if header_data:
            flat_header = flatten_dict(header_data)
            if flat_header:
                df_header = pd.DataFrame(list(flat_header.items()), columns=["Field", "Value"])
                st.dataframe(df_header, use_container_width=True, hide_index=True)
            else:
                st.info("No header data found.")
        else:
            st.info("No header data found.")
        
        # 2. Line Items Table
        st.markdown("#### 📦 Line Items")
        line_items = result_data.get("line_items", [])
        if line_items:
            df_lines = pd.DataFrame(line_items)
            # Clean up column names for display
            df_lines.columns = [col.replace('_', ' ').title() for col in df_lines.columns]
            
            # Drop columns that are completely empty/null across all line items
            df_lines = df_lines.dropna(how='all', axis=1)
            
            # Explicitly remove the 'Taxed' column as requested
            if 'Taxed' in df_lines.columns:
                df_lines = df_lines.drop(columns=['Taxed'])
            
            # Format boolean columns to be readable emojis instead of empty checkboxes
            for col in df_lines.select_dtypes(include=['bool']).columns:
                df_lines[col] = df_lines[col].map({True: "✅ Yes", False: "❌ No", pd.NA: "-"})
                
            st.dataframe(df_lines, use_container_width=True, hide_index=True)
        else:
            st.info("No line items found.")
            
        # 3. Summary Table
        st.markdown("#### 📊 Summary")
        summary_data = result_data.get("summary", {})
        if summary_data:
            flat_summary = flatten_dict(summary_data)
            if flat_summary:
                df_summary = pd.DataFrame(list(flat_summary.items()), columns=["Field", "Value"])
                st.dataframe(df_summary, use_container_width=True, hide_index=True)
            else:
                st.info("No summary data found.")
        else:
            st.info("No summary data found.")

        # 4. Footer Table
        st.markdown("#### 📝 Footer Details")
        footer_data = result_data.get("footer", {})
        if footer_data:
            flat_footer = flatten_dict(footer_data)
            if flat_footer:
                df_footer = pd.DataFrame(list(flat_footer.items()), columns=["Field", "Value"])
                st.dataframe(df_footer, use_container_width=True, hide_index=True)
            else:
                st.info("No footer data found.")
        else:
            st.info("No footer data found.")

    with tab2:
        st.markdown("#### 🔍 Complete JSON Response")
        st.json(result_data)
