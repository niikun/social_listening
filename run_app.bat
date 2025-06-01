@echo off
chcp 65001 >nul
title LLM100人に聞きました - GPT-4o-mini版
echo.
echo LLM100人に聞きました - GPT-4o-mini版
echo ========================================
echo.

REM 必要ファイルの確認
if not exist app.py (
    echo ERROR: app.py が見つかりません
    echo 正しいディレクトリで実行してください
    pause
    exit /b 1
)

REM パッケージ確認
echo 必要なパッケージを確認中...
python -c "import streamlit, pandas, plotly, openai, tiktoken" 2>nul
if errorlevel 1 (
    echo WARNING: 必要なパッケージが不足しています
    echo インストール中...
    pip install -r requirements.txt
)

REM .env確認
if exist .env (
    findstr /C:"your_api_key_here" .env >nul
    if not errorlevel 1 (
        echo.
        echo WARNING: .envファイルでAPIキーを設定してください
        echo シミュレーション版は設定なしでも利用可能です
        echo.
    )
)

echo.
echo Streamlitアプリを起動中...
echo ブラウザで http://localhost:8501 が開きます
echo アプリを終了するには Ctrl+C を押してください
echo.

REM ブラウザを開く（少し遅延）
timeout /t 3 >nul
start http://localhost:8501

REM Streamlit起動
streamlit run app.py

pause
