import streamlit as st
import streamlit.components.v1 as components

# 页面配置
st.set_page_config(page_title="同步听写助手", layout="centered")

# 核心程序
html_code = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root { --primary: #648dd1; --bg: #ffffff; --danger: #e56b60; --success: #78c2ad; --text: #333; }
        body { font-family: 'PingFang SC', sans-serif; background: #f0f2f5; margin: 0; padding: 5px; display: flex; justify-content: center; }
        .container { background: white; width: 100%; max-width: 500px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; min-height: 95vh; }
        .nav-tabs { display: flex; background: #fff; border-bottom: 1px solid #eee; }
        .tab-item { flex: 1; text-align: center; padding: 15px 0; cursor: pointer; font-weight: bold; color: #999; position: relative; }
        .tab-item.active { color: var(--primary); }
        .tab-item.active::after { content: ''; position: absolute; bottom: 0; left: 25%; width: 50%; height: 3px; background: var(--primary); }
        .module-content { flex: 1; padding: 15px; }
        .view-panel { display: none; }
        .view-panel.active { display: block; }
        .card-box { background: #f8f9fa; padding: 12px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #eee; }
        label { display: block; margin-bottom: 4px; font-weight: bold; color: #666; font-size: 13px; }
        select, input, textarea { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid #ddd; font-size: 16px; box-sizing: border-box; margin-bottom: 8px; outline: none; background: #fff; }
        textarea { resize: vertical; min-height: 80px; }
        .player-card { text-align: center; padding: 30px 10px; border: 2px dashed #d0d7de; border-radius: 15px; margin: 10px 0; background: #fff; min-height: 140px; display: flex; flex-direction: column; justify-content: center; }
        #wordHidden { font-size: 45px; font-weight: bold; color: var(--primary); }
        .btn-main { background: var(--primary); color: white; border: none; padding: 16px; border-radius: 14px; font-size: 18px; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 10px; }
        .btn-stop { background: #fff1f0; color: #cf1322; border: 1px solid #ffa39e; padding: 16px; border-radius: 14px; font-size: 18px; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 10px; display: none; }
        .btn-group-nav { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
        .btn-sub { background: #edf2f7; border: none; padding: 12px; border-radius: 10px; color: #4a5568; font-weight: bold; cursor: pointer; font-size: 14px; }
        .word-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
        .word-tag { padding: 15px; border: 1px solid #eee; border-radius: 10px; text-align: center; cursor: pointer; font-weight: bold; background: #fff; font-size: 18px; }
        .word-tag.done { border-color: var(--success); color: var(--success); background: #f6ffed; }
        .word-tag.still-wrong { border-color: var(--danger); color: var(--danger); background: #fff1f0; }
        .mistake-item { display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 12px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #eee; }
        .btn-del { color: var(--danger); font-size: 12px; cursor: pointer; padding: 4px 8px; border: 1px solid #ffccc7; border-radius: 4px; background: #fff1f0; }
        .badge { background: var(--danger); color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px; margin-left: 4px; }
    </style>
</head>
<body>
<div class="container">
    <div class="nav-tabs">
        <div class="tab-item active" onclick="switchModule('dictation')">听写模块</div>
        <div class="tab-item" onclick="switchModule('mistakeBook')">错题本<span id="mistakeBadge" class="badge">0</span></div>
    </div>
    <div class="module-content">
        <div id="dictationView" class="view-panel active">
            <div class="card-box">
                <label>练习模式</label>
                <select id="modeSelect" onchange="toggleMode()">
                    <option value="textbook">课本同步联动听写</option>
                    <option value="custom">✨ 自定义词语听写</option>
                    <option value="mistakeMode">🔥 错题强化挑战</option>
                </select>
                <!-- 课本联动 -->
                <div id="textbookControls">
                    <label>版本 & 单元 & 课文</label>
                    <select id="verSelect" onchange="updateUnits()"></select>
                    <select id="unitSelect" onchange="updateLessons()"></select>
                    <select id="lessonSelect"></select>
                </div>
                <!-- 自定义输入 -->
                <div id="customControls" style="display:none;">
                    <label>输入词语 (逗号或空格分隔)</label>
                    <textarea id="customWordsInput" placeholder="在此输入新词语..."></textarea>
                </div>
                <div style="display:flex; gap:10px;">
                    <div style="flex:1"><label>间隔(s)</label><input type="number" id="interval" value="6"></div>
                    <div style="flex:1"><label>遍数</label><input type="number" id="repeat" value="2"></div>
                </div>
            </div>
            <div class="player-card">
                <div id="wordHidden">准备就绪</div>
                <div id="progressInfo" style="color:#999; font-size:13px; margin-top:5px;"></div>
                <div id="reinforceArea" style="display:none; margin-top:10px;">
                    <div id="reinforceTip" style="font-weight:bold; font-size:13px; margin-bottom:5px;"></div>
                    <div class="word-grid" id="checkGrid"></div>
                </div>
            </div>
            <button id="startBtn" class="btn-main" onclick="startDictation()">🚀 开始报听写</button>
            <button id="stopBtn" class="btn-stop" onclick="stopAndSwitch()">⏹ 停止并重选</button>
            <div class="btn-group-nav">
                <button class="btn-sub" onclick="navControl('prev')">上一个</button>
                <button class="btn-sub" onclick="navControl('replay')">重读</button>
                <button class="btn-sub" onclick="navControl('next')">下一个</button>
            </div>
        </div>
        <div id="mistakeBookView" class="view-panel">
            <button class="btn-main" onclick="quickDictMistakes()">🎧 听写所有错题</button>
            <div id="mistakeList"></div>
            <button class="btn-sub" style="width:100%;margin-top:20px;color:red;" onclick="clearAllMistakes()">清空全部错题</button>
        </div>
    </div>
</div>

<script>
// 1. 240词库数据
const TEXTBOOK_DATA = {
    "人教版语文二下": {
        "词语表 (240词)": {
            "2.春天": ["春天", "寻找", "眉毛", "野花", "柳枝", "桃花"],
            "3.鲜花": ["鲜花", "先生", "原来", "大叔", "太太", "做客", "正巧", "惊奇", "快活", "美好", "礼物"],
            "4.植树": ["植树", "碧空如洗", "万里无云", "格外", "引人注目", "休息", "小心", "笔直"],
            "5.雷锋": ["雷锋", "叔叔", "昨天", "温暖", "爱心"],
            "6.好奇": ["好奇", "也许", "桌子", "平时", "难道", "平常", "农民", "加工", "农具", "甜菜", "工具", "劳动", "经过", "应该"],
            "7.弱小": ["弱小", "周末", "父母", "吸引", "芬芳", "背包", "雨衣", "为什么", "勇敢"],
            "识字1.神州": ["神州", "中华", "山川", "长江", "长城", "民族", "情谊"],
            "识字2.传统": ["传统", "节日", "春节", "花灯", "清明节", "先人", "龙舟", "中秋", "转眼", "团圆"],
            "识字3.故事": ["故事", "生活", "甲骨文", "样子", "钱币", "钱财", "有关"],
            "识字4.美食": ["美食", "茄子", "烤鸭", "水煮鱼", "羊肉", "蛋炒饭"],
            "8.彩色": ["彩色", "铅笔盒", "森林", "雪松", "歌声", "苹果", "精灵", "季节", "流动"],
            "9.出色": ["出色", "妹妹", "碧绿", "波纹", "恋恋不舍", "柳树", "枝条", "不时"],
            "10.绿色": ["绿色", "一直", "说话", "童话", "阿姨", "发现", "弟弟", "发明", "拼音", "字母", "上升"],
            "11.亡羊补牢": ["亡羊补牢", "劝告", "禾苗", "力气", "明白"],
            "12.杨桃": ["杨桃", "图画", "讲桌", "座位", "教室", "老老实实", "时候", "哈哈大笑", "五角星", "画纸", "神情"],
            "13.愿意": ["愿意", "飞快", "为难", "伯伯", "立刻", "突然", "吃惊", "认真", "难为情"],
            "15.雷雨": ["雷雨", "乌云", "黑沉沉", "闪电", "雷声", "窗户", "清新", "迎面"],
            "16.野外": ["野外", "天然", "指南针", "帮助", "方向", "忠实", "向导", "指点", "北极星", "永远", "黑夜", "帮忙", "特别", "积雪"],
            "17.航天员": ["航天员", "宇宙飞船", "空间站", "活动", "主要", "方便", "直接", "浴桶", "清理", "实在", "通常"],
            "18.大象": ["大象", "耳朵", "扇子", "似得", "慢慢", "遇到", "一定", "每天", "睡觉", "经常", "人家"],
            "19.决定": ["决定", "商店", "河马", "工夫", "终于", "星期"],
            "20.青蛙": ["青蛙", "野鸭", "泉水", "花丛", "尽情", "游泳"],
            "21.新奇": ["新奇", "目光", "到处", "仿佛", "周游", "任何", "事情", "纺织", "怎样", "以前", "灵巧", "色彩", "花纹"],
            "22.开始": ["开始", "光明", "值日", "决心", "最后", "从此", "欢唱", "生机"],
            "23.传说": ["传说", "首领", "步行", "忽然", "启发", "搬运", "号召", "民众", "自由", "道理", "根本", "果然", "提供", "便利"],
            "24.洪水": ["洪水", "痛苦", "百姓", "必须", "反而", "仍然", "治服", "继续", "采用", "奔波", "带领", "农业", "安居乐业"]
        }
    }
};

const synth = window.speechSynthesis;
let currentWords = []; let currentIndex = 0; let isPlaying = false; let timer = null;

// 初始化函数：确保在页面加载时执行
function initApp() {
    console.log("初始化程序...");
    const vSel = document.getElementById('verSelect');
    if(!vSel) return;
    
    // 填充版本
    vSel.innerHTML = Object.keys(TEXTBOOK_DATA).map(v => `<option value="${v}">${v}</option>`).join('');
    
    // 加载保存的自定义词
    const savedCustom = localStorage.getItem('CUSTOM_WORDS_VAL');
    if(savedCustom) document.getElementById('customWordsInput').value = savedCustom;

    // 触发联动
    updateUnits(); 
    updateMistakeUI();
    toggleMode(); // 确保模式显示正确
}

function updateUnits() {
    const v = document.getElementById('verSelect').value;
    const uSel = document.getElementById('unitSelect');
    uSel.innerHTML = Object.keys(TEXTBOOK_DATA[v]).map(u => `<option value="${u}">${u}</option>`).join('');
    updateLessons();
}

function updateLessons() {
    const v = document.getElementById('verSelect').value;
    const u = document.getElementById('unitSelect').value;
    const lSel = document.getElementById('lessonSelect');
    lSel.innerHTML = Object.keys(TEXTBOOK_DATA[v][u]).map(l => `<option value="${l}">${l}</option>`).join('');
}

function switchModule(m) {
    document.querySelectorAll('.tab-item, .view-panel').forEach((el,i) => {
        el.classList.toggle('active', (m==='dictation'&&i%2===0) || (m==='mistakeBook'&&i%2!==0));
    });
    if(m==='mistakeBook') renderMistakeList();
}

function toggleMode() {
    const mode = document.getElementById('modeSelect').value;
    document.getElementById('textbookControls').style.display = (mode === 'textbook' ? 'block' : 'none');
    document.getElementById('customControls').style.display = (mode === 'custom' ? 'block' : 'none');
}

function startDictation() {
    const mode = document.getElementById('modeSelect').value;
    if (mode === 'mistakeMode') {
        currentWords = getMistakes();
        if (!currentWords.length) return alert("错题本是空的！");
    } else if (mode === 'custom') {
        const val = document.getElementById('customWordsInput').value.trim();
        if (!val) return alert("请输入词语！");
        currentWords = val.split(/[,\s，\n]+/).filter(w => w.length > 0);
        localStorage.setItem('CUSTOM_WORDS_VAL', val);
    } else {
        const v = document.getElementById('verSelect').value, u = document.getElementById('unitSelect').value, l = document.getElementById('lessonSelect').value;
        currentWords = TEXTBOOK_DATA[v][u][l];
    }
    currentIndex = 0; isPlaying = true;
    setUIPlaying(true);
    document.getElementById('reinforceArea').style.display = "none";
    document.getElementById('wordHidden').style.display = "block";
    runPlayer();
}

function stopAndSwitch() {
    isPlaying = false; clearTimeout(timer); synth.cancel();
    setUIPlaying(false);
    document.getElementById('wordHidden').innerText = "已停止";
}

function setUIPlaying(s) {
    document.getElementById('startBtn').style.display = s ? "none" : "block";
    document.getElementById('stopBtn').style.display = s ? "block" : "none";
    ['modeSelect', 'verSelect', 'unitSelect', 'lessonSelect', 'interval', 'repeat', 'customWordsInput'].forEach(id => {
        const el = document.getElementById(id); if(el) el.disabled = s;
    });
}

async function runPlayer() {
    if (!isPlaying || currentIndex >= currentWords.length) { if (currentIndex >= currentWords.length) finishDictation(); return; }
    const word = currentWords[currentIndex];
    document.getElementById('wordHidden').innerText = "???";
    document.getElementById('progressInfo').innerText = `进度：${currentIndex + 1} / ${currentWords.length}`;
    const repeat = parseInt(document.getElementById('repeat').value);
    for (let i = 0; i < repeat; i++) {
        if (!isPlaying) return;
        await speak(word);
        await new Promise(r => setTimeout(r, 1500));
    }
    timer = setTimeout(() => { currentIndex++; runPlayer(); }, parseInt(document.getElementById('interval').value) * 1000);
}

function speak(text) {
    return new Promise(res => {
        synth.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'zh-CN'; u.rate = 0.8; u.onend = res;
        synth.speak(u);
    });
}

function finishDictation() {
    isPlaying = false; setUIPlaying(false);
    document.getElementById('wordHidden').style.display = "none";
    const mode = document.getElementById('modeSelect').value, grid = document.getElementById('checkGrid'), tip = document.getElementById('reinforceTip');
    document.getElementById('reinforceArea').style.display = "block"; grid.innerHTML = "";
    if (mode === 'mistakeMode') {
        tip.innerHTML = "🎯 点击写对的词移出";
        currentWords.forEach(word => {
            const el = document.createElement('div'); el.className = "word-tag still-wrong"; el.innerText = word;
            el.onclick = () => { el.className = "word-tag done"; removeMistake(word); setTimeout(() => el.style.visibility = 'hidden', 400); };
            grid.appendChild(el);
        });
    } else {
        tip.innerHTML = "📝 点击写错的词存出错题本";
        currentWords.forEach(word => {
            const el = document.createElement('div'); el.className = "word-tag"; el.innerText = word;
            el.onclick = () => { if (el.classList.contains('still-wrong')) { el.classList.remove('still-wrong'); removeMistake(word); } else { el.classList.add('still-wrong'); addMistake(word); } };
            grid.appendChild(el);
        });
    }
}

function getMistakes() { return JSON.parse(localStorage.getItem('MISTAKE_STORAGE') || "[]"); }
function addMistake(w) { let l = getMistakes(); if (!l.includes(w)) { l.push(w); localStorage.setItem('MISTAKE_STORAGE', JSON.stringify(l)); updateMistakeUI(); } }
function removeMistake(w) { let l = getMistakes().filter(i => i !== w); localStorage.setItem('MISTAKE_STORAGE', JSON.stringify(l)); updateMistakeUI(); }
function updateMistakeUI() { document.getElementById('mistakeBadge').innerText = getMistakes().length; }
function renderMistakeList() {
    const c = document.getElementById('mistakeList'); const m = getMistakes();
    c.innerHTML = m.length ? m.map(w => `<div class="mistake-item"><b>${w}</b><span class="btn-del" onclick="removeMistake('${w}'); renderMistakeList();">移除</span></div>`).join('') : '<div style="text-align:center;color:#ccc;margin-top:40px;">暂无错题</div>';
}
function clearAllMistakes() { if(confirm("确定清空吗？")){ localStorage.setItem('MISTAKE_STORAGE', "[]"); updateMistakeUI(); renderMistakeList(); }}
function quickDictMistakes() { switchModule('dictation'); document.getElementById('modeSelect').value = 'mistakeMode'; toggleMode(); startDictation(); }
function navControl(t) {
    clearTimeout(timer); synth.cancel();
    if (t === 'next') currentIndex = Math.min(currentWords.length - 1, currentIndex + 1);
    if (t === 'prev') currentIndex = Math.max(0, currentIndex - 1);
    if (isPlaying) runPlayer();
}

// 强制在页面所有内容加载后执行初始化
window.addEventListener('load', initApp);
// Streamlit 有时渲染较快，补充一个定时检查
setTimeout(initApp, 100);
</script>
</body>
</html>
"""

# Streamlit 渲染设置
components.html(html_code, height=900, scrolling=True)
