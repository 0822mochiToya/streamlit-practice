# 神奈川県会場検索サイト

神奈川県内のスタジアム・アリーナ・ライブハウスを検索できる
Streamlit アプリです。

## 主な機能

- 会場名・種別による検索
- 会場の写真・概要・歴史の表示
- 主な利用実績の表示
- 会場ごとの口コミ投稿
- 会場写真の出典表示

## 起動方法

```shell
mise install
mise run install
streamlit run arena_app.py
```

ブラウザで次のURLを開きます。

```text
http://localhost:8501
```

## 必要な環境

- Python 3.14.6
- Streamlit
- mise（推奨）

## 開発環境

このプロジェクトでは、Python のバージョンとドキュメント用タスクを
[mise](https://mise.jdx.dev/) で管理します。

```shell
mise install
mise run install
streamlit run arena_app.py
```

## ドキュメントのバージョン公開

`main` ブランチに push すると、GitHub Actions がドキュメントを
GitHub Pages に公開します。

```shell
git push origin main
```

ローカルでドキュメントを確認する場合は、次を実行します。

```shell
mise run docs-serve
```

## 注意事項

掲載している写真・情報の著作権や利用条件を確認してください。
