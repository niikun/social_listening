# LLM100人に聞きました - インストール手順

## 🚀 クイックスタート

### 方法1: 自動インストールスクリプト（推奨）

```bash
# インストールスクリプトを実行
python install.py

# アプリを起動
streamlit run app.py
```

### 方法2: setup.pyを使用

```bash
# 開発環境でのインストール
pip install -e .

# 本番環境でのインストール
pip install .

# アプリを起動
streamlit run app.py
```

### 方法3: requirements.txtを使用

```bash
# 必要なライブラリをインストール
pip install -r requirements.txt

# アプリを起動
streamlit run app.py
```

## 📦 必要なライブラリ

### 必須ライブラリ
- **streamlit**: Webアプリフレームワーク
- **pandas**: データ処理
- **numpy**: 数値計算
- **plotly**: グラフ作成
- **openai**: GPT-4o-mini API
- **tiktoken**: トークン数計算
- **duckduckgo-search**: 無料Web検索 🦆
- **requests**: HTTP通信

### オプション（高度な分析用）
- **matplotlib**: グラフ作成
- **seaborn**: 統計グラフ
- **wordcloud**: ワードクラウド
- **mecab-python3**: 日本語形態素解析

## 🔧 個別インストール

### DuckDuckGo検索のみインストール
```bash
pip install duckduckgo-search>=3.9.0
```

### OpenAI関連のみインストール
```bash
pip install openai>=1.0.0 tiktoken>=0.5.0
```

### 基本セットのみインストール
```bash
pip install streamlit pandas numpy plotly
```

## 🌐 環境構築

### 1. Python環境の確認
```bash
python --version  # Python 3.8以上が必要
```

### 2. 仮想環境の作成（推奨）
```bash
# venv使用
python -m venv llm_survey_env
source llm_survey_env/bin/activate  # Linux/Mac
# llm_survey_env\Scripts\activate  # Windows

# conda使用
conda create -n llm_survey python=3.10
conda activate llm_survey
```

### 3. ライブラリのインストール
```bash
# 自動インストール（推奨）
python install.py

# 手動インストール
pip install streamlit pandas numpy plotly openai tiktoken duckduckgo-search requests
```

## 🔑 APIキーの設定

### OpenAI APIキー

#### 方法1: 環境変数で設定
```bash
# Linux/Mac
export OPENAI_API_KEY="your_api_key_here"

# Windows
set OPENAI_API_KEY=your_api_key_here
```

#### 方法2: アプリ内で設定
1. アプリを起動
2. サイドバーの「OpenAI API Key」フィールドに入力

#### APIキーの取得方法
1. [OpenAI Platform](https://platform.openai.com) にアクセス
2. アカウント作成・ログイン
3. API Keys ページでキーを作成
4. キーをコピーして設定

## 🦆 DuckDuckGo検索の確認

### インストール確認
```python
python -c "from duckduckgo_search import DDGS; print('DuckDuckGo OK')"
```

### アプリでの確認
- ✅ サイドバーに「DuckDuckGo検索利用可能」と表示
- ❌ 「模擬Web検索（デモ）」と表示される場合は未インストール

## 🐛 トラブルシューティング

### よくある問題

#### 1. DuckDuckGoが使えない
```bash
pip install --upgrade duckduckgo-search
```

#### 2. Streamlitが起動しない
```bash
pip install --upgrade streamlit
streamlit --version
```

#### 3. OpenAIライブラリエラー
```bash
pip install --upgrade openai tiktoken
```

#### 4. 権限エラー（Windows）
```bash
pip install --user [パッケージ名]
```

#### 5. 依存関係エラー
```bash
pip install --upgrade pip
pip install --force-reinstall [パッケージ名]
```

### エラー時の対処

#### ImportError: No module named 'xxx'
```bash
pip install xxx
```

#### ModuleNotFoundError
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 💰 コスト情報

### GPT-4o-mini料金
- **100回答**: 約1.2円
- **AI分析**: 約0.3円/回
- **DuckDuckGo検索**: 完全無料

### シミュレーション版
- **すべて無料**: APIキー不要で動作確認可能

## 🎯 動作確認

### 1. 基本動作テスト
```bash
streamlit run app.py
```

### 2. ブラウザでアクセス
```
http://localhost:8501
```

### 3. 機能確認
1. ペルソナ生成（10人）
2. シミュレーション調査実行
3. DuckDuckGo検索テスト
4. 結果の確認

## 📞 サポート

### 問題が解決しない場合
1. エラーメッセージを確認
2. Python・pipのバージョン確認
3. 仮想環境での実行を試行
4. 個別ライブラリの再インストール

### 成功確認
- ✅ アプリが正常に起動
- ✅ ペルソナ生成が完了
- ✅ DuckDuckGo検索が利用可能
- ✅ 調査実行・結果表示が正常

これで、DuckDuckGo検索を含むすべての機能が利用可能になります！