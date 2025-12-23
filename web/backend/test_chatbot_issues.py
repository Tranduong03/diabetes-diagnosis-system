"""
FULL TEST – COUNT CORRECT ANSWERS
Đếm số câu chatbot trả lời đúng dựa trên confidence threshold
Phù hợp debug + báo cáo đồ án
"""

from ai.chatbot import get_semantic_chatbot


# ======================
# CONFIG
# ======================
CONFIDENCE_THRESHOLD = 0.5   # bạn có thể thử 0.45 / 0.6


def get_test_queries():
    """Danh sách câu hỏi PARAPHRASE – in-scope"""
    return [

        # ===== Khái niệm =====
        "Tiểu đường là bệnh như thế nào?",
        "Bệnh đái tháo đường nghĩa là gì?",
        "Tiểu đường thực chất là bệnh gì?",
        "Diabetes mellitus là bệnh gì?",
        "Tiểu đường xảy ra khi nào?",

        # ===== Phân loại =====
        "Bệnh tiểu đường có mấy loại?",
        "Tiểu đường gồm những loại nào?",
        "Tiểu đường có bao nhiêu type?",
        "Tiểu đường type 1 và type 2 khác nhau thế nào?",

        # ===== Triệu chứng =====
        "Dấu hiệu nhận biết bệnh tiểu đường là gì?",
        "Người bị tiểu đường thường có biểu hiện gì?",
        "Triệu chứng ban đầu của tiểu đường là gì?",
        "Tôi hay khát nước và đi tiểu nhiều có sao không?",
        "Ăn nhiều nhưng vẫn sụt cân nhanh",
        "Vết thương lâu lành có phải do tiểu đường không?",

        # ===== Nguyên nhân =====
        "Vì sao lại mắc bệnh tiểu đường?",
        "Nguyên nhân nào gây ra tiểu đường?",
        "Bệnh tiểu đường do đâu mà có?",
        "Tiểu đường có di truyền không?",
        "Béo phì có làm tăng nguy cơ tiểu đường không?",

        # ===== Chẩn đoán =====
        "Làm sao để biết mình bị tiểu đường?",
        "Kiểm tra tiểu đường bằng cách nào?",
        "Cần xét nghiệm gì để phát hiện tiểu đường?",
        "Đường huyết bao nhiêu thì được coi là tiểu đường?",
        "Xét nghiệm HbA1c dùng để làm gì?",

        # ===== Điều trị =====
        "Bệnh tiểu đường có chữa khỏi được không?",
        "Tiểu đường có thể khỏi hẳn không?",
        "Tiểu đường type 2 có đảo ngược được không?",
        "Làm sao để kiểm soát bệnh tiểu đường?",

        # ===== Chế độ ăn =====
        "Người tiểu đường nên ăn gì?",
        "Chế độ ăn cho người bị tiểu đường như thế nào?",
        "Tiểu đường có được ăn cơm không?",
        "Người tiểu đường cần kiêng ăn gì?",

        # ===== Vận động =====
        "Người tiểu đường có nên tập thể dục không?",
        "Tập thể thao có giúp giảm đường huyết không?",
        "Bị tiểu đường có cần vận động không?",

        # ===== Biến chứng =====
        "Tiểu đường có gây biến chứng gì không?",
        "Bệnh tiểu đường nguy hiểm ở điểm nào?",
        "Tiểu đường lâu ngày có hậu quả gì?",
        "Tiểu đường có gây mù mắt không?",

        # ===== Theo dõi =====
        "Người bị tiểu đường cần theo dõi những gì?",
        "Bao lâu nên kiểm tra đường huyết một lần?",
        "Bao lâu nên xét nghiệm HbA1c?",

        # ===== Hệ thống AI =====
        "Hệ thống dự đoán tiểu đường này hoạt động như thế nào?",
        "AI trong hệ thống phân tích dữ liệu ra sao?",
        "PhoBERT được dùng để làm gì trong chatbot?",

        # ===== Độ chính xác =====
        "Kết quả dự đoán có chính xác không?",
        "Dự đoán của hệ thống có đáng tin không?",
        "Tôi có thể tin vào kết quả này không?",

        # ===== Sử dụng =====
        "Cách sử dụng hệ thống dự đoán như thế nào?",
        "Hướng dẫn dùng chatbot này ra sao?",

        # ===== Phòng ngừa =====
        "Làm sao để phòng ngừa bệnh tiểu đường?",
        "Có cách nào tránh bị tiểu đường không?",

        # ===== Hỗ trợ =====
        "Tôi cần hỗ trợ thì liên hệ ở đâu?",
        "Gặp sự cố với hệ thống thì làm sao?",
    ]


def run_accuracy_test():
    chatbot = get_semantic_chatbot()
    test_queries = get_test_queries()

    total = len(test_queries)
    correct = 0
    failed = []

    print("=" * 80)
    print("CHATBOT ACCURACY TEST")
    print("=" * 80)
    print(f"Total test queries: {total}")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print("=" * 80)

    for idx, query in enumerate(test_queries, 1):
        response = chatbot.chat(query)

        success = (
            response.get("success") is True
            and response.get("confidence", 0) >= CONFIDENCE_THRESHOLD
        )

        if success:
            correct += 1
            status = "✅ CORRECT"
        else:
            status = "❌ WRONG"
            failed.append({
                "query": query,
                "confidence": response.get("confidence"),
                "source": response.get("source"),
                "category": response.get("category"),
            })

        print(f"\n[{idx}] {status}")
        print(f"Q: {query}")
        print(f"Confidence: {response.get('confidence')}")
        print(f"Category: {response.get('category')}")
        print(f"Source: {response.get('source')}")

    accuracy = correct / total * 100

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print(f"Correct answers : {correct}/{total}")
    print(f"Accuracy        : {accuracy:.2f}%")

    if failed:
        print("\n❌ FAILED QUERIES:")
        for f in failed:
            print(
                f"- {f['query']} "
                f"(conf={f['confidence']}, "
                f"cat={f['category']}, "
                f"source={f['source']})"
            )


if __name__ == "__main__":
    run_accuracy_test()
