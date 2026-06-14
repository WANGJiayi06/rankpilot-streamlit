import os
import base64
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path("data/admissions_2025_sichuan_physics_v4.csv")
HERO_IMAGE_PATH = Path("assets/hero.jpg")

DISCLAIMER = (
    "本项目仅用于课程项目演示。数据为四川省 2025 年物理类，"
    "不同高校公开口径可能包括专业线、专业类线、专业组线或院校最低线。"
    "本项目不构成真实志愿填报建议，实际填报请以四川省教育考试院、"
    "高校招生章程和官方录取数据为准。"
)


st.set_page_config(page_title="RankPilot", layout="wide")


@st.cache_data
def load_hero_image() -> str:
    if not HERO_IMAGE_PATH.exists():
        return ""
    return base64.b64encode(HERO_IMAGE_PATH.read_bytes()).decode("utf-8")


def render_hero() -> None:
    hero_image = load_hero_image()
    image_layer = (
        f"background-image: url('data:image/jpeg;base64,{hero_image}');"
        if hero_image
        else "background: linear-gradient(135deg, #1f2937, #020617);"
    )
    st.markdown(
        f"""
        <style>
        .block-container {{
            max-width: 1180px;
            padding-top: 1.5rem;
        }}
        .rankpilot-hero {{
            position: relative;
            min-height: 520px;
            border-radius: 0;
            overflow: hidden;
            margin: 0 0 28px 0;
            background: #020617;
            box-shadow: 0 24px 80px rgba(15, 23, 42, 0.28);
        }}
        .rankpilot-hero::before {{
            content: "";
            position: absolute;
            inset: 0;
            {image_layer}
            background-size: cover;
            background-position: center left;
            filter: saturate(1.06) contrast(1.02);
            transform: scale(1.01);
        }}
        .rankpilot-hero::after {{
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 34%, rgba(0,0,0,0.42) 50%, rgba(0,0,0,0.82) 67%, #000 100%),
                linear-gradient(180deg, rgba(0,0,0,0.08) 0%, rgba(0,0,0,0.10) 58%, rgba(0,0,0,0.68) 100%);
            backdrop-filter: blur(0px);
        }}
        .rankpilot-hero-panel {{
            position: absolute;
            top: 0;
            right: 0;
            width: 42%;
            height: 100%;
            background: linear-gradient(90deg, rgba(0,0,0,0.12), rgba(0,0,0,0.96) 52%, #000 100%);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }}
        .rankpilot-hero-content {{
            position: absolute;
            z-index: 2;
            right: 5.5%;
            top: 50%;
            transform: translateY(-50%);
            width: min(420px, 38vw);
            color: #ffffff;
            text-align: left;
        }}
        .rankpilot-kicker {{
            font-size: 0.84rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: rgba(255,255,255,0.62);
            margin-bottom: 18px;
        }}
        .rankpilot-title {{
            font-size: clamp(3.4rem, 7vw, 6.4rem);
            line-height: 0.92;
            font-weight: 760;
            letter-spacing: 0;
            margin: 0;
        }}
        .rankpilot-subtitle {{
            margin-top: 22px;
            font-size: clamp(1rem, 1.6vw, 1.28rem);
            line-height: 1.8;
            color: rgba(255,255,255,0.82);
            letter-spacing: 0.02em;
        }}
        .rankpilot-scroll-hint {{
            position: absolute;
            z-index: 2;
            right: 5.5%;
            bottom: 30px;
            color: rgba(255,255,255,0.52);
            font-size: 0.88rem;
        }}
        .rankpilot-section-title {{
            margin: 8px 0 18px 0;
            font-size: 1.45rem;
            font-weight: 700;
            color: #111827;
        }}
        @media (max-width: 760px) {{
            .rankpilot-hero {{
                min-height: 620px;
            }}
            .rankpilot-hero::after {{
                background:
                    linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.46) 42%, rgba(0,0,0,0.96) 72%, #000 100%);
            }}
            .rankpilot-hero-panel {{
                width: 100%;
                height: 55%;
                top: auto;
                bottom: 0;
                background: linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,0.92) 34%, #000 100%);
            }}
            .rankpilot-hero-content {{
                left: 26px;
                right: 26px;
                top: auto;
                bottom: 88px;
                width: auto;
                transform: none;
            }}
            .rankpilot-scroll-hint {{
                left: 26px;
                right: auto;
            }}
        }}
        </style>
        <section class="rankpilot-hero">
            <div class="rankpilot-hero-panel"></div>
            <div class="rankpilot-hero-content">
                <div class="rankpilot-kicker">GAOKAO ADMISSION ASSISTANT</div>
                <h1 class="rankpilot-title">RankPilot</h1>
                <div class="rankpilot-subtitle">选择自有方寸，未来满目星光。</div>
            </div>
            <div class="rankpilot-scroll-hint">向下生成你的冲稳保方案</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            "未找到数据文件："
            f"{DATA_PATH}。请确认已上传 data/admissions_2025_sichuan_physics_v4.csv，"
            "并保持 data 文件夹与 app.py 在同一项目目录下。"
        )
        st.stop()
    df = pd.read_csv(DATA_PATH)
    df["min_score"] = pd.to_numeric(df["min_score"], errors="coerce")
    df["min_rank"] = pd.to_numeric(df["min_rank"], errors="coerce")
    df = df.dropna(subset=["min_score"]).copy()
    df["min_score"] = df["min_score"].astype(int)
    return df


def classify_by_score(score_diff: float, risk_mode: str) -> str:
    if risk_mode == "保守":
        if score_diff < 0:
            return "冲"
        if score_diff <= 15:
            return "稳"
        return "保"

    if risk_mode == "激进":
        if score_diff < -10:
            return "冲"
        if score_diff <= 5:
            return "稳"
        return "保"

    if score_diff < -5:
        return "冲"
    if score_diff <= 10:
        return "稳"
    return "保"


def classify_by_rank(rank_diff: float | None, choice_type: str) -> str:
    if pd.isna(rank_diff):
        return "无位次数据"
    if rank_diff < -3000:
        return "位次偏冲"
    if rank_diff <= 5000:
        return "位次接近"
    return "位次较稳"


def parse_keywords(keyword: str) -> list[str]:
    if not keyword.strip():
        return []
    parts = re.split(r"[,\s，、]+|或者|或", keyword.strip())
    return [part.strip() for part in parts if part.strip()]


def filter_data(
    df: pd.DataFrame,
    cities: list[str],
    schools: list[str],
    school_tags: list[str],
    keyword: str,
    include_group_lines: bool,
) -> pd.DataFrame:
    result = df.copy()

    if cities:
        result = result[result["city"].isin(cities)]

    if schools:
        result = result[result["school"].isin(schools)]

    if school_tags:
        pattern = "|".join(school_tags)
        result = result[result["school_type"].fillna("").str.contains(pattern, regex=True)]

    keywords = parse_keywords(keyword)
    if keywords:
        major_text = result["major_or_group"].fillna("")
        mask = False
        for item in keywords:
            mask = mask | major_text.str.contains(item, case=False, regex=False)
        result = result[mask]

    if not include_group_lines:
        result = result[~result["note"].fillna("").str.contains("非具体专业最低分", regex=False)]

    return result.copy()


def rule_based_advice(result: pd.DataFrame, score: int, risk_mode: str) -> str:
    if result.empty:
        return (
            "当前筛选条件下没有匹配记录。建议放宽城市、学校类型或专业关键词，"
            "再重新生成方案。"
        )

    counts = result["choice_type"].value_counts()
    top_stable = result[result["choice_type"] == "稳"].sort_values("score_diff").head(3)
    top_safe = result[result["choice_type"] == "保"].sort_values("score_diff").head(3)
    top_rush = result[result["choice_type"] == "冲"].sort_values("score_diff", ascending=False).head(3)

    def names(df: pd.DataFrame) -> str:
        if df.empty:
            return "暂无"
        return "；".join(f"{r.school}-{r.major_or_group}" for r in df.itertuples())

    return f"""
根据当前筛选条件，系统共找到 {len(result)} 条记录：冲 {counts.get("冲", 0)} 条，稳 {counts.get("稳", 0)} 条，保 {counts.get("保", 0)} 条。

当前分数为 {score}，风险偏好为“{risk_mode}”。建议采用“少量冲刺、重点稳妥、保底充分”的组合，不要只看最高分差，也要核对招生计划、专业组要求和调剂规则。

可优先查看：
- 冲刺候选：{names(top_rush)}
- 稳妥候选：{names(top_stable)}
- 保底候选：{names(top_safe)}

本结果只基于 2025 年录取线做静态模拟，不能代表 2026 年真实录取概率。
"""


def ai_advice(prompt: str) -> str:
    try:
        from openai import OpenAI

        api_key = st.secrets.get("DASHSCOPE_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        base_url = (
            st.secrets.get("DASHSCOPE_BASE_URL")
            or os.getenv("DASHSCOPE_BASE_URL")
            or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        model = st.secrets.get("DASHSCOPE_MODEL") or os.getenv("DASHSCOPE_MODEL") or "qwen-turbo"

        if not api_key:
            return "AI 解释暂不可用：未配置 DASHSCOPE_API_KEY。"

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个谨慎的高考志愿填报模拟解释助手。"
                        "只能解释用户表格中已有的学校和专业，不能编造数据，"
                        "不能承诺录取结果，必须提醒用户以官方信息为准。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as exc:
        return f"AI 解释暂不可用，已显示规则版建议。错误信息：{exc}"


def build_prompt(result: pd.DataFrame, score: int, risk_mode: str, keyword: str) -> str:
    sample_cols = [
        "choice_type",
        "school",
        "major_or_group",
        "min_score",
        "score_diff",
        "min_rank",
        "rank_diff",
        "city",
        "note",
    ]
    counts = result["choice_type"].value_counts()
    sample_parts = []
    for choice_type in ["冲", "稳", "保"]:
        part = result[result["choice_type"] == choice_type].copy()
        if part.empty:
            sample_parts.append(f"\n【{choice_type}】无候选记录")
            continue
        if choice_type == "冲":
            part = part.sort_values("score_diff", ascending=False).head(6)
        else:
            part = part.sort_values("score_diff", ascending=True).head(6)
        sample_parts.append(f"\n【{choice_type}】\n{part[sample_cols].to_string(index=False)}")

    sample_text = "\n".join(sample_parts)
    return f"""
你是一个高考志愿填报模拟助手。请根据下面的 Python 计算结果，为用户生成谨慎、简洁、可执行的解释性建议。

用户信息：
- 省份：四川
- 科类：物理类
- 用户分数：{score}
- 风险偏好：{risk_mode}
- 专业关键词：{keyword or "不限"}

系统根据 2025 年四川物理类录取线计算出的候选结果统计：
- 总记录数：{len(result)}
- 冲：{counts.get("冲", 0)}
- 稳：{counts.get("稳", 0)}
- 保：{counts.get("保", 0)}

分层样本如下。请同时参考冲、稳、保三类；如果某一类为空，必须明确说明该类当前没有候选，而不是说你看不到数据。
{sample_text}

请按以下格式输出：
一、总体判断
二、冲稳保搭配建议
三、值得优先查看的学校/专业
四、真实填报前必须核对的信息

要求：
- 只能引用表格里出现的学校和专业，不要编造。
- 必须分别讨论“冲、稳、保”三类；如果某类为空，说明原因并建议放宽筛选条件或调整风险偏好。
- 不要承诺录取。
- 不要给绝对结论。
- 明确说明本项目仅用于课程演示。
"""


def main() -> None:
    df = load_data()

    render_hero()
    st.markdown('<div class="rankpilot-section-title">生成冲稳保方案</div>', unsafe_allow_html=True)
    st.warning(DISCLAIMER)

    with st.expander("使用说明", expanded=False):
        st.write(
            "输入你的高考分数，选择城市、学校类型、专业关键词和风险偏好后，点击“生成冲稳保方案”。"
            "系统会计算你的分数与各专业/专业组最低分的差值，并按规则划分为“冲、稳、保”。"
            "如果数据包含最低位次，页面会额外显示位次差作为参考。"
        )

    _, form_col, _ = st.columns([1, 2, 1])

    with form_col:
        st.subheader("输入条件")
        score = st.number_input("你的高考分数", min_value=0, max_value=750, value=650, step=1)
        rank_input = st.number_input(
            "你的全省位次（可选，0 表示不使用）",
            min_value=0,
            max_value=500000,
            value=0,
            step=100,
        )
        risk_mode = st.selectbox("风险偏好", ["保守", "均衡", "激进"], index=1)

        cities = st.multiselect("城市偏好", sorted(df["city"].dropna().unique().tolist()))
        school_tags = st.multiselect("学校标签", ["985", "211", "双一流", "财经", "工科", "师范", "综合"])
        schools = st.multiselect("指定学校（可选）", sorted(df["school"].dropna().unique().tolist()))
        keyword = st.text_input("专业关键词", placeholder="可输入多个关键词，例如：计算机，金融 或 统计 电子信息 临床")
        include_group_lines = st.checkbox("包含专业组/院校最低线等非具体专业线", value=True)
        use_ai = st.checkbox("使用大模型解释", value=False)

        run = st.button("生成冲稳保方案", type="primary", use_container_width=True)

    if run:
        result = filter_data(df, cities, schools, school_tags, keyword, include_group_lines)

        if result.empty:
            st.error("没有匹配记录。请放宽筛选条件。")
            st.stop()

        result["score_diff"] = score - result["min_score"]
        result["choice_type"] = result["score_diff"].apply(lambda x: classify_by_score(x, risk_mode))

        if rank_input > 0 and result["min_rank"].notna().any():
            result["rank_diff"] = result["min_rank"] - rank_input
            result["rank_hint"] = result.apply(
                lambda row: classify_by_rank(row["rank_diff"], row["choice_type"]), axis=1
            )
        else:
            result["rank_diff"] = pd.NA
            result["rank_hint"] = "未使用位次"

        type_order = {"冲": 0, "稳": 1, "保": 2}
        result["type_order"] = result["choice_type"].map(type_order)
        result = result.sort_values(["type_order", "score_diff"], ascending=[True, False])

        st.divider()
        st.subheader("冲稳保结果")
        counts = result["choice_type"].value_counts()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("冲", int(counts.get("冲", 0)))
        m2.metric("稳", int(counts.get("稳", 0)))
        m3.metric("保", int(counts.get("保", 0)))
        m4.metric("匹配记录", len(result))

        display_cols = [
            "choice_type",
            "school",
            "major_or_group",
            "min_score",
            "score_diff",
            "min_rank",
            "rank_diff",
            "rank_hint",
            "city",
            "school_type",
            "note",
        ]
        st.dataframe(result[display_cols], use_container_width=True, hide_index=True)

        st.subheader("分数差可视化")
        chart_df = result[result["score_diff"].between(-20, 20)].copy()
        if chart_df.empty:
            st.info("当前筛选结果中没有分数差在 -20 到 +20 之间的候选项，暂不显示图表。")
        else:
            st.caption("图表仅展示分数差在 -20 到 +20 之间的候选项，避免极端分差挤占视图。")
            chart_df = chart_df.sort_values("score_diff", ascending=True).head(35)
            chart_df["label"] = chart_df["school"] + "｜" + chart_df["major_or_group"].astype(str)
            fig = px.bar(
                chart_df,
                x="score_diff",
                y="label",
                color="choice_type",
                orientation="h",
                hover_data=["school", "major_or_group", "min_score", "city", "note"],
                title="候选专业分数差分布（仅显示 -20 到 +20 分）",
                color_discrete_map={"冲": "#d95f02", "稳": "#1b9e77", "保": "#377eb8"},
            )
            fig.update_layout(yaxis_title="", xaxis_title="分数差", height=650)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("解释建议")
        rule_text = rule_based_advice(result, score, risk_mode)
        st.info(rule_text)

        if use_ai:
            st.subheader("AI 补充解释")
            with st.spinner("正在生成 AI 解释..."):
                ai_text = ai_advice(build_prompt(result, score, risk_mode, keyword))
            if ai_text.startswith("AI 解释暂不可用"):
                st.warning(ai_text)
            else:
                st.write(ai_text)

        with st.expander("分类规则"):
            st.markdown(
                """
                分数差 = 你的分数 - 录取线。

                - 保守：分数差 < 0 为“冲”，0 到 15 为“稳”，大于 15 为“保”。
                - 均衡：分数差 < -5 为“冲”，-5 到 10 为“稳”，大于 10 为“保”。
                - 激进：分数差 < -10 为“冲”，-10 到 5 为“稳”，大于 5 为“保”。

                如果数据包含最低位次，系统会额外计算“最低位次 - 你的位次”。位次越小越好，
                因此该差值越大，说明相对越稳。
                """
            )

    else:
        st.info("请在左侧输入条件后点击“生成冲稳保方案”。")


if __name__ == "__main__":
    main()
