# app.py
import streamlit as st
import time

# --- 1. Nhập các lớp nghiệp vụ từ code gốc của bạn ---
# Đảm bảo các file taotkchinh.py và mailao.py nằm trong cùng thư mục
try:
    from taotkchinh import GarenaRegister
    from mailao import tempmail
    # Bạn có thể cần thêm các import khác nếu tool của bạn yêu cầu
except ImportError as e:
    st.error(f"Lỗi import: Không tìm thấy module {e}. Đảm bảo các file gốc đã được đặt đúng chỗ.")
    st.stop()
    
# --- 2. Xây dựng giao diện Streamlit ---
st.title("🚀 Tool Reg Acc Thử Nghiệm")
st.markdown("Nhập thông tin đăng ký để chạy thử nghiệm tool Python của bạn.")

# Khởi tạo các đối tượng cần thiết
reg_tool = GarenaRegister()
mail_tool = tempmail()

# Tạo Form nhập liệu
with st.form(key='registration_form'):
    st.subheader("Thông tin Đăng ký")
    
    # Giả định các input cần thiết cho tool reg acc Garena của bạn
    username = st.text_input("Tên đăng nhập (Username)")
    password = st.text_input("Mật khẩu (Password)", type="password")
    
    # Các thông số khác (ví dụ: proxy)
    proxy = st.text_input("Proxy (ví dụ: 103.119.160.1)", value="", help="Để trống nếu không dùng proxy.")
    port = st.number_input("Port", value=0)
    
    submit_button = st.form_submit_button("Chạy Tool Đăng Ký")

if submit_button:
    if not username or not password:
        st.warning("Vui lòng nhập Tên đăng nhập và Mật khẩu.")
    else:
        st.info("Đang bắt đầu quá trình đăng ký...")
        
        # --- 3. Thực thi Logic Đăng Ký Cốt Lõi ---
        try:
            # B1: Lấy email tạm thời (có thể gọi hàm tạo email nếu cần,
            # ở đây ta giả định taotkchinh.py sẽ tự tạo email nếu cần)
            
            # B2: Gửi yêu cầu OTP/lấy OTP
            st.warning("Đang chờ OTP Email...")
            # Ví dụ: Giả định email là "test@tempmail.plus"
            test_email = f"{username}@tempmail.plus" 
            
            # Giả định hàm get_code của bạn cần chạy lặp để lấy OTP
            email_otp = None
            for i in range(5):
                st.write(f"Đang kiểm tra mail lần thứ {i+1}...")
                # Giả sử email đã được tạo và lưu trong một biến nào đó
                email_otp = mail_tool.get_code(test_email) 
                if email_otp:
                    st.success(f"✔️ Lấy được OTP: {email_otp}")
                    break
                time.sleep(2)
            
            if not email_otp:
                st.error("❌ Không lấy được OTP Email.")
            else:
                # B3: Gọi hàm đăng ký chính của bạn
                st.warning("Đang tiến hành đăng ký tài khoản...")
                # Hàm register_account của bạn (proxy, port được truyền từ input)
                result = reg_tool.register_account(
                    username=username, 
                    email=test_email, 
                    email_otp=email_otp, 
                    passw=password, 
                    proxy=proxy if port > 0 else None, 
                    port=port if port > 0 else None
                )

                # B4: Hiển thị kết quả
                if result and result.get('code') == 0:
                    st.balloons()
                    st.success(f"✅ Đăng ký thành công tài khoản: {username}")
                    st.json(result)
                else:
                    st.error("❌ Đăng ký thất bại. Xem chi tiết lỗi:")
                    st.json(result)
                    
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi chạy tool: {e}")
            st.exception(e)