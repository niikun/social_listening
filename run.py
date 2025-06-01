#!/usr/bin/env python3
# run.py - アプリ実行スクリプト

import subprocess
import sys
import os
import webbrowser
import time

def main():
    print("LLM100人に聞きました - GPT-4o-mini版")
    print("=" * 40)
    
    # 環境確認
    if not os.path.exists('app.py'):
        print("ERROR: app.py が見つかりません")
        print("正しいディレクトリで実行してください")
        return
    
    # .envファイル確認
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_api_key_here' in content:
                print("WARNING: .envファイルでAPIキーを設定してください")
                print("シミュレーション版は設定なしでも利用可能です")
    
    print("\nStreamlitアプリを起動中...")
    print("ブラウザで http://localhost:8501 が開きます")
    print("アプリを終了するには Ctrl+C を押してください")
    print()
    
    try:
        # ブラウザを開く（少し遅延）
        import threading
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Streamlit起動
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        
    except KeyboardInterrupt:
        print("\nアプリを終了しました")
    except Exception as e:
        print(f"ERROR: エラーが発生しました: {e}")
        print("\n対処法:")
        print("1. 必要なパッケージのインストール: python setup.py")
        print("2. Streamlitの手動起動: streamlit run app.py")

if __name__ == "__main__":
    main()
