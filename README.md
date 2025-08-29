# 週報作成マルチエージェントシステム

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

> Google Gemini APIとNotion APIを活用した、AI駆動の自動週報生成システム

## ✨ 特徴

- 🤖 **マルチエージェント構成**: 3つの専門エージェントが協働して高品質な週報を生成
- 📝 **自動コンテンツ抽出**: 議事録やNotionから重要な情報を自動抽出
- 🔍 **インテリジェントレビュー**: AIによる内容の完全性チェックと改善提案
- 👔 **上司視点のフィードバック**: 建設的なコメントと評価を自動生成
- 🚀 **簡単セットアップ**: uvを使った高速な環境構築

## 🏗️ システムアーキテクチャ

```
議事録・Notionデータ → 週報作成エージェント → レビューエージェント → 上司エージェント → 最終週報
                    ↓                    ↓                ↓
                 ドラフト生成           改善提案          評価・コメント
```

### エージェント構成

1. **📊 週報作成エージェント** (Report Writer Agent)
   - 議事録やNotionから情報を収集・分析
   - 成果、タスク、課題を整理してドラフト作成

2. **🔍 レビューエージェント** (Review Agent)
   - 内容の完全性と明確性をチェック
   - 具体的な改善提案を生成

3. **👔 上司エージェント** (Manager Agent)
   - 上司視点から建設的なフィードバック
   - 来週への期待とアドバイスを提供

## 🚀 クイックスタート

### 前提条件

- Python 3.9以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー
- Google API キー ([取得方法](https://ai.google.dev/))
- Notion API キー ([取得方法](https://developers.notion.com/))

### インストール

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/your-username/manager-agent.git
   cd manager-agent
   ```

2. **仮想環境を作成**
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # または
   .venv\Scripts\activate     # Windows
   ```

3. **依存関係をインストール**
   ```bash
   uv pip install -e .
   ```

4. **環境変数を設定**
   ```bash
   cp .env.example .env
   # .envファイルを編集してAPIキーを設定
   ```

### 設定

`.env`ファイルに以下の環境変数を設定：

```env
# Google API設定
GOOGLE_API_KEY=your_google_api_key_here

# Notion API設定 (オプション)
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# アプリケーション設定
LOG_LEVEL=INFO
MODE=development
```

## 📋 使用方法

### 基本実行

```bash
# サンプルデータで実行
python main.py

# 議事録ファイルを指定して実行
python main.py --notes meeting1.md meeting2.md

# Notion連携を無効化して実行
python main.py --no-notion

# 本番モードで実行
python main.py --mode production
```

### 出力例

実行すると以下のような週報が `output/` フォルダに生成されます：

```markdown
# 週報 - 2024年12月20日

## 今週の成果
- プロジェクトAのフェーズ1完了
- リリース日を12月25日に決定

## 進捗状況
### 完了タスク
- ドキュメント更新
- テスト環境の準備

### 課題・懸念事項
- パフォーマンステストで目標値未達
- リソース不足の懸念あり

---

## レビュー結果
**スコア**: 8/10

### 改善提案
- 具体的な数値目標の明記
- 次週のアクションプランの追加

---

## 上司コメント
### 総評
フェーズ1の完了、お疲れ様でした。スケジュール通りの進捗で安心しています。

### 来週への期待
パフォーマンス改善に集中し、リリースに向けて最後の調整を頑張ってください。
```

## 🛠️ 開発

### コード品質チェック

```bash
# リントチェック
uv run ruff check .

# 自動修正
uv run ruff check --fix .

# フォーマット
uv run ruff format .

# 型チェック
uv run mypy .
```

### テスト実行

```bash
# 単体テスト
uv run pytest tests/

# 統合テスト
uv run pytest tests/integration/

# カバレッジ付きテスト
uv run pytest --cov=agents --cov=tools --cov=config tests/
```

## 📁 プロジェクト構造

```
manager-agent/
├── agents/              # エージェント実装
│   ├── base_agent.py    # ベースエージェントクラス
│   ├── report_writer.py # 週報作成エージェント
│   ├── reviewer.py      # レビューエージェント
│   └── manager.py       # 上司エージェント
├── tools/               # ユーティリティツール
│   ├── notion_tools.py  # Notion API連携
│   └── document_parser.py # 議事録パーサー
├── config/              # 設定ファイル
│   └── agent_config.py  # エージェント設定
├── tests/               # テストファイル
├── output/              # 生成された週報の保存先
├── main.py              # メインエントリーポイント
├── pyproject.toml       # プロジェクト設定
└── README.md            # このファイル
```

## ⚙️ 設定とカスタマイズ

### エージェント設定

`config/agent_config.py`でエージェントの動作をカスタマイズできます：

```python
REPORT_WRITER_CONFIG = AgentConfig(
    name="ReportWriter",
    model="gemini-2.0-flash-exp",
    temperature=0.7,
    max_tokens=4096,
    system_prompt="..."
)
```

### 週報テンプレート

デフォルトのテンプレートは以下の構成です：

- 今週の成果
- 進捗状況（完了タスク・進行中タスク）  
- 課題・懸念事項
- 来週の計画
- その他連絡事項

## 🔧 トラブルシューティング

### よくある問題

#### API認証エラー
```
ValueError: GOOGLE_API_KEY is not set
```
**解決方法**: `.env`ファイルに正しいAPIキーが設定されているか確認

#### Notion連携エラー
```
Error fetching Notion updates: Unauthorized
```
**解決方法**: 
- Notion APIキーの権限を確認
- データベースIDが正しく設定されているか確認

#### メモリ不足エラー
**解決方法**: `agent_config.py`で`max_tokens`を調整

### ログ出力

詳細なデバッグには環境変数でログレベルを調整：

```bash
export LOG_LEVEL=DEBUG
python main.py
```

## 🚧 今後の拡張予定

- [ ] Slack連携機能
- [ ] 週報の自動送信機能  
- [ ] 過去の週報との比較分析
- [ ] チーム全体の週報集約機能
- [ ] WebUI の提供
- [ ] Docker対応

## 🤝 貢献

プルリクエストやIssueは大歓迎です！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

## 🙏 謝辞

- [Google Generative AI](https://ai.google.dev/) - 高性能なLLMAPI
- [Notion API](https://developers.notion.com/) - データ連携機能  
- [uv](https://docs.astral.sh/uv/) - 高速パッケージ管理
- [ruff](https://docs.astral.sh/ruff/) - 高速リンター・フォーマッター

## 📚 参考資料

- [Google Generative AI Documentation](https://ai.google.dev/)
- [Notion API Documentation](https://developers.notion.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [uv Documentation](https://docs.astral.sh/uv/)

---

<div align="center">

**⭐ このプロジェクトが役に立った場合は、スターをつけていただけると嬉しいです！**

</div>
