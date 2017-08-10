from flask import Flask, request, render_template, Markup
import requests
from urllib.parse import urlparse
import markdown
import os
import subprocess
import socket


app = Flask(__name__)

try:
    # Looking for the IP address on the K8s
    faas = "faas-netesd.default"
    ip = socket.getaddrinfo(faas, 0, 0, 0, 0)
    faas_port = 8080
    swarm_tag = ""
except Exception:
    # finds Docker swarm host IP upon no K8s
    p1 = subprocess.Popen(["/sbin/ip", "route"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["awk", "/default/ { print $3 }"], stdin=p1.stdout, stdout=subprocess.PIPE)
    faas = (p2.stdout).read().decode("utf-8").replace("\n", "")
    faas_port = 8080
    swarm_tag = "time2code_"


@app.route('/')
def time2code():

    return render_template('index-panel.html')


@app.route('/code', methods=['POST'])
def code():
    if request.method == 'POST':
        data = request.data
        lang = request.args.get('lang')
        hosturl = urlparse(request.url)
        host = hosturl.hostname
        # url = "http://%s:%s/function/time2py" % host
        url = "http://%s:%s/function/%s%s" % (faas, faas_port, swarm_tag, lang)
        # print(url)
        headers = {"Content-Type": "text/plain"}

        code_exec = requests.post(url, data=data, headers=headers)

        resp = code_exec.text

        # print(resp)

        return resp


@app.route('/tutorial')
def tutorial():
    text = request.args.get('code') + "?raw=true"
    straight_text = request.args.get('straight_text')
    get_tut = request.args.get('tut') + "?raw=true"
    code_text = ""
    tut_url = ""
    mark = ""

    if get_tut:
        tut_url = get_tut
        r = requests.get(tut_url)
        mark = r.text
    else:
        tut_url = "https://raw.githubusercontent.com/JockDaRock/Time2Code/master/Sample.md"
        r = requests.get(tut_url)
        mark = r.text

    if text:
        r_text = requests.get(text)
        code_text = r_text.text
    elif straight_text:
        code_text = straight_text

    content = Markup(markdown.markdown(mark, extensions=['pymdownx.github', 'pymdownx.highlight']))
    return render_template('index-tut.html', markdown=content, code_text=code_text)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5555, debug=True)

