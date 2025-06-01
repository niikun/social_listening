#!/bin/bash
# run_app.sh - Unix/Linux/Mac用実行スクリプト

echo "LLM100人に聞きました - GPT-4o-mini版"
echo "========================================"
echo

# 必要ファイルの確認
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py が見つかりません"
    echo "正しいディレクトリで実行してください"
    exit 1
fi

# パッケージ確認
echo "必要なパッケージを確認中..."
python3 -c "import streamlit, pandas, plotly, openai, tiktoken" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: 必要なパッケージが不足しています"
    echo "インストール中..."
    pip3 install -r requirements.txt
fi

# .env確認
if [ -f ".env" ]; then
    if grep -q "your_api_key_here" .env; then
        echo
        echo "WARNING: .envファイルでAPIキーを設定してください"
        echo "シミュレーション版は設定なしでも利用可能です"
        echo
    fi
fi

echo
echo "Streamlitアプリを起動中..."
echo "ブラウザで http://localhost:8501 が開きます"
echo "アプリを終了するには Ctrl+C を押してください"
echo

# ブラウザを開く（バックグラウンド）
(sleep 3 && open http://localhost:8501 2>/dev/null || xdg-open http://localhost:8501 2>/dev/null) &

# Streamlit起動
streamlit run app.py
