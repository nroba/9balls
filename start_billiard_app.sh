#!/bin/bash

# --- 設定 ---
APP_DIR="$HOME/9balls"  # FlaskアプリとDockerfileがあるディレクトリ
PORT_FLASK=10000
PORT_ADMINER=8080

echo "✅ Flaskビリヤード管理アプリ 起動スクリプト"

# --- Dockerがインストールされているか確認 ---
if ! command -v docker &> /dev/null; then
  echo "❌ Docker が見つかりません。先にインストールしてください。"
  exit 1
fi

# --- Dockerデーモンが動作しているか確認 ---
if ! systemctl is-active --quiet docker; then
  echo "🔄 Docker を起動します..."
  sudo systemctl start docker
fi

# --- docker compose が使えるか確認 ---
if ! docker compose version &> /dev/null; then
  echo "❌ docker compose が見つかりません。以下を実行してください："
  echo "    sudo apt install docker-compose-plugin"
  exit 1
fi

# --- アプリディレクトリに移動 ---
cd "$APP_DIR" || {
  echo "❌ ディレクトリ $APP_DIR が存在しません。パスを確認してください。"
  exit 1
}

echo "📁 ディレクトリ移動完了：$APP_DIR"

# --- コンテナをビルドして起動 ---
echo "🚀 アプリを起動します..."
docker compose build && docker compose up -d

# --- アクセス案内 ---
echo "🌐 アクセス情報："
echo "  - Flaskアプリ   → http://localhost:$PORT_FLASK"
echo "  - SQLiteブラウザ(Adminer) → http://localhost:$PORT_ADMINER"
