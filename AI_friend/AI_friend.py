import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json
#网站基本信息
st.set_page_config(
    page_title="AI Friend",
    page_icon="🩷",
    layout="wide",#布局centered wide None
    initial_sidebar_state="expanded",
)
def return_time():
    return datetime.now().strftime("%Y-%m-%d %H：%M：%S")
#保存当前信息
def saveItem():
    if st.session_state.current_session:
            session_data={
                "nickname": st.session_state.nickname,
                "nature": st.session_state.nature,
                "current_session": st.session_state.current_session,
                "messages": st.session_state.messages,
            }
    #如果sessions不存在，则创建一个空列表
            if not os.path.exists("sessions"):
                os.mkdir("sessions")


            with open(f"sessions/{st.session_state.current_session}.json","w",encoding="utf-8") as f:
                json.dump(session_data,f,ensure_ascii=False,indent=2)
#加载会话列表信息
def load_sessions():
    session_list=[]
    if os.path.exists("sessions"):
        file_list=os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5:1])
    session_list.sort(reverse=True)
    return session_list

#加载指定会话
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json","r",encoding="utf-8") as f:
                session_date=json.load(f)
                st.session_state.messages=session_date["messages"]
                st.session_state.nickname=session_date["nickname"]
                st.session_state.nature=session_date["nature"]
                st.session_state.current_session=session_name
    except Exception:
        st.error("加载会话失败")
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
        if st.session_state.current_session==session_name:
            st.session_state.messages=[]
            st.session_state.nickname="Selly"
            st.session_state.nature="一位温柔体贴，善解人意，偶尔有点小脾气，但总是以关心和爱护为出发点的伴侣，喜欢文学作品，对中国古代诗词歌赋有较大的爱好，喜欢在对话中引用一些诗词。"
            st.session_state.current_session=""

    except Exception:
        st.error("删除会话失败")
st.title("AI Friend")
st.header("This is a header")
st.subheader("This is a subheader")
st.logo("./image/logo1.png")
#系统提示词
system_prompt = """
            你叫%s,现在是用户真实伴侣，请完全代入角色:
            规则：
            1.每次回复1到4条消息
            2.禁止任何场景或状态描述性文字
            3.匹配用户语言
            4.回复简短，假设你在微信聊天一样
            5.有需要可以增加一些颜文字或者其它emoji表情包
            6.用符合伴侣性格的方式对话
            7.回复的内容，要充分体现伴侣性格特征
        伴侣性格：
        %s
    必须严格遵守上述规则和伴侣性格进行对话  
"""


#存储信息防止被覆盖
if "messages" not in st.session_state:
    st.session_state.messages = []
#昵称
if "nickname" not in st.session_state:
    st.session_state.nickname = "Selly"
#性格
if "nature" not in st.session_state:
    st.session_state.nature = "一位温柔体贴，善解人意，偶尔有点小脾气，但总是以关心和爱护为出发点的伴侣，喜欢文学作品，对中国古代诗词歌赋有较大的爱好，喜欢在对话中引用一些诗词。"
#显示会话历史
if st.session_state.messages:
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])
#会话显示
if "current_session" not in st.session_state:
    st.session_state.current_session = return_time()


#生成侧边栏
with st.sidebar:
    #ai控制面板
    st.header("AI控制面板")
    #按钮

    if  st.button("新建会话",width="stretch",icon="❣️"):
        
        #保存当前会话信息
        saveItem()
    #创建新会话
        if st.session_state.messages:#如果当前会话有消息了才保存
            st.session_state.messages=[]
            st.session_state.current_session=return_time()
            saveItem()
            st.rerun()#重新运行当前页面
    
    st.text("会话列表")
    #显示会话列表
    session_lists=load_sessions()
    for session in session_lists:
        col1,col2=st.columns([4,1])
        with col1:
            if st.button(session,width="stretch",icon="📙",key=f"load_{session}",type="primary"if session==st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("",width="stretch",icon="✖️",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()
    st.divider()
    st.subheader("Friend Info")
    nickname=st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nickname)
    if nickname:
        st.session_state.nickname=nickname
    nature=st.text_area("性格特点",placeholder="请输入性格特点",value=st.session_state.nature,height=600,width=300)
    if nature:
        st.session_state.nature=nature


#创建与OpenAI API的连接，使用环境变量中的API密钥和指定的基础URL
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")


#消息输入框
prompt=st.chat_input("Please enter ur question")
if prompt:#字符串会自动转化为bool值
    st.chat_message("user").write(prompt)
    print("----->调用大模型",prompt)
    #将用户输入的消息添加到会话状态中
    st.session_state.messages.append({"role": "user", "content": prompt})
    #调用AI大模型
    assistant_content = ""
    with st.chat_message("assistant"):
        response_messageOne = st.empty()

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt % (st.session_state.nickname, st.session_state.nature)},
                *st.session_state.messages
            ],
            stream=True
        )

        # 新版 SDK 中 delta 是对象，不是 dict，需用属性访问
        for chunk in response:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                assistant_content += delta_content
                response_messageOne.write(assistant_content)

    except Exception as e:
        assistant_content = f"调用模型失败: {e}"
        response_messageOne.write(assistant_content)

    st.session_state.messages.append({"role": "assistant", "content": assistant_content})

    #save
    saveItem()