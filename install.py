#!/usr/bin/env python3
"""
LLM100人に聞きました - 超簡単インストールスクリプト
PDF出力対応版の全ライブラリを自動インストール
"""

import subprocess
import sys
import os
import platform
import datetime

def run_command(command):
    """コマンドを実行"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version():
    """Pythonバージョンチェック"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"{version.major}.{version.minor}"
    return True, f"{version.major}.{version.minor}.{version.micro}"

def main():
    print("🚀 LLM100人に聞きました - PDF出力対応版インストール")
    print("=" * 65)
    
    # Python版本チェック
    print("🐍 Step 1: Python バージョンチェック...")
    is_compatible, version = check_python_version()
    if is_compatible:
        print(f"✅ Python {version} (対応済み)")
    else:
        print(f"❌ Python {version} (Python 3.8以上が必要)")
        print("Pythonを最新版にアップグレードしてください")
        return
    
    # OS情報表示
    os_info = platform.system()
    print(f"💻 OS: {os_info} {platform.release()}")
    
    # Step 1: pipのアップグレード
    print("\n📦 Step 2: pip をアップグレード中...")
    success, output = run_command(f"{sys.executable} -m pip install --upgrade pip")
    if success:
        print("✅ pip アップグレード完了")
    else:
        print("⚠️  pip アップグレード失敗（続行します）")
        print(f"   詳細: {output[:100]}...")
    
    # Step 2: 基本ツールをインストール
    print("\n📦 Step 3: 基本ツールをインストール中...")
    basic_tools = ["setuptools", "wheel", "build"]
    
    for tool in basic_tools:
        print(f"   ⬇️  {tool}")
        success, output = run_command(f"{sys.executable} -m pip install {tool}")
        if success:
            print(f"   ✅ {tool}")
        else:
            print(f"   ⚠️  {tool} (警告)")
    
    # Step 3: 必要なライブラリを一括インストール
    packages = [
        # Streamlit関連
        "streamlit>=1.28.0",
        
        # データ処理
        "pandas>=1.5.0", 
        "numpy>=1.24.0",
        
        # 可視化
        "plotly>=5.15.0",
        "matplotlib>=3.6.0",
        
        # AI/LLM関連
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
        
        # 検索機能
        "duckduckgo-search>=3.9.0",
        "requests>=2.31.0",
        
        # PDF出力関連
        "reportlab>=4.0.0",
        
        # その他
        "python-dateutil>=2.8.0",
        "aiohttp>=3.8.0",
 
    ]
    
    print(f"\n📦 Step 4: 必要なライブラリ({len(packages)}個)をインストール中...")
    print("   これには数分かかる場合があります...")
    
    # 一括インストール試行
    package_list = " ".join([f'"{pkg}"' for pkg in packages])
    command = f"{sys.executable} -m pip install {package_list}"
    
    print("⬇️  一括インストール実行中...")
    success, output = run_command(command)
    
    if success:
        print("✅ 一括インストール完了！")
    else:
        print("⚠️  一括インストール失敗。個別インストールに切り替えます...")
        
        # 個別インストール
        failed_packages = []
        for package in packages:
            print(f"   ⬇️  {package}")
            success, output = run_command(f"{sys.executable} -m pip install \"{package}\"")
            if success:
                print(f"   ✅ {package}")
            else:
                print(f"   ❌ {package}")
                failed_packages.append(package)
                print(f"      エラー: {output[:100]}...")
        
        if failed_packages:
            print(f"\n❌ {len(failed_packages)}個のパッケージが失敗:")
            for pkg in failed_packages:
                print(f"   - {pkg}")
            print("\n💡 失敗したパッケージは手動インストールしてください:")
            print(f"pip install {' '.join(failed_packages)}")
    
    # Step 4: インストール確認
    print("\n📦 Step 5: インストール確認中...")
    
    test_imports = [
        ("streamlit", "Streamlit", True),
        ("pandas", "Pandas", True),
        ("numpy", "NumPy", True),
        ("plotly", "Plotly", True),
        ("matplotlib", "Matplotlib", True),
        ("openai", "OpenAI", False),
        ("tiktoken", "Tiktoken", False),
        ("duckduckgo_search", "DuckDuckGo Search", False),
        ("requests", "Requests", True),
        ("reportlab", "ReportLab (PDF出力)", True),
    ]
    
    success_count = 0
    critical_missing = []
    
    for module, name, is_critical in test_imports:
        try:
            __import__(module)
            print(f"✅ {name}")
            success_count += 1
        except ImportError:
            if is_critical:
                print(f"❌ {name} (重要)")
                critical_missing.append(name)
            else:
                print(f"⚠️  {name} (オプショナル)")
    
    print(f"\n📊 結果: {success_count}/{len(test_imports)} パッケージが利用可能")
    
    # Step 5: 重要機能の特別確認
    print("\n🔍 Step 6: 重要機能の動作確認...")
    
    # Streamlit確認
    try:
        import streamlit as st
        print("✅ Streamlit: 完全に利用可能")
    except ImportError:
        print("❌ Streamlit: 利用不可（アプリが起動できません）")
        critical_missing.append("Streamlit")
    
    # PDF出力確認
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        print("✅ PDF出力: 完全に利用可能")
    except ImportError:
        print("❌ PDF出力: 利用不可")
        print("   手動インストール: pip install reportlab matplotlib")
    
    # DuckDuckGo検索確認
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        print("✅ DuckDuckGo検索: インストール済み")
        
        # 簡単なテスト検索
        try:
            results = list(ddgs.text("test", max_results=1))
            if results:
                print("✅ DuckDuckGo検索: 動作テスト成功")
            else:
                print("⚠️  DuckDuckGo検索: インストール済みだが検索結果なし")
        except Exception as e:
            print("⚠️  DuckDuckGo検索: インストール済みだが検索テスト失敗")
            print(f"   エラー: {str(e)[:100]}...")
            
    except ImportError:
        print("⚠️  DuckDuckGo検索: 利用不可（オプショナル機能）")
        print("   手動インストール: pip install duckduckgo-search")
    
    # OpenAI確認
    try:
        import openai
        print("✅ OpenAI: インストール済み（APIキーは別途設定）")
    except ImportError:
        print("⚠️  OpenAI: 利用不可（GPT-4o-mini機能が使用不可）")
        print("   手動インストール: pip install openai")
    
    # データ処理確認
    try:
        import pandas as pd
        import numpy as np
        import plotly.express as px
        print("✅ データ処理・可視化: 完全に利用可能")
    except ImportError as e:
        print(f"❌ データ処理・可視化: 一部利用不可 ({e})")
        critical_missing.append("データ処理ライブラリ")
    
    # アプリファイル確認
    print("\n📁 Step 7: アプリファイル確認...")
    if os.path.exists("app.py"):
        print("✅ app.py: 見つかりました")
        
        # ファイルサイズチェック
        file_size = os.path.getsize("app.py")
        if file_size > 10000:  # 10KB以上
            print(f"✅ app.py: サイズ正常 ({file_size:,} bytes)")
        else:
            print(f"⚠️  app.py: サイズが小さいです ({file_size:,} bytes)")
            print("   完全版のapp.pyをダウンロードしてください")
    else:
        print("❌ app.py: 見つかりません")
        print("   完全版のapp.pyを同じフォルダに配置してください")
    
    # 最終結果とガイダンス
    print("\n" + "=" * 65)
    
    if success_count >= 8 and not critical_missing:
        print("🎉 インストール完了！アプリを起動できます")
        
        print("\n🚀 アプリ起動コマンド:")
        print("streamlit run app.py")
        
        print("\n🌐 アクセス方法:")
        print("1. 上記コマンド実行後、自動でブラウザが開きます")
        print("2. または http://localhost:8501 にアクセス")
        
        print("\n⚙️ 初期設定:")
        print("1. サイドバーでOpenAI API Keyを設定（有料版使用時）")
        print("2. 「ペルソナ」タブでペルソナを生成")
        print("3. 「調査」タブで質問を設定して実行")
        print("4. 「結果」タブでPDFレポートをダウンロード")
        
        print("\n💰 コスト情報:")
        print("- シミュレーション版: 完全無料")
        print("- GPT-4o-mini版: 100回答約1.2円")
        print("- AI分析: 約1.8円/回")
        print("- DuckDuckGo検索: 完全無料")
        print("- PDF出力: 無料")
        
        print("\n📋 主要機能:")
        print("- 統計的に正確なペルソナ生成")
        print("- 100文字制限の簡潔な回答")
        print("- 2400文字の創造的AI分析")
        print("- 最新情報検索（DuckDuckGo）")
        print("- 包括的なPDFレポート出力")
        print("- CSV/JSONデータエクスポート")
        
    elif critical_missing:
        print("⚠️  重要なライブラリが不足しています")
        print("以下の重要コンポーネントを手動インストールしてください:")
        for component in critical_missing:
            print(f"   - {component}")
        
        print("\n🔧 修復コマンド:")
        print("pip install streamlit pandas numpy plotly matplotlib reportlab")
        
    else:
        print("⚠️  一部のライブラリが不足していますが、基本機能は利用可能です")
        
        print("\n📦 推奨追加インストール:")
        print("pip install openai tiktoken duckduckgo-search")
        
        print("\n⚠️  制限事項:")
        if "OpenAI" in [name for module, name, critical in test_imports if module == "openai"]:
            print("- GPT-4o-mini機能は利用不可（シミュレーション版のみ）")
        if "DuckDuckGo Search" in [name for module, name, critical in test_imports if module == "duckduckgo_search"]:
            print("- 最新情報検索機能は利用不可")
    
    print("\n💡 トラブルシューティング:")
    print("- エラーが発生した場合は、Python環境を確認してください")
    print("- 仮想環境の使用を推奨します: python -m venv venv")
    print("- Windowsの場合: venv\\Scripts\\activate")
    print("- Mac/Linuxの場合: source venv/bin/activate")
    
    print("\n📚 サポート:")
    print("- 詳細なエラーログが必要な場合は --verbose オプションを使用")
    print("- 最新版のダウンロード: GitHub リポジトリを確認")
    
    # 環境情報の保存
    try:
        with open("install_log.txt", "w", encoding="utf-8") as f:
            f.write(f"LLM100人に聞きました インストールログ\n")
            f.write(f"実行日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python: {version}\n")
            f.write(f"OS: {os_info} {platform.release()}\n")
            f.write(f"成功: {success_count}/{len(test_imports)}\n")
            if critical_missing:
                f.write(f"不足: {', '.join(critical_missing)}\n")
            f.write("\n詳細:\n")
            for module, name, critical in test_imports:
                try:
                    __import__(module)
                    f.write(f"✅ {name}\n")
                except ImportError:
                    f.write(f"❌ {name}\n")
        
        print(f"\n📄 インストールログを保存しました: install_log.txt")
        
    except Exception as e:
        print(f"⚠️  ログ保存失敗: {e}")

def check_install_verbose():
    """詳細インストールチェック"""
    print("\n🔍 詳細診断モード")
    print("-" * 40)
    
    # より詳細なライブラリチェック
    detailed_checks = [
        ("streamlit", "import streamlit; print(streamlit.__version__)"),
        ("pandas", "import pandas; print(pandas.__version__)"),
        ("numpy", "import numpy; print(numpy.__version__)"),
        ("plotly", "import plotly; print(plotly.__version__)"),
        ("openai", "import openai; print(openai.__version__)"),
        ("reportlab", "import reportlab; print(reportlab.Version)"),
        ("matplotlib", "import matplotlib; print(matplotlib.__version__)"),
    ]
    
    for name, check_code in detailed_checks:
        try:
            result = subprocess.run(
                [sys.executable, "-c", check_code], 
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {name}: {version}")
            else:
                print(f"❌ {name}: インポートエラー")
        except Exception as e:
            print(f"❌ {name}: {e}")

if __name__ == "__main__":
    
    # コマンドライン引数チェック
    if len(sys.argv) > 1 and sys.argv[1] == "--verbose":
        main()
        check_install_verbose()
    else:
        main()
        
    print(f"\n⏰ 完了時刻: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 お疲れさまでした！")