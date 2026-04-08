import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials

# 1. Cấu hình giao diện
st.set_page_config(page_title="AI Assistant", layout="centered")
st.title("🤖 Trợ lý AI của tôi")

# 2. Kết nối Google Sheet (Tối ưu hóa để chạy nhanh hơn)
@st.cache_resource
def connect_google_sheet(conf, sheet_id):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(conf, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1

# 3. Lấy thông tin từ Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GOOGLE_SHEET_ID = st.secrets["GOOGLE_SHEET_ID"]
    GOOGLE_JSON = st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"]
    
    # Thiết lập AI
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # Thiết lập Sheet
    sheet = connect_google_sheet(GOOGLE_JSON, GOOGLE_SHEET_ID)
except Exception as e:
    st.error(f"❌ Lỗi cấu hình Secrets hoặc Kết nối: {e}")
    st.stop()

# 4. Giao diện Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Gõ 'Lưu: ...' để ghi vào Sheet hoặc chat bình thường"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        if prompt.lower().startswith("lưu:"):
            try:
                data_to_save = prompt[4:].strip()
                sheet.append_row([data_to_save])
                full_response = f"✅ Đã lưu vào Sheet: **{data_to_save}**"
            except Exception as e:
                full_response = f"❌ Lỗi khi ghi Sheet: {e}"
        else:
            try:
                # Gọi Gemini xử lý
                res = model.generate_content(prompt)
                full_response = res.text
            except Exception as e:
                full_response = f"❌ Lỗi AI: {e}. Vui lòng kiểm tra lại API Key."

        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
