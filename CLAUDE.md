# 週報作成マルチエージェントシステム

## プロジェクト概要
Google ADK (Agent Development Kit) を使用して、議事録やNotionのアップデート情報から自動的に週報を作成するマルチエージェントシステムを構築します。

## システムアーキテクチャ

### エージェント構成
1. **週報作成エージェント** (Report Writer Agent)
   - 議事録やNotionから情報を収集
   - 週報のドラフトを作成
   
2. **レビューエージェント** (Review Agent)
   - 週報の内容をレビュー
   - 改善点の提案
   
3. **上司エージェント** (Manager Agent)
   - 上司の視点から週報にコメント
   - フィードバックの提供

## 技術スタック
- **フレームワーク**: Google ADK Python
- **言語**: Python 3.9+
- **LLMモデル**: Gemini 2.0 Flash（推奨）
- **外部連携**: Notion API

## セットアップ手順

### 1. 環境構築
```bash
# ADKのインストール
pip install google-adk

# 開発用依存関係のインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定
```bash
# .envファイルを作成
GOOGLE_API_KEY=your_google_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
```

## プロジェクト構造
```
manager-agent/
├── agents/
│   ├── report_writer.py    # 週報作成エージェント
│   ├── reviewer.py          # レビューエージェント
│   └── manager.py           # 上司エージェント
├── tools/
│   ├── notion_tools.py      # Notion連携ツール
│   └── document_parser.py   # 議事録パーサー
├── config/
│   └── agent_config.py      # エージェント設定
├── main.py                  # メインエントリーポイント
├── requirements.txt         # 依存関係
└── .env                     # 環境変数
```

## 実装ガイドライン

### エージェント間の通信フロー
1. **Report Writer** が議事録とNotionからデータを収集
2. 週報ドラフトを生成してReviewerに送信
3. **Reviewer** がドラフトをレビューし、改善提案を返信
4. **Report Writer** が改善を反映した最終版を作成
5. **Manager** が最終版にコメントを追加

### 各エージェントの責務

#### Report Writer Agent
- **入力**: 議事録ファイル、Notion更新情報
- **処理**: 
  - 重要な成果物の抽出
  - タスクの進捗状況の整理
  - 課題と次週の計画の整理
- **出力**: 週報ドラフト（Markdown形式）

#### Review Agent
- **入力**: 週報ドラフト
- **処理**:
  - 内容の完全性チェック
  - 文章の明確性評価
  - 改善提案の生成
- **出力**: レビューコメントと改善提案

#### Manager Agent
- **入力**: 最終版週報
- **処理**:
  - 成果の評価
  - 建設的なフィードバック
  - 次週への期待とアドバイス
- **出力**: 上司コメント

## 開発コマンド

### エージェントの起動
```bash
# 開発サーバーの起動
python main.py --mode development

# 本番実行
python main.py --mode production
```

### テスト実行
```bash
# 単体テスト
pytest tests/

# 統合テスト
pytest tests/integration/
```

### リント・フォーマット
```bash
# コードフォーマット
black .

# リント実行
ruff check .

# 型チェック
mypy .
```

## 週報テンプレート
```markdown
# 週報 - [日付]

## 今週の成果
- [成果1]
- [成果2]

## 進捗状況
### 完了タスク
- [タスク1]
- [タスク2]

### 進行中タスク
- [タスク1] (進捗: XX%)
- [タスク2] (進捗: XX%)

## 課題・懸念事項
- [課題1]
- [課題2]

## 来週の計画
- [計画1]
- [計画2]

## その他連絡事項
- [連絡事項]
```

## トラブルシューティング

### よくある問題
1. **API認証エラー**: 環境変数が正しく設定されているか確認
2. **Notion連携エラー**: DATABASE_IDとAPI_KEYの権限を確認
3. **メモリ不足**: エージェントのコンテキストサイズを調整

## 今後の拡張予定
- [ ] Slack連携機能
- [ ] 週報の自動送信機能
- [ ] 過去の週報との比較分析
- [ ] チーム全体の週報集約機能

## 参考資料
- [Google ADK Documentation](https://github.com/google/adk-python)
- [Notion API Documentation](https://developers.notion.com/)
- [Gemini API Documentation](https://ai.google.dev/)