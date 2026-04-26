import streamlit as st
import pandas as pd
import random
from openai import OpenAI

# --- 1. 实验初始化配置 ---
st.set_page_config(page_title="Seed AI", layout="centered")

if "consent" not in st.session_state:
    st.markdown("""
    # 欢迎参与本次实验！
尊敬的女士/先生：
您好！非常感谢您参与本实验，本实验旨在了解用户在求职面试相关任务中与AI助手的交互行为，仅用于毕业论文研究。

本次实验包含以下内容：
- 您将进入一个求职面试相关任务情境，并根据页面说明完成相应任务；
- 任务过程中，您可以与AI助手对话，系统会自动记录您的对话数据（仅用于学术研究，全程匿名、严格保密）；
- 任务完成后，请根据页面提示保存数据，并填写一份简短的后续问卷；

实验流程：
1.  阅读任务说明进入任务界面 → 分配用户ID
2.  根据页面说明完成相应任务（与AI对话协作）
3.  完成任务后，点击页面中的“保存数据”按钮
4.  填写后测问卷

⚠️ 重要说明：
- 本实验无对错之分，请按您的真实想法完成任务
- 您可以随时退出实验，无需任何理由，数据不会被记录
- 所有数据仅用于学术研究，不会泄露任何个人信息

点击下方按钮，即表示您已阅读并同意以上说明，自愿参与本次实验。
    """)
    if st.button("我已阅读并同意，进入实验"):
        st.session_state["consent"] = True
        st.rerun()
    st.stop()
    

# 直接配置 DeepSeek 接口
client = OpenAI(
    api_key="sk-f9fd213424cf41d29cf7c564be6ac48d",  # 你自己填写 API Key
    base_url="https://api.deepseek.com"
)

# 简历图片链接（和研究3完全一样）
RESUME_IMAGES = [
    "https://i.imgur.com/hfRjQTI.jpeg",
    "https://i.imgur.com/dDM6Mt2.jpeg",
    "https://i.imgur.com/O5cvFL9.jpeg",
    "https://i.imgur.com/cyRqMzM.jpeg"
]

# 初始化实验数据（完全沿用研究3格式）
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'group' not in st.session_state:
    st.session_state.group = random.choice(['Control', 'A', 'B'])
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{random.randint(100000, 999999)}"
if 'first_intervene' not in st.session_state:
    st.session_state.first_intervene = None
if 'total_intervene' not in st.session_state:
    st.session_state.total_intervene = 0
if 'nudge_prompt' not in st.session_state:
    st.session_state.nudge_prompt = ""

# --- 2. 页面标题 ---
st.title("🤖 Seed AI")

# --- 3. 侧边栏 ---
st.sidebar.info(f"**用户ID:** {st.session_state.user_id}")
st.sidebar.info(f"**助推组别:** {st.session_state.group}")

# --- 4. 简历图片（和研究3完全一样：横向4列） ---
st.subheader("📄 简历材料")
cols = st.columns(4)
for i, img in enumerate(RESUME_IMAGES):
    if img:
        cols[i].image(img, caption=f"简历{i+1}")

st.divider()

# ==============================================
# 研究4任务说明（保持和研究3一样的排版）
# ==============================================
st.markdown("### 任务：人力资源经理（HR）")
st.markdown("""
**你是一名人力资源经理（HR），你所在的公司拟招聘1名AI算法工程师。**
请梳理你目前收到的4份简历，结合岗位招聘标准，为“AI算法工程师”岗位选择1名合适的候选人。
并请给出您选择时参考的岗位招聘标准（至少3个方面，每个方面不超过200字）。

### 招聘岗位：AI 算法工程师
【岗位职责】
- 负责公司核心产品中机器学习/深度学习算法的开发与优化；
- 跟踪前沿 AI 技术，将其转化为可落地的业务方案；
- 参与模型性能评估，确保持续提升算法输出的准确度。

【任职要求】
- 计算机、统计学或数学相关专业本科及以上学历；
- 熟悉 Python/C++ 等编程语言，熟练使用 PyTorch 或 TensorFlow 框架；
- 核心关注：具备良好的算法优化能力，有实际的项目应用经验者优先。
""")
choice = st.radio("✅ 请选择录取的候选人：", ["候选人1", "候选人2", "候选人3", "候选人4"])
q1 = st.text_input("① 专业匹配度评价（≤200字）：")
q2 = st.text_input("② 算法优化能力评价（≤200字）：")
q3 = st.text_input("③ 项目经验评价（≤200字）：")
user_task_input = f"录取：{choice} | 专业：{q1} | 算法能力：{q2} | 项目经验：{q3}"

st.divider()

# --- AI 调用函数（和研究3完全一样） ---
def fetch_ai_response(chat_history):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API调用失败: {e}"

# --- 干预关键词（和研究3完全一样） ---
revision_keywords = [
    "改", "重写", "调整", "不对", "换", "重新", "不要", "修改", "优化",
    "太长", "太短", "长一点", "短一点", "精简", "扩写", "缩写", "字数",
    "语气", "风格", "幽默", "专业", "严肃", "通俗", "正式", "口语化",
    "表格", "列表", "分点", "条理", "结构", "清晰", "替换", "纠正",
    "错", "不好", "不够", "重新生成", "换一种", "再来", "重做", "修正"
]

# ==============================================
# 元认知唤醒助推（按研究3风格嵌入，不破坏界面）
# ==============================================
def render_nudge(last_ai_response):
    if st.session_state.group == 'A':
        if len(last_ai_response) > 150:
            st.warning("💡 提示：内容较长，建议精简为 100-120 字")
            if st.button("🔧 自动精简字数"):
                prompt = "请帮我把每条内容精简到100-120字，保留核心信息"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()

        elif len(last_ai_response) > 2 and "、" not in last_ai_response[:50]:
            st.warning("💡 提示：内容结构较零散，建议分点整理")
            if st.button("🔧 自动分点整理"):
                prompt = "请帮我把内容整理成清晰的分点条目"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()

        elif "会" in last_ai_response[:30] or "可以" in last_ai_response[:30]:
            st.warning("💡 提示：表述偏口语，建议使用专业 HR 用语")
            if st.button("🔧 自动优化专业度"):
                prompt = "请使用专业的HR招聘术语，不要口语化"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()

    elif st.session_state.group == 'B':
        st.info("🧠 元认知助推：点击按钮快速优化内容")
        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("💼 专业语气"):
                prompt = "请使用专业HR语气"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()
        with cb:
            if st.button("📏 控制字数"):
                prompt = "请控制每条内容100-120字"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()
        with cc:
            if st.button("✅ 分点整理"):
                prompt = "请分点整理，结构更清晰"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()
                
    return None

ai_content = st.session_state.messages[-1]["content"] if len(st.session_state.messages) > 0 else ""
render_nudge(ai_content)

# --- 聊天界面 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入指令（可修改/干预意图）..."):
    current_turn = len([m for m in st.session_state.messages if m['role'] == 'user']) + 1
    is_revision = any(keyword in prompt for keyword in revision_keywords)

    if is_revision and st.session_state.first_intervene is None:
        st.session_state.first_intervene = current_turn
    if is_revision:
        st.session_state.total_intervene += 1

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI 思考中..."):
            ai_content = fetch_ai_response(st.session_state.messages)
            st.markdown(ai_content)
    st.session_state.messages.append({"role": "assistant", "content": ai_content})

# --- 导出数据 ---
st.divider()
user_turns = len([m for m in st.session_state.messages if m["role"]=="user"])

if user_turns < 3:
    st.warning(f"当前对话轮次：{user_turns}，**至少完成3轮对话**才能提交实验")
else:
    if st.button("✅ 完成并导出实验数据"):
        first_intervene_turn = st.session_state.first_intervene if st.session_state.first_intervene else 0
        total_intervene_count = st.session_state.total_intervene
        total_turns = len([m for m in st.session_state.messages if m["role"] == "user"])
        
        full_dialogue = ""
        for msg in st.session_state.messages:
            role = "用户" if msg["role"] == "user" else "AI"
            full_dialogue += f"[{role}]: {msg['content']}\n\n"
        
        final_data = {
            "user_id": [st.session_state.user_id],
            "group": [st.session_state.group],
            "total_turns": [total_turns],
            "first_intervene_turn": [first_intervene_turn],
            "total_intervene_count": [total_intervene_count],
            "full_dialogue": [full_dialogue]
        }
        
        final_df = pd.DataFrame(final_data)
        csv = final_df.to_csv(index=False, encoding="utf-8-sig")
        
        st.download_button(
            "📥 点击下载 CSV 文件",
            csv,
            f"SeedAI_Group_{st.session_state.user_id}.csv",
            "text/csv"
        )
