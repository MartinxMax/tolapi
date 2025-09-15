import os
import time
import base64
import uuid
from flask import Flask, request, send_from_directory, render_template_string, make_response, redirect, jsonify
import random
import string
import json
import html
 

app = Flask(__name__)


def generate_password(length=12):
    chars = string.ascii_letters + string.digits  
    return ''.join(random.choice(chars) for _ in range(length))
 
FAILED_ATTEMPTS = {}  
BANNED_IPS = {}     

MAX_ATTEMPTS = 5
BAN_DURATION = 60*5   

GET_DIR = "./get"
PUT_DIR = "./put"
AUTH_PASSWORD = generate_password()

INFO = f'''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣶⣶⣾⣿⣿⣿⣿⣷⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣾⣿⣿⣿⣿⣷⣶⣶⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣠⡴⠾⠟⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠉⠉⠙⠛⠷⢦⣄⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠘⠋⠁⠀⠀⢀⣀⣤⣶⣖⣒⣒⡲⠶⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠶⢖⣒⣒⣲⣶⣤⣀⡀⠀⠀⠈⠙⠂⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣠⢖⣫⣷⣿⣿⣿⣿⣿⣿⣶⣤⡙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⢋⣤⣾⣿⣿⣿⣿⣿⣿⣾⣝⡲⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣄⣀⣠⢿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠻⢿⣿⣿⣦⣳⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣟⣴⣿⣿⡿⠟⠻⢿⣿⣿⣿⣿⣿⣿⣿⡻⣄⣀⣤⠀⠀⠀
⠀⠀⠀⠈⠟⣿⣿⣿⡿⢻⣿⣿⣿⠃⠀⠀⠀⠀⠙⣿⣿⣿⠓⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⣿⣿⣿⠋⠀⠀⠀⠀⠘⣿⣿⣿⡟⢿⣿⣿⣟⠻⠁⠀⠀⠀
⠤⣤⣶⣶⣿⣿⣿⡟⠀⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡏⠀⠀⠀⠀⠀⠀⣹⣿⣿⣷⠈⢻⣿⣿⣿⣶⣦⣤⠤
⠀⠀⠀⠀⠀⢻⣟⠀⠀⣿⣿⣿⣿⡀⠀⠀⠀⠀⢀⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⡀⠀⠀⠀⠀⢀⣿⣿⣿⣿⠀⠀⣿⡟⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠻⣆⠀⢹⣿⠟⢿⣿⣦⣤⣤⣴⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡿⢷⣤⣤⣤⣴⣿⣿⣿⣿⡇⠀⣰⠟⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠙⠂⠀⠙⢀⣀⣿⣿⣿⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⠁⠀⣻⣿⣿⣿⣿⣿⣿⠏⠀⠘⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡈⠻⠿⣿⣿⣿⡿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠻⢿⣿⣿⣿⠿⠛⢁⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⠛⣶⣦⣤⣤⣤⡤⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⢤⣤⣤⣤⣶⣾⠛⠓⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            Maptnh@S-H4CK13{' '*100}tolapi V1.4
{' '*70}https://github.com/MartinxMax/
[Auth-Code]=====>{AUTH_PASSWORD}
'''

os.makedirs(GET_DIR, exist_ok=True)
os.makedirs(PUT_DIR, exist_ok=True)

temp_tokens = {}
upload_tokens = {}

# ---------------------- Dashboard Page Template ----------------------
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TOL-API Dashboard</title>
<style>

body { font-family: "Segoe UI","Arial",sans-serif; background:#f5f6fa; margin:0; padding:0; }
header { background: linear-gradient(90deg,#4a90e2,#3578e5); color:#fff; padding:20px; font-size:1.8em; font-weight:bold; display:flex; justify-content:space-between; align-items:center; }


.container { display:flex; height:calc(100vh - 60px); overflow:hidden; }
.nav { width:160px; background:#fff; border-right:1px solid #ddd; display:flex; flex-direction:column; }
.nav button { padding:12px; border:none; background:none; text-align:left; cursor:pointer; font-size:1em; border-left:4px solid transparent; transition:0.2s; }
.nav button.active { background:#e0e4f7; border-left-color:#4a90e2; font-weight:bold; }
.nav button:hover { background:#f0f4fa; }

.content { flex:1; padding:20px; overflow:auto; }


h3 { margin-top:20px; margin-bottom:10px; color:#333; }
.file-list { display:flex; flex-wrap: wrap; gap:20px; margin-top:5px; }
.file-card { background:#fff; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1); padding:15px; width:200px; display:flex; align-items:center; transition:transform 0.2s, box-shadow 0.2s; }
.file-card:hover { transform:translateY(-3px); box-shadow:0 8px 20px rgba(0,0,0,0.15); }
.file-name { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-weight:500; color:#333; flex:1; }
input[type=checkbox] { margin-right:10px; }


.file-cmd-card { background:#fff; border-radius:8px; padding:10px; margin-top:15px; box-shadow:0 4px 8px rgba(0,0,0,0.1); }
.tabs { margin-top:5px; }
.tab-btn { border:none; background:#e0e4f7; padding:4px 8px; cursor:pointer; margin-right:5px; border-radius:4px; font-size:0.9em; }
.tab-btn.active { background:#4a90e2; color:#fff; }
.tab-content { background:#f0f4fa; padding:6px; border-radius:4px; margin-top:5px; font-family:monospace; font-size:0.9em; max-height:300px; overflow:auto; }
.cmd-line { position: relative; padding:2px 6px; margin:2px 0; border-radius:4px; display:flex; justify-content:flex-start; align-items:center; }
.cmd-line:hover { background: #fff3a1; }


.btn {
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    background: linear-gradient(90deg,#4a90e2,#3578e5);
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-top: 5px;
}
.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.2);
}
</style>

<script>
function showPanel(panelId){
    document.querySelectorAll(".panel").forEach(p=>p.style.display="none");
    document.getElementById(panelId).style.display="block";
    document.querySelectorAll(".nav button").forEach(b=>b.classList.remove("active"));
    document.querySelector("button[data-panel='"+panelId+"']").classList.add("active");
}

function switchTab(btn, tabId){
    let parent = btn.parentNode;
    parent.querySelectorAll(".tab-btn").forEach(b=>b.classList.remove("active"));
    btn.classList.add("active");
    let container = parent.parentNode;
    container.querySelectorAll(".tab-content").forEach(div=>div.style.display="none");
    document.getElementById(tabId).style.display="block";
}

function generateCurlToken(){
    let checkboxes = document.querySelectorAll('#get-panel .file-card input[type=checkbox]:checked');
    if(checkboxes.length===0){ alert('Please select files first'); return; }
    let files = Array.from(checkboxes).map(cb => cb.value);
    let expireInput = document.getElementById("expire-time");
    let expire = expireInput.value || "60";
    fetch("/generate_token_multi?files="+encodeURIComponent(files.join(','))+"&expire="+expire)
    .then(r=>r.json())
    .then(data=>{
        let box = document.getElementById('curl-box');
        box.innerHTML = '';
        data.forEach(block => {
            let fileToken = block.file.replace(/\W/g,'_');
            let html = `<div class="file-cmd-card">
              <b>${block.file}</b>
              <div class="tabs">
                <button class="tab-btn active" onclick="switchTab(this,'win-${fileToken}')">Windows</button>
                <button class="tab-btn" onclick="switchTab(this,'lin-${fileToken}')">Linux</button>
              </div>
              <div id="win-${fileToken}" class="tab-content">
                ${block.windows.map(cmd=>`<div class="cmd-line">${cmd}</div>`).join('')}
              </div>
              <div id="lin-${fileToken}" class="tab-content" style="display:none;">
                ${block.linux.map(cmd=>`<div class="cmd-line">${cmd}</div>`).join('')}
              </div>
            </div>`;
            box.innerHTML += html;
        });
    });
}

function generateUploadToken(){
    let expireInput = document.getElementById("upload-expire");
    let expire = expireInput.value || "60";
    let localFileInput = document.getElementById("local-file");
    let localFile = localFileInput.value || "/path/to/file.txt";

    fetch("/generate_upload_token?expire="+expire)
    .then(r=>r.json())
    .then(data=>{
        let box = document.getElementById('upload-curl-box');
        box.innerHTML = '';
        data.forEach(block=>{
            let fileToken = block.file.replace(/\W/g,'_');

            let winHtml = block.windows.map(cmd=>`<div class="cmd-line">${cmd.replace(/FILE_NAME/g, localFile)}</div>`).join('');
            let linHtml = block.linux.map(cmd=>`<div class="cmd-line">${cmd.replace(/\/path\/to\/file\.txt/g, localFile)}</div>`).join('');

            let html = `<div class="file-cmd-card">
                <b>${block.file}</b>
                <div class="tabs">
                    <button class="tab-btn active" onclick="switchTab(this,'win-up-${fileToken}')">Windows</button>
                    <button class="tab-btn" onclick="switchTab(this,'lin-up-${fileToken}')">Linux</button>
                </div>
                <div id="win-up-${fileToken}" class="tab-content">${winHtml}</div>
                <div id="lin-up-${fileToken}" class="tab-content" style="display:none;">${linHtml}</div>
            </div>`;
            box.innerHTML += html;
        });
    });
}

window.onload = function(){ showPanel('get-panel'); }
</script>
</head>

<body>
<header>
    <span>TOL-API Dashboard</span>
    <a href="https://github.com/MartinxMax/" target="_blank" style="font-size: 0.6em; font-weight: normal; color:#fff; text-decoration:none;">S-H4CK13@Maptnh</a>
</header>

<div class="container">
    <div class="nav">
        <button data-panel="get-panel" onclick="showPanel('get-panel')">Download</button>
        <button data-panel="put-panel" onclick="showPanel('put-panel')">Upload</button>
    </div>

    <div class="content">
        <!-- GET Panel -->
        <div id="get-panel" class="panel">
            <label>Token Expiry (seconds): <input type="number" id="expire-time" value="60" min="1"></label>
            <button class="btn" onclick="generateCurlToken()">Generate Download Commands</button>
            <div id="curl-box"></div>

            {% for folder, info in get_files.items() %}
                <h3>{{ folder or "/" }}{% if info.description %} <small style="color:#666; font-weight:normal;">{{ info.description }}</small>{% endif %}</h3>
                <div class="file-list">
                {% for f in info.files %}
                    <div class="file-card">
                        <input type="checkbox" value="{{ f }}">
                        <span class="file-name">{{ f.split('/')[-1] }}</span>
                    </div>
                {% endfor %}
                </div>
            {% endfor %}
        </div>

        <!-- PUT Panel -->
        <div id="put-panel" class="panel" style="display:none;">
            <label>Token Expiry (seconds): <input type="number" id="upload-expire" value="60" min="1"></label>
            <br>
            <label>Local File Path: <input type="text" id="local-file" placeholder="e.g., C:/Users/Leader/Desktop/file.txt"></label>
            <button class="btn" onclick="generateUploadToken()">Generate Upload Commands</button>
            <div id="upload-curl-box"></div>
        </div>
    </div>
</div>
</body>
</html>
"""


FORBIDDEN_TEMPLATE = "<h1>403 Forbidden</h1>"

# ---------------------- Helper Functions ----------------------
def list_files_grouped(base_dirs):
    grouped = {}
    for base_dir in base_dirs:
        for root, _, filenames in os.walk(base_dir):
            if not filenames: 
                continue
            rel_root = os.path.relpath(root, base_dir).replace("\\", "/")
            folder = rel_root if rel_root != "." else ""
            files_sorted = sorted(filenames, key=lambda f: os.path.getmtime(os.path.join(root, f)), reverse=True)
            
 
            description = ""
            describe_path = os.path.join(root, "describe.conf")
            if os.path.isfile(describe_path):
                try:
                    with open(describe_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and 'describe' in data:
                            description = html.escape(str(data['describe']))
                except Exception:
           
                    pass

            grouped.setdefault(folder, {"files": [], "description": description})
            for f in files_sorted:
                grouped[folder]["files"].append(os.path.join(rel_root, f).replace("\\","/"))
    return grouped

def find_file_in_all_dirs(filename):
    for base_dir in [GET_DIR, PUT_DIR]:
        for root, _, files in os.walk(base_dir):
            if filename in files:
                return os.path.join(root, filename)
    return None

def check_cookie_auth():
    cookie = request.cookies.get("auth")
    if not cookie: return False
    try:
        decoded = base64.b64decode(cookie).decode()
    except:
        return False
    return decoded == AUTH_PASSWORD

def get_user_folder(ip):
    folder = os.path.join(PUT_DIR, ip.replace(":", "_"))
    os.makedirs(folder, exist_ok=True)
    return folder

# ---------------------- Routes ----------------------
@app.route("/")
def login():
    ip = request.remote_addr

  
    if ip in BANNED_IPS:
        if time.time() < BANNED_IPS[ip]:
            remain = int(BANNED_IPS[ip] - time.time())
            return f"<h1>403 Forbidden</h1><p>Your IP is temporarily banned for {remain} seconds due to too many failed login attempts.</p>", 403
        else:
            del BANNED_IPS[ip]

    pwd = request.args.get("pwd")
    if pwd:
        if pwd == AUTH_PASSWORD:
            if ip in FAILED_ATTEMPTS:
                del FAILED_ATTEMPTS[ip]
            resp = make_response(redirect("/dashboard"))
            encoded = base64.b64encode(pwd.encode()).decode()
            resp.set_cookie("auth", encoded, max_age=3600)
            return resp
        else:
            if ip not in FAILED_ATTEMPTS:
                FAILED_ATTEMPTS[ip] = [0, time.time()]
            FAILED_ATTEMPTS[ip][0] += 1
            if FAILED_ATTEMPTS[ip][0] >= MAX_ATTEMPTS:
                BANNED_IPS[ip] = time.time() + BAN_DURATION
                del FAILED_ATTEMPTS[ip]
                return "<h1>403 Forbidden</h1><p>Your IP is temporarily banned due to too many failed login attempts.</p>", 403
            else:
                return f"<script>alert('Wrong password! Attempt {FAILED_ATTEMPTS[ip][0]} of {MAX_ATTEMPTS}'); window.location.href='/'</script>"

    
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>TOL-API</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
    * { margin:0; padding:0; box-sizing:border-box; font-family: 'Inter', sans-serif; }
    body { display:flex; justify-content:center; align-items:center; height:100vh; background: linear-gradient(135deg,#667eea,#764ba2); }
    #pwdBox { background:#fff; padding:40px; border-radius:15px; box-shadow:0 15px 40px rgba(0,0,0,0.3); width:320px; text-align:center; }
    h2 { margin-bottom:20px; color:#333; }
    .pwd-container { position:relative; margin-bottom:20px; }
    input[type="password"], input[type="text"] { width:100%; padding:12px 40px 12px 12px; border-radius:10px; border:1px solid #ddd; font-size:1em; outline:none; transition:0.3s; }
    input[type="password"]:focus, input[type="text"]:focus { border-color:#667eea; box-shadow:0 0 8px rgba(102,126,234,0.3); }
    .eye { position:absolute; right:10px; top:50%; transform:translateY(-50%); cursor:pointer; font-size:1.2em; color:#666; transition:0.2s; }
    .eye:hover { color:#667eea; }
    button { width:100%; padding:12px; background:#667eea; border:none; border-radius:10px; color:#fff; font-size:1em; font-weight:600; cursor:pointer; transition:0.3s; }
    button:hover { background:#5563c1; transform:translateY(-2px); box-shadow:0 6px 15px rgba(0,0,0,0.2); }
    </style>
    </head>
    <body>
        <div id="pwdBox">
            <h2>Auth Code</h2>
            <div class="pwd-container">
                <input type="password" id="pwdInput" placeholder="Code">
                <span class="eye" onclick="togglePwd()">👁️</span>
            </div>
            <button onclick="submitPwd()">Login</button>
        </div>

        <script>
        function submitPwd() {
            let pwd = document.getElementById("pwdInput").value;
            if(!pwd){
                alert("Access canceled");
            } else {
                window.location.href = "/?pwd=" + encodeURIComponent(pwd);
            }
        }

        function togglePwd() {
            let input = document.getElementById("pwdInput");
            input.type = input.type === "password" ? "text" : "password";
        }

        document.getElementById("pwdInput").addEventListener("keypress", function(e){
            if(e.key === "Enter") submitPwd();
        });
        </script>
    </body>
    </html>
    '''


@app.route("/dashboard")
def dashboard():
    if not check_cookie_auth(): return FORBIDDEN_TEMPLATE, 403
    get_files = list_files_grouped([GET_DIR, PUT_DIR])
    put_files = list_files_grouped([PUT_DIR])
    return render_template_string(DASHBOARD_TEMPLATE, get_files=get_files, put_files=put_files)

@app.route("/generate_token_multi")
def generate_token_multi():
    if not check_cookie_auth(): return FORBIDDEN_TEMPLATE, 403
    files = request.args.get("files","").split(',')
    expire = int(request.args.get("expire",300))
    result = []

    for f in files:
        filename_only = os.path.basename(f)
        filepath = find_file_in_all_dirs(filename_only)
        if not filepath or not os.path.isfile(filepath):
            continue

        token = uuid.uuid4().hex
        temp_tokens[token] = (filepath, time.time()+expire)
        url = f"{request.host_url}download_with_token/{token}"

        windows_cmds = [
            f'powershell -c "Invoke-WebRequest -Uri \'{url}\' -OutFile \'{filename_only}\'"',
            f'certutil -urlcache -split -f "{url}" "{filename_only}"',
            f'curl -o "{filename_only}" "{url}"',
            f'wget -O "{filename_only}" "{url}"'
        ]
        linux_cmds = [
            f'curl -o "{filename_only}" "{url}"',
            f'wget -O "{filename_only}" "{url}"',
            f'aria2c -o "{filename_only}" "{url}"',
            f'axel -o "{filename_only}" "{url}"'
        ]
        result.append({"file": filename_only, "windows": windows_cmds, "linux": linux_cmds})

    return jsonify(result)

@app.route("/download_with_token/<token>", methods=["GET"])
def download_with_token(token):
    data = temp_tokens.get(token)
    if not data: return FORBIDDEN_TEMPLATE, 403
    filepath, expire = data
    if time.time() > expire:
        del temp_tokens[token]
        return FORBIDDEN_TEMPLATE, 403
    return send_from_directory(os.path.dirname(filepath), os.path.basename(filepath), as_attachment=True)

@app.route("/generate_upload_token")
def generate_upload_token():
    if not check_cookie_auth(): return FORBIDDEN_TEMPLATE, 403
    expire = int(request.args.get("expire", 300))
    token = uuid.uuid4().hex
    upload_tokens[token] = time.time() + expire

    windows_cmds = [
 
	f'Terminal in Powershell :</br>$f=Join-Path $PWD \'FILE_NAME\'; $u=\'{request.host_url}upload_with_token/{token}\'; $wc=New-Object System.Net.WebClient; $r=$wc.UploadFile($u,$f); [System.Text.Encoding]::UTF8.GetString($r)',
        f'Terminal in CMD :</br>powershell.exe -NoProfile -Command "$f=Join-Path $PWD \'FILE_NAME\'; $u=\'{request.host_url}upload_with_token/{token}\'; $wc=New-Object System.Net.WebClient; $r=$wc.UploadFile($u,$f); [System.Text.Encoding]::UTF8.GetString($r)"',
        f'curl.exe -X POST -F "file=@FILE_NAME" "{request.host_url}upload_with_token/{token}"',
        f'aria2 --post-file=FILE_NAME "{request.host_url}upload_with_token/{token}"',
        f'lftp -c "open {request.host_url}; put FILE_NAME"'
    ]
    linux_cmds = [
        f'curl -X POST -F "file=@/path/to/file.txt" "{request.host_url}upload_with_token/{token}"',
        f'aria2 --post-file=/path/to/file.txt "{request.host_url}upload_with_token/{token}"',
        f'lftp -c "open {request.host_url}; put /path/to/file.txt"',
        f"python3 -c 'import requests; r = requests.post(\"{request.host_url}upload_with_token/{token}\", files={{\"file\": open(\"/path/to/file.txt\",\"rb\")}}); print(\"o_o---success!!!\" if r.status_code == 200 else \"X_X----failed\")'",
        f'powershell -c "Invoke-WebRequest -Method POST -InFile \'/path/to/file.txt\' -Uri \'{request.host_url}upload_with_token/{token}\'"'
    ]
    return jsonify([{"file":"Upload Commands","windows":windows_cmds,"linux":linux_cmds}])

@app.route("/upload_with_token/<token>", methods=["POST"])
def upload_with_token(token):
    expire_time = upload_tokens.get(token)
    if not expire_time or time.time() > expire_time:
        return FORBIDDEN_TEMPLATE, 403

    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    orig_name = file.filename
    if not orig_name:
        return "Invalid filename", 400
    _, ext = os.path.splitext(orig_name)
    timestamp_name = f"{int(time.time() * 1000)}{ext}" 
    user_folder = get_user_folder(request.remote_addr)
    os.makedirs(user_folder, exist_ok=True)
    save_path = os.path.join(user_folder, timestamp_name)
    file.save(save_path)

    return f"File uploaded successfully to {save_path}"

def find_available_port(preferred=80, fallback=10831):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('', preferred))
        s.close()
        return preferred
    except OSError:
        return fallback

# ---------------------- Run ----------------------
if __name__ == "__main__":
    print('*'*100)
    print(INFO)
    port = find_available_port()
    print('*'*100)
    app.run(host="0.0.0.0", port=port, debug=False)
