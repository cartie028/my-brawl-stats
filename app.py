import os
import requests
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

# Токен берем из настроек Render (Environment Variables)
TOKEN = os.getenv("BRAWL_TOKEN")

CSS = """
:root { --gold: #fcc419; --dark: #0a0a0f; --card: #16161f; }
body { 
    background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; 
    margin: 0; padding: 20px; user-select: none;
}
.search-box { 
    background: #1c1c28; padding: 30px; border-radius: 20px; 
    text-align: center; margin-bottom: 40px; border: 1px solid #333; 
}
input { padding: 12px; border-radius: 8px; border: 1px solid #444; background: #000; color: white; width: 220px; }
button { padding: 12px 25px; border-radius: 8px; border: none; background: var(--gold); font-weight: bold; cursor: pointer; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 30px; perspective: 1200px; }
.card { 
    background: var(--card); padding: 30px; border-radius: 25px; border: 1px solid #2d2d3d;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    transition: transform 0.6s cubic-bezier(0.23, 1, 0.32, 1); transform-style: preserve-3d;
}
.card:hover { border-color: var(--gold); box-shadow: 0 15px 35px rgba(252, 196, 25, 0.2); }
.b-img { 
    width: 140px; height: 140px; object-fit: contain; margin-bottom: 15px; 
    filter: drop-shadow(0 10px 15px rgba(0,0,0,0.7)); transform: translateZ(50px);
}
.b-name { font-size: 18px; font-weight: 900; text-transform: uppercase; transform: translateZ(30px); }
.trophies { color: var(--gold); font-size: 22px; font-weight: 800; transform: translateZ(30px); }
.item-row { display: flex; gap: 10px; margin-top: 15px; transform: translateZ(20px); }
.skill-box { width: 45px; height: 45px; background: rgba(0,0,0,0.5); border-radius: 10px; border: 1px solid #444; padding: 5px; }
.skill-box img { width: 100%; height: 100%; object-fit: contain; }
"""

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><style>{{ css|safe }}</style></head>
<body oncontextmenu="return false;">
    <div class="search-box">
        <h1>BRAWL <span style="color:var(--gold)">STATS</span></h1>
        <form action="/search" method="post">
            <input type="text" name="tag" placeholder="Твой тег" required>
            <button type="submit">ПОИСК</button>
        </form>
    </div>
    {% if data %}
    <div class="grid">
        {% for b in data.brawlers %}
        <div class="card" onmousemove="tilt(event, this)" onmouseleave="reset(this)">
            <img class="b-img" src="https://cdn-old.brawlify.com/brawlers/borderless/{{ b.id }}.png">
            <div class="b-name">{{ b.name }}</div>
            <div class="trophies">{{ b.trophies }} 🏆</div>
            <div class="item-row">
                <div class="skill-box">
                    {% if b.gadgets %}<img src="https://cdn-old.brawlify.com/gadgets/{{ b.gadgets[0].id }}.png">{% endif %}
                </div>
                <div class="skill-box">
                    {% if b.starPowers %}<img src="https://cdn-old.brawlify.com/star-powers/{{ b.starPowers[0].id }}.png">{% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    <script>
        document.onkeydown = function(e) { if(e.keyCode == 123) return false; };
        function tilt(e, el) {
            const r = el.getBoundingClientRect();
            const x = e.clientX - r.left - r.width/2;
            const y = e.clientY - r.top - r.height/2;
            el.style.transform = `rotateY(${x/10}deg) rotateX(${-y/10}deg)`;
        }
        function reset(el) { el.style.transform = `rotateY(0deg) rotateX(0deg)`; }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, css=CSS)

@app.route('/search', methods=['POST'])
def search():
    tag = request.form.get('tag').strip().replace('#', '').upper()
    return redirect(f'/player/{tag}')

@app.route('/player/<tag>')
def player(tag):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"https://api.brawlstars.com/v1/players/%23{tag}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return render_template_string(HTML, css=CSS, data=r.json())
        return render_template_string(HTML, css=CSS, error="Ошибка 403: Проверь токен!")
    except:
        return render_template_string(HTML, css=CSS, error="Ошибка сети")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
