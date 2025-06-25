FROM python:3.11-slim

# 作業ディレクトリ設定
WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# アプリケーション実行
CMD ["python", "app.py"]
