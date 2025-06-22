# ベースイメージ
FROM python:3.10-slim

# 作業ディレクトリ作成
WORKDIR /app

# ファイルをコピー
COPY . .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# ポートを開放（Flaskが使う）
EXPOSE 10000

# アプリ起動
CMD ["python", "app.py"]
