"""
FAQ Knowledge Base for Diabetes Diagnosis System - UPDATED WITH 7 NEW FAQs
Cơ sở tri thức FAQ về bệnh tiểu đường (tiếng Việt) - ĐÃ THÊM 7 FAQ MỚI
"""

# ============================================================
# KNOWLEDGE BASE - Dữ liệu FAQ về bệnh tiểu đường (22 FAQs)
# ============================================================
DIABETES_FAQ = [
    # ================== 15 FAQ GỐC ==================
    {
        "id": "faq_001",
        "category": "Khái niệm",
        "question": "Bệnh tiểu đường là gì?",
        "answer": """Bệnh tiểu đường (diabetes mellitus) là một bệnh mãn tính xảy ra khi cơ thể không sản xuất đủ insulin hoặc không thể sử dụng insulin hiệu quả. Insulin là hormone giúp glucose (đường) từ thực phẩm đi vào tế bào để tạo năng lượng. Khi thiếu insulin hoặc insulin không hoạt động tốt, glucose tích tụ trong máu gây ra tình trạng tăng đường huyết.""",
        "keywords": ["tiểu đường là gì", "định nghĩa tiểu đường", "diabetes là gì", "khái niệm tiểu đường", "giải thích tiểu đường"]
    },
    {
        "id": "faq_002",
        "category": "Phân loại",
        "question": "Có mấy loại bệnh tiểu đường?",
        "answer": """Có 3 loại chính:
• Tiểu đường type 1: Cơ thể không sản xuất insulin, thường xuất hiện ở trẻ em và thanh thiếu niên.
• Tiểu đường type 2: Cơ thể không sử dụng insulin hiệu quả, phổ biến nhất (90-95% ca), thường xuất hiện ở người trưởng thành.
• Tiểu đường thai kỳ: Xuất hiện trong thai kỳ, thường biến mất sau sinh nhưng tăng nguy cơ mắc type 2 sau này.""",
        "keywords": ["loại tiểu đường", "type 1", "type 2", "phân loại", "thai kỳ"]
    },
    {
        "id": "faq_003",
        "category": "Triệu chứng",
        "question": "Triệu chứng của bệnh tiểu đường là gì?",
        "answer": """Các triệu chứng phổ biến của bệnh tiểu đường:
• Khát nước nhiều và đi tiểu thường xuyên (đặc biệt ban đêm)
• Cảm thấy rất đói dù đã ăn
• Mệt mỏi, uể oải
• Giảm cân không rõ nguyên nhân
• Nhìn mờ, mắt kém dần
• Vết thương lâu lành
• Nhiễm trùng da hoặc nấm thường xuyên
• Tê tay chân
Lưu ý: Nhiều người type 2 không có triệu chứng rõ ràng ban đầu.""",
        "keywords": ["triệu chứng", "dấu hiệu", "biểu hiện", "nhận biết", "khát nước", "đi tiểu", "mệt mỏi", "giảm cân", "nhìn mờ", "tê tay chân"]
    },
    {
        "id": "faq_004",
        "category": "Nguyên nhân",
        "question": "Nguyên nhân gây bệnh tiểu đường?",
        "answer": """Nguyên nhân phụ thuộc vào loại:
Type 1: Hệ miễn dịch tấn công tế bào sản xuất insulin trong tuyến tụy (tự miễn). Nguyên nhân chính xác chưa rõ, có thể liên quan đến gen và môi trường.
Type 2: Các yếu tố nguy cơ:
• Thừa cân, béo phì (đặc biệt béo bụng)
• Ít vận động
• Tiền sử gia đình có người mắc
• Tuổi tác (>45 tuổi)
• Huyết áp cao, cholesterol cao
• Từng có tiền tiểu đường hoặc tiểu đường thai kỳ""",
        "keywords": ["nguyên nhân", "tại sao", "yếu tố nguy cơ", "di truyền", "béo phì"]
    },
    {
        "id": "faq_005",
        "category": "Chẩn đoán",
        "question": "Làm thế nào để chẩn đoán bệnh tiểu đường?",
        "answer": """Các xét nghiệm chẩn đoán:
1. Đường huyết lúc đói (FPG):
   • Bình thường: <100 mg/dL
   • Tiền tiểu đường: 100-125 mg/dL
   • Tiểu đường: ≥126 mg/dL
2. HbA1c (đường huyết trung bình 2-3 tháng):
   • Bình thường: <5.7%
   • Tiền tiểu đường: 5.7-6.4%
   • Tiểu đường: ≥6.5%
3. Nghiệm pháp dung nạp glucose (OGTT):
   • Uống 75g glucose, đo sau 2h
   • Tiểu đường: ≥200 mg/dL
Cần xét nghiệm lại để xác nhận.""",
        "keywords": ["chẩn đoán", "xét nghiệm", "kiểm tra", "phát hiện", "biết có bị", "glucose", "HbA1c", "đường huyết", "đường huyết cao", "đường huyết bao nhiêu"]
    },
    {
        "id": "faq_006",
        "category": "Điều trị",
        "question": "Bệnh tiểu đường có chữa khỏi được không?",
        "answer": """Type 1: Chưa có cách chữa khỏi hoàn toàn. Người bệnh cần tiêm insulin suốt đời và quản lý đường huyết cẩn thận.
Type 2: Không thể "chữa khỏi" hoàn toàn nhưng CÓ THỂ KIỂM SOÁT và thậm chí ĐẢO NGƯỢC triệu chứng thông qua:
• Giảm cân (nếu thừa cân)
• Chế độ ăn lành mạnh
• Tập thể dục đều đặn
• Thuốc hạ đường huyết (nếu cần)
• Theo dõi đường huyết thường xuyên
Nhiều người type 2 có thể giảm hoặc ngừng thuốc nếu thay đổi lối sống hiệu quả.""",
        "keywords": ["chữa khỏi", "điều trị", "kiểm soát", "đảo ngược"]
    },
    {
        "id": "faq_007",
        "category": "Chế độ ăn",
        "question": "Người bị tiểu đường nên ăn gì?",
        "answer": """Nguyên tắc chung:
NÊN ĂN:
• Rau xanh, rau củ không tinh bột
• Ngũ cốc nguyên hạt (gạo lứt, yến mạch)
• Protein nạc (cá, gà, đậu)
• Chất béo lành mạnh (dầu olive, quả bơ, hạt)
• Trái cây ít đường (táo, dâu, cam)
HẠN CHẾ:
• Đường, kẹo, bánh ngọt
• Đồ ăn chế biến sẵn
• Nước ngọt có gas
• Tinh bột trắng (gạo trắng, bánh mì trắng)
• Thức ăn chiên, nhiều dầu mỡ
Ăn nhiều bữa nhỏ trong ngày, đều đặn.""",
        "keywords": ["ăn gì", "chế độ ăn", "thực đơn", "dinh dưỡng", "kiêng"]
    },
    {
        "id": "faq_008",
        "category": "Vận động",
        "question": "Người tiểu đường có nên tập thể dục không?",
        "answer": """RẤT NÊN! Vận động là một phần quan trọng trong kiểm soát tiểu đường:
Lợi ích:
• Giảm đường huyết tự nhiên
• Tăng độ nhạy insulin
• Giảm cân, kiểm soát BMI
• Cải thiện sức khỏe tim mạch
• Giảm stress
Khuyến nghị:
• Ít nhất 150 phút/tuần (30 phút/ngày x 5 ngày)
• Kết hợp aerobic (đi bộ, bơi, đạp xe) và tập sức mạnh
• Bắt đầu từ từ, tăng dần cường độ
Lưu ý: Kiểm tra đường huyết trước và sau tập, mang theo đồ ăn nhẹ phòng hạ đường huyết.""",
        "keywords": ["tập thể dục", "vận động", "thể thao", "exercise"]
    },
    {
        "id": "faq_009",
        "category": "Biến chứng",
        "question": "Biến chứng của bệnh tiểu đường là gì?",
        "answer": """Nếu không kiểm soát tốt, tiểu đường có thể gây:
Biến chứng lâu dài:
• Bệnh tim mạch, đột quỵ
• Bệnh thận (thận tiểu đường)
• Tổn thương mắt (có thể mù)
• Tổn thương thần kinh (tê tay chân, đau)
• Bệnh lý bàn chân (nhiễm trùng, loét)
• Vấn đề răng miệng, nướu
• Nhiễm trùng da
Biến chứng cấp tính:
• Hạ đường huyết (nguy hiểm)
• Tăng đường huyết nghiêm trọng (hôn mê)
Kiểm soát đường huyết tốt CÓ THỂ NGĂN NGỪA hầu hết biến chứng.""",
        "keywords": ["biến chứng", "tác hại", "nguy hiểm", "hậu quả", "nguy cơ", "tim mạch", "thận", "mắt", "đường huyết cao lâu ngày"]
    },
    {
        "id": "faq_010",
        "category": "Theo dõi",
        "question": "Cần theo dõi gì khi mắc tiểu đường?",
        "answer": """Theo dõi đường huyết:
• Đo đường huyết tại nhà (theo chỉ định bác sĩ)
• Xét nghiệm HbA1c mỗi 3-6 tháng
• Mục tiêu: HbA1c <7% (hoặc theo chỉ định)
Khám định kỳ:
• Bác sĩ nội tiết: 3-6 tháng/lần
• Khám mắt: 1 năm/lần
• Khám thận: xét nghiệm nước tiểu định kỳ
• Khám bàn chân: mỗi lần khám
• Theo dõi huyết áp, cholesterol
Ghi chép nhật ký:
• Đường huyết
• Chế độ ăn
• Vận động
• Thuốc men""",
        "keywords": ["theo dõi", "kiểm tra", "khám", "định kỳ", "HbA1c"]
    },
    {
        "id": "faq_011",
        "category": "Hệ thống",
        "question": "Hệ thống dự đoán này hoạt động như thế nào?",
        "answer": """Hệ thống sử dụng AI để phân tích nguy cơ tiểu đường qua 2 cách:
1. Machine Learning (ML):
   • Phân tích 8 chỉ số y tế (glucose, BMI, tuổi...)
   • Sử dụng nhiều models: KNN, Naive Bayes, ID3
   • Độ chính xác: 75-85%
2. Natural Language Processing (NLP):
   • Phân tích mô tả triệu chứng bằng tiếng Việt
   • Sử dụng PhoBERT (AI hiểu tiếng Việt)
   • Xác định giai đoạn bệnh (0-3)
3. Ensemble:
   • Kết hợp ML + NLP (50-50)
   • Đưa ra kết luận cuối cùng
Lưu ý: Đây chỉ là công cụ hỗ trợ, KHÔNG THAY THẾ chẩn đoán của bác sĩ.""",
        "keywords": ["hệ thống", "AI", "machine learning", "hoạt động", "dự đoán"]
    },
    {
        "id": "faq_012",
        "category": "Hệ thống",
        "question": "Kết quả dự đoán có chính xác không?",
        "answer": """Độ chính xác:
• ML models: 75-85% (trên dữ liệu test)
• NLP model: ~85% (PhoBERT)
• Ensemble: Cải thiện độ tin cậy bằng cách kết hợp 2 phương pháp
Giới hạn:
• Kết quả dựa trên dữ liệu bạn nhập và patterns từ data huấn luyện
• KHÔNG thay thế xét nghiệm máu chuyên sâu
• Chỉ là công cụ sàng lọc/tham khảo ban đầu
Khuyến nghị:
• Nếu kết quả "Có nguy cơ" → ĐI KHÁM BÁC SĨ để xác nhận
• Xét nghiệm máu glucose và HbA1c là tiêu chuẩn vàng
• Sử dụng kết quả để nhận thức nguy cơ, không tự chẩn đoán""",
        "keywords": ["chính xác", "độ tin cậy", "accuracy", "đáng tin"]
    },
    {
        "id": "faq_013",
        "category": "Sử dụng",
        "question": "Làm thế nào để sử dụng hệ thống?",
        "answer": """Các bước sử dụng:
1. Đăng ký/Đăng nhập:
   • Tạo tài khoản miễn phí
   • Đăng nhập để sử dụng
2. Nhập thông tin:
   • Chỉ số y tế: Pregnancies, Glucose, BMI, Age...
   • Triệu chứng (tùy chọn): Mô tả bằng tiếng Việt
3. Nhấn "Gửi dữ liệu":
   • Hệ thống phân tích bằng ML + NLP
   • Kết quả hiển thị trong ~2-5 giây
4. Xem kết quả:
   • ML: Dựa trên chỉ số y tế
   • NLP: Dựa trên triệu chứng
   • Ensemble: Kết luận tổng hợp
5. Lưu lịch sử:
   • Tất cả dự đoán được lưu tự động
   • Xem lại tại Dashboard""",
        "keywords": ["hướng dẫn", "cách dùng", "sử dụng", "tutorial"]
    },
    {
        "id": "faq_014",
        "category": "Phòng ngừa",
        "question": "Làm thế nào để phòng ngừa bệnh tiểu đường?",
        "answer": """Các biện pháp phòng ngừa type 2:
1. Duy trì cân nặng hợp lý:
   • BMI 18.5-24.9
   • Giảm 5-7% cân nặng nếu thừa cân
2. Ăn uống lành mạnh:
   • Nhiều rau xanh, trái cây
   • Ngũ cốc nguyên hạt
   • Hạn chế đường, tinh bột trắng
3. Vận động đều đặn:
   • 30 phút/ngày, 5 ngày/tuần
   • Đi bộ, chạy, bơi, đạp xe
4. Kiểm tra sức khỏe định kỳ:
   • Đường huyết 1 năm/lần (nếu có yếu tố nguy cơ)
   • HbA1c nếu có tiền tiểu đường
5. Quản lý stress:
   • Ngủ đủ giấc (7-8h/đêm)
   • Thiền, yoga, thư giãn""",
        "keywords": ["phòng ngừa", "dự phòng", "tránh", "ngăn ngừa"]
    },
    {
        "id": "faq_015",
        "category": "Hỗ trợ",
        "question": "Tôi cần hỗ trợ thêm, liên hệ ai?",
        "answer": """Hỗ trợ kỹ thuật:
• Email: support@diabetesdiagnosis.com
• Hotline: 1900-xxxx (8h-20h hàng ngày)
Hỗ trợ y tế:
• Vui lòng liên hệ bác sĩ hoặc cơ sở y tế gần nhất
• Hotline khẩn cấp: 115
Tài liệu tham khảo:
• WHO: https://www.who.int/diabetes
• Hiệp hội Tiểu đường Việt Nam
• Bộ Y tế Việt Nam
Lưu ý: Hệ thống không cung cấp tư vấn y tế trực tiếp. Mọi thắc mắc về sức khỏe cần tham khảo ý kiến bác sĩ.""",
        "keywords": ["liên hệ", "hỗ trợ", "help", "support", "contact"]
    },

    {
        "id": "faq_016",
        "category": "Chẩn đoán",
        "question": "Tiền tiểu đường là gì và cần làm gì?",
        "answer": """Tiền tiểu đường (prediabetes) là tình trạng đường huyết cao hơn bình thường nhưng chưa đạt mức tiểu đường:
• HbA1c: 5.7–6.4%
• Đường huyết lúc đói: 100–125 mg/dL
Đây là giai đoạn cảnh báo sớm, nhưng hoàn toàn có thể ĐẢO NGƯỢC bằng:
• Giảm 5-7% cân nặng (nếu thừa cân)
• Ăn uống lành mạnh, nhiều rau, ngũ cốc nguyên hạt
• Tập thể dục đều đặn 150 phút/tuần
• Kiểm tra đường huyết định kỳ
Nếu không thay đổi lối sống, khoảng 30% sẽ tiến triển thành tiểu đường type 2 trong 5 năm. Hãy gặp bác sĩ để được tư vấn cụ thể.""",
        "keywords": ["tiền tiểu đường", "prediabetes", "đường huyết cao nhẹ", "HbA1c 5.7", "đảo ngược tiểu đường", "ngăn ngừa type 2"]
    },
    {
        "id": "faq_017",
        "category": "Biến chứng",
        "question": "Hạ đường huyết nguy hiểm thế nào và xử lý ra sao?",
        "answer": """Hạ đường huyết (đường huyết <70 mg/dL) thường xảy ra khi dùng insulin hoặc một số thuốc hạ đường huyết quá liều, bỏ bữa.
Triệu chứng: Run tay, vã mồ hôi, chóng mặt, đói dữ dội, tim đập nhanh, lú lẫn, nghiêm trọng có thể ngất hoặc co giật.
Xử lý khẩn cấp (quy tắc 15-15):
• Ăn/uống ngay 15g carbohydrate nhanh (1 ly nước đường, 3-4 viên kẹo glucose, nửa ly nước ngọt)
• Đo lại đường huyết sau 15 phút
• Nếu vẫn thấp, lặp lại
• Sau khi ổn định, ăn bữa nhẹ có protein để tránh tái phát
Mang theo kẹo/glucose mọi lúc. Nếu nặng, cần tiêm glucagon hoặc gọi cấp cứu 115.""",
        "keywords": ["hạ đường huyết", "hạ đường", "run tay", "vã mồ hôi", "ngất", "glucagon", "xử lý hạ đường huyết"]
    },
    {
        "id": "faq_018",
        "category": "Phân loại",
        "question": "Tiểu đường thai kỳ cần chú ý gì?",
        "answer": """Tiểu đường thai kỳ ảnh hưởng khoảng 10-15% thai phụ ở Việt Nam. Thường xuất hiện từ tuần 24-28.
Nguy cơ: Bé to, sinh khó, hạ đường huyết sơ sinh, mẹ dễ bị type 2 sau này.
Quản lý:
• Kiểm soát đường huyết chặt chẽ (thường bằng chế độ ăn + vận động)
• Một số trường hợp cần dùng insulin (an toàn cho thai nhi)
• Theo dõi thai kỹ (siêu âm, NST)
Sau sinh:
• Kiểm tra đường huyết lại sau 6-12 tuần
• Duy trì lối sống lành mạnh để giảm 50-70% nguy cơ type 2 sau này.""",
        "keywords": ["tiểu đường thai kỳ", "đái tháo đường thai kỳ", "mang thai bị tiểu đường", "bầu bị tiểu đường", "insulin khi mang thai"]
    },
    {
        "id": "faq_019",
        "category": "Theo dõi",
        "question": "Máy đo đường huyết liên tục (CGM) có lợi ích gì?",
        "answer": """CGM (Continuous Glucose Monitoring) là thiết bị theo dõi đường huyết liên tục 24/7 qua cảm biến dưới da.
Lợi ích:
• Phát hiện sớm tăng/hạ đường huyết (đặc biệt ban đêm)
• Hiển thị xu hướng đường huyết (mũi tên lên/xuống)
• Giảm nguy cơ biến chứng cấp tính
• Giúp điều chỉnh liều insulin/thuốc chính xác hơn
Khuyến cáo mạnh cho:
• Người type 1
• Người dùng insulin nhiều lần/ngày
• Type 2 có nguy cơ hạ đường huyết cao
Hiện nay ở Việt Nam đã có nhiều loại CGM (Freestyle Libre, Dexcom). Cần bác sĩ hướng dẫn sử dụng.""",
        "keywords": ["CGM", "máy đo đường huyết liên tục", "freestyle libre", "dexcom", "cảm biến đường huyết", "theo dõi liên tục"]
    },
    {
        "id": "faq_020",
        "category": "Điều trị",
        "question": "Thuốc GLP-1 (Ozempic, semaglutide) dùng cho tiểu đường như thế nào?",
        "answer": """GLP-1 receptor agonists (như semaglutide - Ozempic, Rybelsus; dulaglutide - Trulicity) là nhóm thuốc hiện đại cho type 2.
Lợi ích nổi bật:
• Hạ đường huyết hiệu quả
• Giảm cân đáng kể (5-15%)
• Bảo vệ tim mạch và thận (giảm nguy cơ nhồi máu, suy thận)
• Dùng 1 lần/tuần (tiêm) hoặc uống hàng ngày
Thường chỉ định cho người thừa cân/béo phì có kèm bệnh tim mạch.
Tác dụng phụ phổ biến: Buồn nôn, nôn, tiêu chảy (thường giảm sau vài tuần).
Cần bác sĩ kê đơn và theo dõi.""",
        "keywords": ["GLP-1", "ozempic", "semaglutide", "rybelsus", "trulicity", "thuốc giảm cân tiểu đường", "thuốc tiêm tiểu đường"]
    },
    {
        "id": "faq_021",
        "category": "Biến chứng",
        "question": "Tiểu đường có ảnh hưởng đến sức khỏe tâm thần không?",
        "answer": """Có. Người bệnh tiểu đường có nguy cơ cao hơn:
• Trầm cảm: gấp 2 lần người bình thường
• Lo âu, stress mãn tính
• "Diabetes distress" - căng thẳng vì quản lý bệnh hàng ngày
Nguyên nhân: Biến động đường huyết ảnh hưởng não bộ, gánh nặng bệnh mãn tính.
Khuyến nghị:
• Sàng lọc tâm lý định kỳ (bác sĩ thường hỏi PHQ-9)
• Chia sẻ với gia đình, tham gia nhóm hỗ trợ
• Tập thể dục, thiền, ngủ đủ giúp cải thiện rõ rệt
• Nếu cần, dùng thuốc hoặc tư vấn tâm lý (an toàn với tiểu đường)
Kiểm soát tốt tâm thần cũng giúp kiểm soát đường huyết tốt hơn.""",
        "keywords": ["tiểu đường trầm cảm", "stress tiểu đường", "diabetes distress", "tâm lý tiểu đường", "tâm thần"]
    },
    {
        "id": "faq_022",
        "category": "Biến chứng",
        "question": "Tiểu đường có liên quan đến gan nhiễm mỡ không?",
        "answer": """Có, rất chặt chẽ. Khoảng 50-70% người type 2 bị gan nhiễm mỡ không do rượu (MASLD - trước gọi là NAFLD).
Nguyên nhân: Kháng insulin làm mỡ tích tụ ở gan.
Nguy cơ: Có thể tiến triển thành viêm gan, xơ gan.
Cách cải thiện:
• Giảm cân (mục tiêu 7-10%)
• Kiểm soát đường huyết và mỡ máu tốt
• Một số thuốc tiểu đường mới (GLP-1, SGLT2) có lợi cho gan
• Hạn chế rượu hoàn toàn
Nên siêu âm gan định kỳ và xét nghiệm men gan nếu có yếu tố nguy cơ.""",
        "keywords": ["gan nhiễm mỡ", "MASLD", "NAFLD", "tiểu đường gan", "mỡ gan"]
    }
]

# ============================================================
# CATEGORY MAPPING (cập nhật thêm nếu cần)
# ============================================================
CATEGORIES = {
    "Khái niệm": ["Khái niệm cơ bản về bệnh"],
    "Phân loại": ["Các loại bệnh tiểu đường"],
    "Triệu chứng": ["Dấu hiệu nhận biết"],
    "Nguyên nhân": ["Nguyên nhân và yếu tố nguy cơ"],
    "Chẩn đoán": ["Xét nghiệm và chẩn đoán"],
    "Điều trị": ["Điều trị và kiểm soát"],
    "Chế độ ăn": ["Dinh dưỡng và chế độ ăn"],
    "Vận động": ["Tập thể dục và vận động"],
    "Biến chứng": ["Biến chứng và tác hại"],
    "Theo dõi": ["Theo dõi và khám định kỳ"],
    "Phòng ngừa": ["Phòng ngừa và dự phòng"],
    "Hệ thống": ["Về hệ thống AI"],
    "Sử dụng": ["Hướng dẫn sử dụng"],
    "Hỗ trợ": ["Liên hệ và hỗ trợ"]
}

# ============================================================
# DEFAULT RESPONSES (giữ nguyên)
# ============================================================
DEFAULT_GREETING = """Xin chào! 👋 Tôi là trợ lý AI của Hệ thống Chẩn đoán Tiểu đường.
Tôi có thể giúp bạn:
• Tìm hiểu về bệnh tiểu đường
• Giải đáp thắc mắc về triệu chứng, chẩn đoán
• Hướng dẫn sử dụng hệ thống dự đoán
• Tư vấn về chế độ ăn uống, vận động
Bạn muốn hỏi gì? 😊"""

DEFAULT_NOT_FOUND = """Xin lỗi, tôi không tìm thấy thông tin chính xác cho câu hỏi của bạn.
Bạn có thể:
• Hỏi về: triệu chứng, nguyên nhân, chẩn đoán, điều trị tiểu đường
• Hỏi về hệ thống: cách dùng, độ chính xác
• Liên hệ hỗ trợ: support@diabetesdiagnosis.com
Hoặc thử đặt câu hỏi khác? 🤔"""

OUT_OF_SCOPE = """Xin lỗi, câu hỏi này nằm ngoài phạm vi của tôi. Tôi chỉ có thể trả lời về:
• Bệnh tiểu đường (triệu chứng, nguyên nhân, điều trị...)
• Hệ thống dự đoán AI của chúng tôi
Nếu bạn có thắc mắc y tế cụ thể, vui lòng tham khảo bác sĩ. 🏥"""