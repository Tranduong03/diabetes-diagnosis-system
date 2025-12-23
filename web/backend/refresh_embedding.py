"""
Refresh FAQ Embeddings
Chạy script này sau khi thêm/sửa keywords trong knowledge base
"""

if __name__ == "__main__":
    print("\n" + "="*80)
    print("REFRESHING FAQ EMBEDDINGS")
    print("="*80 + "\n")
    
    from ai.chatbot import get_semantic_chatbot
    
    print("Loading chatbot...")
    chatbot = get_semantic_chatbot()
    
    print("\nRefreshing embeddings with new keywords...")
    chatbot.refresh_embeddings()
    
    print("\n" + "="*80)
    print("✅ EMBEDDINGS REFRESHED SUCCESSFULLY!")
    print("="*80)
    
    print("\nYou can now test with:")
    print("  python test_chatbot_issues.py")
    print("\nOr start the server:")
    print("  uvicorn main:app --reload")