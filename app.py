import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials

# 1. Cấu hình giao diện
st.set_page_config(page_title="AI Assistant", layout="centered")
st.title("🤖 Trợ lý AI của tôi")
st.info("App có thể chat với Gemini và lưu dữ liệu vào Google Sheet!")

# 2. Lấy thông tin bảo mật từ Secrets (sẽ cấu hình ở Bước 7)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GOOGLE_SHEET_ID = st.secrets["GOOGLE_SHEET_ID"]
GOOGLE_JSON = st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"]

# 3. Thiết lập kết nối
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# Kết nối Google Sheet
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(GOOGLE_JSON, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

# 4. Giao diện Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập nội dung hoặc gõ 'Lưu: ...' để ghi vào Sheet"):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Xử lý Logic
    if prompt.lower().startswith("lưu:"):
        # Nếu câu chat bắt đầu bằng "Lưu:", sẽ ghi vào Sheet
        data_to_save = prompt[4:].strip()
        sheet.append_row([data_to_save])
        response = f"✅ Đã lưu vào Sheet: {data_to_save}"
    else:
        # Nếu không, sẽ hỏi Gemini
        res = model.generate_content(prompt)
        response = res.text

    # Hiển thị phản hồi từ AI
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
