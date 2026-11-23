import base64
import html
import mimetypes
from pathlib import Path
from urllib.parse import quote

import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="神奈川県内会場検索サイト",
    page_icon="assets/arena-photo.png",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #eef6f7;
    }
    [data-testid="stHeader"] {
        display: none;
    }
    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #cbd5e1;
    }
    h1, h2, h3 {
        color: #0f172a !important;
        letter-spacing: -0.02em;
    }
    .site-hero {
        padding: 1.25rem 0 1rem;
        margin-bottom: 1.25rem;
    }
    .site-hero-kicker {
        margin: 0 0 0.4rem;
        color: #0f766e;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }
    .site-hero-title {
        margin: 0;
        color: #0f172a;
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.1;
    }
    .site-hero-description {
        margin: 0.75rem 0 0;
        color: #475569;
        font-size: 1.05rem;
    }
    .st-key-search-panel {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 100;
        width: auto;
        padding: 0.5rem 1rem 0.25rem;
        margin: 0;
        background: #f8fafc;
        border-bottom: 1px solid #cbd5e1;
        box-shadow: none;
    }
    .st-key-search-panel input,
    .st-key-search-panel [data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #0f172a !important;
        border-color: #94a3b8 !important;
    }
    .st-key-search-panel input {
        padding-left: 2.5rem !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2364758b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m20 20-4-4'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 0.8rem center !important;
        background-size: 1.2rem !important;
    }
    .st-key-search-panel input::placeholder {
        color: #64748b !important;
        opacity: 1;
    }
    .st-key-search-panel [data-testid="stPopover"] > button {
        min-height: 2.5rem;
        padding: 0.35rem 0.75rem;
        font-size: 1rem;
    }
    .back-to-list {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        margin: 0.25rem 0 1.25rem;
        color: #0f766e;
        font-size: 1rem;
        font-weight: 700;
        text-decoration: none;
        transition: color 0.2s, transform 0.2s;
    }
    .back-to-list:hover {
        color: #1d4ed8;
        transform: translateX(-0.2rem);
    }
    [data-testid="stCaptionContainer"] {
        color: #64748b;
    }
    div[data-testid="stButton"] > button {
        min-height: 3.5rem;
        padding: 0.65rem 1.1rem;
        border: 1px solid #cbd5e1;
        border-radius: 0.75rem;
        background-color: #ffffff;
        color: #0f172a;
        text-align: left;
        transition: border-color 0.2s, box-shadow 0.2s, color 0.2s;
    }
    div[data-testid="stButton"] > button p {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
    .st-key-search-panel [data-testid="stPopover"] button {
        font-size: 0.75rem !important;
        line-height: 1.1 !important;
    }
    .st-key-category-options [data-testid="stButton"] > button p,
    .st-key-category-options [data-testid="stButton"] button p {
        font-size: 0.75rem !important;
        line-height: 1.1 !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #0f766e;
        color: #0f766e;
        box-shadow: 0 0.25rem 0.75rem rgba(15, 118, 110, 0.15);
    }
    .venue-image-link {
        display: block;
        overflow: hidden;
        border-radius: 0.75rem;
        position: relative;
    }
    .venue-image-link::after {
        content: "クリックして詳細を見る";
        position: absolute;
        inset: auto 0 0;
        padding: 0.55rem;
        background: rgba(15, 23, 42, 0.75);
        color: #ffffff;
        font-size: 0.9rem;
        text-align: center;
        opacity: 0;
        transform: translateY(100%);
        transition: opacity 0.2s, transform 0.2s;
    }
    .venue-image-link:hover::after {
        opacity: 1;
        transform: translateY(0);
    }
    .venue-image-link img {
        display: block;
        transition: transform 0.2s, filter 0.2s;
    }
    .venue-image-link:hover img {
        filter: brightness(0.82) saturate(1.15);
        transform: scale(1.04);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 1. データの準備（詳細情報・歴史・過去実績・複数の写真URLなどを追加）
if "venues" not in st.session_state:
    st.cache_data.clear()

    @st.cache_data
    def load_venues():
        import json
        with open(Path("venues.json"), "r", encoding="utf-8") as venue_file:
            return json.load(venue_file)

    st.session_state.venues = load_venues()

# 以前の初期データに含まれていた架空レビューだけを削除し、投稿済みの口コミは残す
fake_reviews = {
    "国内最大級の収容人数を誇る野外スタジアム。大規模なライブやスポーツの定番。",
    "横浜スタジアム（ハマスタ）。野球だけでなく野外ライブの熱気もすごい。",
    "定番のアリーナ会場。まわりに飲食店やホテルが多くてアクセス抜群。",
    "比較的新しく、スタンド席との距離が近くてステージが見やすい。",
    "ドリンク代が電子マネー対応でスムーズ。段差があって見やすいライブハウス。",
}
for venue in st.session_state.venues:
    venue["reviews"] = [
        review for review in venue.get("reviews", []) if review not in fake_reviews
    ]

# 画像をリンク化して表示するためのヘルパー
def render_venue_image(image_path, venue_name):
    if image_path.startswith(("http://", "https://")):
        image_src = image_path
    else:
        image_file = Path(image_path)
        image_data = base64.b64encode(image_file.read_bytes()).decode("ascii")
        image_type = mimetypes.guess_type(image_file.name)[0] or "image/png"
        image_src = f"data:{image_type};base64,{image_data}"

    venue_url = f"?venue={quote(venue_name)}"
    st.markdown(
        f"""
        <a class="venue-image-link" href="{venue_url}" target="_self">
            <img src="{image_src}" alt="{html.escape(venue_name)}"
                 style="width: 100%; height: 220px; object-fit: cover;
                        border-radius: 0.75rem; cursor: pointer;">
        </a>
        """,
        unsafe_allow_html=True,
    )


# 画面表示の管理用State（初期状態は「一覧画面」）
if "selected_venue_name" not in st.session_state:
    st.session_state.selected_venue_name = None
if st.query_params.get("venue"):
    st.session_state.selected_venue_name = st.query_params.get("venue")


# ----------------------------------------------------
# A. 詳細ページ画面（会場名が選択されている時）
# ----------------------------------------------------
if st.session_state.selected_venue_name:
    # 選択されている会場のデータを検索
    venue = next((v for v in st.session_state.venues if v["name"] == st.session_state.selected_venue_name), None)

    if venue:
        # 戻るボタン
        st.markdown(
            '<a class="back-to-list" href="./" target="_self">'
            "← 会場一覧へ戻る</a>",
            unsafe_allow_html=True,
        )

        st.title(venue["name"])
        st.caption(f"種別: {venue['category']} | キャパシティ: 約 {venue['capacity']:,} 人")
        st.markdown(f"公式サイト: [{venue['website']}]({venue['website']})")

        # タブで詳細情報をすっきり整理
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["基本情報", "写真ギャラリー", "歴史・概要", "主な利用実績", "口コミ・感想"]
        )

        with tab1:
            city = venue["address"].replace("神奈川県", "").split("区")[0]
            if "市" in city:
                city = city.split("市")[0] + "市"
            facilities_by_category = {
                "スタジアム": "大規模なスポーツ大会や屋外ライブに対応する多目的会場です。",
                "アリーナ": "音楽ライブ、スポーツ、展示会などに利用される屋内会場です。",
                "ライブハウス": "ライブやファンミーティングなど、音楽イベントに適した会場です。",
                "ホール": "コンサート、舞台、式典などに利用されるホールです。",
                "劇場": "演劇や舞台公演を中心とした客席・ステージ型の会場です。",
                "コンベンション・ホール": "展示会、会議、イベントなど幅広い用途に対応する会場です。",
            }
            st.markdown("#### アクセス")
            station_walk = venue.get("station_walk", {})
            if station_walk:
                station_text = "、".join(
                    f"{station}（{walk_time}）"
                    for station, walk_time in station_walk.items()
                )
            else:
                station_text = venue["station"]
            st.write(f"最寄り駅: {station_text}")
            st.write(f"所在地: {venue['address']}")
            map_query = quote(f"{venue['name']} {venue['address']}")
            st.components.v1.html(
                f"""
                <iframe
                    src="https://www.google.com/maps?q={map_query}&hl=ja&z=15&output=embed"
                    width="100%"
                    height="260"
                    style="border:0; border-radius:12px;"
                    loading="lazy"
                    referrerpolicy="no-referrer-when-downgrade"
                    title="{html.escape(venue['name'])}の地図">
                </iframe>
                """,
                height=280,
            )

            st.markdown("#### 設備・特徴")
            st.write(
                facilities_by_category.get(
                    venue["category"], "さまざまなイベントに利用される会場です。"
                )
            )
            st.write(f"収容人数: 約 {venue['capacity']:,} 人")

            st.markdown("#### 周辺情報")
            nearby_spots = venue.get("nearby_spots", [])
            if nearby_spots:
                st.markdown("##### 会場周辺の観光スポット")
                for spot in nearby_spots:
                    st.write(
                        f"- **{spot['name']}**（{spot['time']}）"
                        f"{'：' + spot['description'] if spot.get('description') else ''}"
                    )
            elif venue.get("nearby_notice"):
                st.markdown("##### 会場周辺の観光スポット")
                st.write(venue["nearby_notice"])

            st.markdown("##### 会場周辺のコンビニ・飲食店")
            nearby_places = venue.get("nearby_places", [])
            if nearby_places:
                for place in nearby_places:
                    st.write(f"{place['time']}に{place['name']}")

            st.markdown("#### 公式リンク")
            st.markdown(f"[公式サイトを見る]({venue['website']})")

            st.markdown("#### 公式SNS")
            social_links = venue.get("social_links", {})
            for label, url in [
                ("Instagram", social_links.get("instagram")),
                ("LINE", social_links.get("line")),
                ("X", social_links.get("x")),
                ("Facebook", social_links.get("facebook")),
            ]:
                if url:
                    st.link_button(label, url, use_container_width=True)
                else:
                    st.caption(f"{label}: 未登録")

        with tab2:
            st.subheader("会場フォトギャラリー")
            gallery = venue.get("gallery", [venue["image"]])
            cols = st.columns(len(gallery))
            for i, img_url in enumerate(gallery):
                with cols[i]:
                    st.image(img_url, use_container_width=True, caption=f"{venue['name']} Photo {i+1}")
            if venue.get("image_source"):
                st.caption(
                    f"{venue['name']}写真の出典: "
                    f"{venue.get('image_source_name', '提供元')}"
                )

        with tab3:
            st.subheader("会場の歴史")
            timeline = venue.get("timeline", [])
            if timeline:
                for item in timeline:
                    year_col, event_col = st.columns([1, 4])
                    with year_col:
                        st.markdown(f"**{item['year']}**")
                    with event_col:
                        st.write(item["event"])
            else:
                st.write("年表情報は準備中です。")
            history_description = venue.get("history_description")
            if history_description:
                st.write(history_description)
            charm_point = venue.get("charm_point")
            charm_description = venue.get("charm_description")
            if charm_description:
                st.write(charm_description)

        with tab4:
            major_uses = venue.get("major_uses")
            if major_uses:
                for category, items in major_uses:
                    st.subheader(category)
                    for item in items:
                        st.markdown(f"- {item}")
            else:
                st.subheader("主に使用したアーティスト")
                performers = venue.get("performers", [])
                if performers:
                    for p in performers:
                        st.markdown(f"- **{p}**")
                else:
                    st.write("アーティスト情報準備中")

        with tab5:
            reviews = venue.setdefault("reviews", [])
            st.subheader(f"口コミ・評価 （全 {len(reviews)} 件）")
            
            # 口コミ投稿フォーム
            with st.form("detail_review_form"):
                new_review = st.text_area("この会場についての感想や知恵袋を投稿しよう")
                if st.form_submit_button("口コミを投稿"):
                    if new_review.strip():
                        reviews.append(new_review)
                        st.success("口コミを投稿しました！")
                        st.rerun()

            st.divider()
            for r in reviews:
                st.info(r)


# ----------------------------------------------------
# B. 一覧ページ画面（トップ画面）
# ----------------------------------------------------
else:
    # ページ最上部に検索・フィルターを配置
    with st.container(key="search-panel"):
        search_col, category_col = st.columns([2, 1])
        with search_col:
            search_keyword = st.text_input(
                "検索",
                placeholder="例：横浜アリーナ",
                help="会場名・種別・住所から検索できます。",
                label_visibility="collapsed",
            ).strip().lower()
        categories = sorted(
            {venue["category"] for venue in st.session_state.venues}
        )
        with category_col:
            selected_category = st.session_state.get("selected_category")
            if selected_category not in categories:
                selected_category = None
                st.session_state.selected_category = None
            with st.popover(
                selected_category or "種別に絞り込む",
                use_container_width=True,
            ):
                with st.container(key="category-options"):
                    if st.button(
                        "すべて",
                        key="category-filter-all",
                        use_container_width=True,
                    ):
                        st.session_state.selected_category = None
                        selected_category = None
                    for category in categories:
                        if st.button(
                            category,
                            key=f"category-filter-{category}",
                            use_container_width=True,
                        ):
                            st.session_state.selected_category = category
                            selected_category = category

    st.markdown(
        """
        <header class="site-hero">
            <p class="site-hero-kicker">KANAGAWA VENUE GUIDE</p>
            <h1 class="site-hero-title">神奈川の会場を探す</h1>
        </header>
        """,
        unsafe_allow_html=True,
    )
    st.write("写真を選択すると、会場の詳しい情報を確認できます。")

    filtered_venues = []
    for venue in st.session_state.venues:
        searchable_text = " ".join(
            [venue["name"], venue["category"], venue["address"]]
        ).lower()
        if search_keyword and search_keyword not in searchable_text:
            continue
        if (
            selected_category is not None
            and venue["category"] != selected_category
        ):
            continue
        filtered_venues.append(venue)

    st.caption(f"{len(filtered_venues)}件の会場")
    if not filtered_venues:
        st.info("条件に一致する会場がありません。")

    # トップ画面は写真と会場名だけを3列のグリッドで表示
    for row_start in range(0, len(filtered_venues), 3):
        columns = st.columns(3)
        for column, venue in zip(columns, filtered_venues[row_start:row_start + 3]):
            with column:
                render_venue_image(
                    venue.get("image", "https://via.placeholder.com/300"),
                    venue["name"],
                )
                if venue.get("image_source"):
                    st.caption(
                        f"写真出典: {venue.get('image_source_name', '提供元')}"
                    )
                st.markdown(f"**{venue['name']}**")