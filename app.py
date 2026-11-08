from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# --- Simulated Database ---
class backend:
    users = {
        "admin@marine.org": {"name": "system admin", "role": "admin", "status": "active", "strikes": 0},
        "dr.smith@marine.org": {"name": "dr. smith", "role": "researcher", "status": "approved", "strikes": 0},
        "dr.jones@marine.org": {"name": "dr. jones", "role": "researcher", "status": "approved", "strikes": 0},
        "john@example.com": {"name": "john doe", "role": "user", "status": "active", "strikes": 0}
    }

    posts = [
        {"id": 1, "author_email": "dr.smith@marine.org", "title": "Great White Migration 2026", "content": "Just uploaded tracking data for the Pacific.", "date": "2026-11-07"}
    ]

    comments = [
        {"id": 1, "post_id": 1, "author_email": "john@example.com", "content": "Fascinating study! What about temperature?", "date": "2026-11-07"}
    ]

    species_db = [
        {"specid": 1, "name": "great white", "type": "fish", "lifespan": 70, "status": "vulnerable", "habitat": "ocean", "climate": "temperate", "img": "https://images.unsplash.com/photo-1560275619-4662e36fa65c?q=80&w=1000", "bgimg": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=2000", "gradient": "from-blue-400 via-gray-300 to-white", "shadow": "rgba(96,165,250,0.4)", "glowclass": "glow-shark", "overlaygradient": "from-blue-900 via-slate-900 to-[#050510]", "desc": "A vulnerable fish found in temperate climates."},
        {"specid": 2, "name": "sea turtle", "type": "reptile", "lifespan": 50, "status": "endangered", "habitat": "reef", "climate": "tropical", "img": "https://images.unsplash.com/photo-1518467166778-b88f373ff255?q=80&w=1000", "bgimg": "https://images.unsplash.com/photo-1546026423-cc4642628d2b?q=80&w=2000", "gradient": "from-green-400 via-teal-400 to-cyan-400", "shadow": "rgba(52,211,153,0.4)", "glowclass": "glow-turtle", "overlaygradient": "from-teal-900 via-cyan-900 to-[#050510]", "desc": "An endangered reptile found in tropical climates."}
    ]

    habitats_db = []
    pending_species = []

    researches_db = [
        {"id": 1, "topic": "Great White Migration", "description": "Tracking global movements.", "date": "2026-08-15", "researcher": "dr.smith@marine.org", "species": "great white", "climate": "temperate", "pdf_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}
    ]

current_user_email = "admin@marine.org"

def get_current_user():
    return backend.users.get(current_user_email, {})

def get_top_blog_contributors():
    activity = Counter([p["author_email"] for p in backend.posts] + [c["author_email"] for c in backend.comments])
    return [user[0] for user in activity.most_common(5)]

def check_strikes(email):
    if email in backend.users and backend.users[email]['strikes'] >= 3:
        backend.users[email]['status'] = 'banned'

# --- Routes ---
@app.route('/')
def root():
    tab = request.args.get('tab', 'login')
    return render_template('login.html', tab=tab)

@app.route('/login', methods=['POST'])
def login():
    global current_user_email
    email = request.form.get('username')
    role = request.form.get('role', 'user')
    
    if email not in backend.users:
        status = "pending" if role == "researcher" else "active"
        backend.users[email] = {"name": email.split('@')[0], "role": role, "status": status, "strikes": 0}
    
    user_info = backend.users[email]
    if user_info["status"] == "banned":
        return "Account is banned.", 403
    if role == "researcher" and user_info["status"] == "pending":
        return "Your researcher account is awaiting admin approval.", 403
        
    current_user_email = email
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('reg_username')
    role = request.form.get('reg_role')
    if email not in backend.users:
        status = "pending" if role == "researcher" else "active"
        backend.users[email] = {"name": email.split('@')[0], "role": role, "status": status, "strikes": 0}
    return redirect(url_for('root', tab='login'))

@app.route('/home')
def home():
    user = get_current_user()
    r_counts = Counter([r['researcher'] for r in backend.researches_db])
    top_researchers = [{"email": e, "name": backend.users.get(e, {}).get("name", e), "count": c} for e, c in r_counts.most_common(3)]
    s_counts = Counter([r['species'] for r in backend.researches_db])
    top_species = [{"name": sp, "count": c} for sp, c in s_counts.most_common(3)]
    c_counts = Counter([r['climate'] for r in backend.researches_db])
    top_regions = [{"name": cl, "count": c} for cl, c in c_counts.most_common(3)]
    recent_posts = backend.posts[::-1][:3]
    for p in recent_posts:
        p['author_name'] = backend.users.get(p['author_email'], {}).get('name', 'Unknown')
    return render_template('home.html', user=user, recent_posts=recent_posts, top_researchers=top_researchers, top_species=top_species, top_regions=top_regions)

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    category = request.args.get('category', 'species')
    results = []
    if category == 'species':
        results = [s for s in backend.species_db if query in s['name'].lower() or query in s['type'].lower()]
    elif category == 'regions':
        results = [s for s in backend.species_db if query in s['climate'].lower() or query in s['habitat'].lower()]
    elif category == 'researchers':
        results = [{"email": e, **u} for e, u in backend.users.items() if u['role'] == 'researcher' and (query in u['name'].lower() or query in e.lower())]
    return render_template('search_results.html', query=query, category=category, results=results, user=get_current_user())

@app.route('/species')
def species():
    spec_id = request.args.get('specid', type=int)
    search_q = request.args.get('search', '').lower()
    hab_f = request.args.get('habitat', '')
    clim_f = request.args.get('climate', '')
    type_f = request.args.get('type', '')

    filtered = [s for s in backend.species_db if 
                (not search_q or search_q in s['name'].lower()) and 
                (not hab_f or s['habitat'] == hab_f) and 
                (not clim_f or s['climate'] == clim_f) and 
                (not type_f or s['type'] == type_f)]

    grouped_data = {}
    for s in filtered:
        grouped_data.setdefault(s['habitat'], []).append(s)

    active_species = next((s for s in backend.species_db if s['specid'] == spec_id), None)
    if not active_species and filtered: active_species = filtered[0]
    if active_species:
        active_species['researches'] = [r for r in backend.researches_db if r['species'] == active_species['name']]

    return render_template('species.html', grouped_data=grouped_data, active_species=active_species, 
                           habitats=sorted(set(s['habitat'] for s in backend.species_db)), 
                           climates=sorted(set(s['climate'] for s in backend.species_db)), 
                           types=sorted(set(s['type'] for s in backend.species_db)),
                           curr_search=search_q, curr_hab=hab_f, curr_clim=clim_f, curr_type=type_f)

@app.route('/blog')
def blog():
    top = get_top_blog_contributors()
    hydrated = []
    for p in backend.posts[::-1]:
        pd = p.copy()
        author = backend.users.get(p["author_email"], {"name": "Unknown", "role": "user"})
        pd.update({"author_name": author["name"], "author_role": author["role"], "is_top": p["author_email"] in top, "post_comments": []})
        for c in backend.comments:
            if c["post_id"] == p["id"]:
                cd = c.copy()
                c_author = backend.users.get(c["author_email"], {"name": "Unknown", "role": "user"})
                cd.update({"author_name": c_author["name"], "author_role": c_author["role"], "is_top": c["author_email"] in top})
                pd["post_comments"].append(cd)
        hydrated.append(pd)
    return render_template('blog.html', posts=hydrated, user=get_current_user())

@app.route('/create_post', methods=['POST'])
def create_post():
    backend.posts.append({"id": len(backend.posts) + 1, "author_email": current_user_email, "title": request.form.get('title'), "content": request.form.get('content'), "date": datetime.now().strftime("%Y-%m-%d")})
    return redirect(url_for('blog'))

@app.route('/create_comment', methods=['POST'])
def create_comment():
    backend.comments.append({"id": len(backend.comments) + 1, "post_id": int(request.form.get('post_id')), "author_email": current_user_email, "content": request.form.get('content'), "date": datetime.now().strftime("%Y-%m-%d")})
    return redirect(url_for('blog'))

@app.route('/research/<int:research_id>')
def research(research_id):
    res = next((r for r in backend.researches_db if r['id'] == research_id), None)
    return render_template('research.html', research=res, user=get_current_user())

@app.route('/researcher/<email>')
def researcher_profile(email):
    return render_template('researcher.html', researcher=backend.users.get(email, {}), works=[r for r in backend.researches_db if r['researcher'] == email], email=email, user=get_current_user())

@app.route('/upload_research', methods=['GET', 'POST'])
def upload_research():
    if request.method == 'POST':
        backend.researches_db.append({
            "id": len(backend.researches_db) + 1,
            "topic": request.form.get('topic'),
            "description": request.form.get('description'),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "researcher": current_user_email,
            "species": request.form.get('species'),
            "climate": request.form.get('climate'),
            "pdf_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        })
        return redirect(url_for('species'))
    return render_template('upload_research.html', species_list=backend.species_db, climates=sorted(set(s['climate'] for s in backend.species_db)), user=get_current_user())

@app.route('/add_entity', methods=['GET', 'POST'])
def add_entity():
    user = get_current_user()
    selected_type = request.args.get('type', 'species')
    
    if request.method == 'POST':
        entity_type = request.form.get('entity_type')
        if entity_type == 'species':
            new_spec = {
                "specid": len(backend.species_db) + len(backend.pending_species) + 1,
                "name": request.form.get('name'), "type": request.form.get('type'),
                "lifespan": int(request.form.get('lifespan') or 0), "status": request.form.get('status'),
                "habitat": request.form.get('habitat'), "climate": request.form.get('climate'),
                "img": request.form.get('img'), "bgimg": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=2000",
                "gradient": "from-gray-400 to-white", "shadow": "rgba(255,255,255,0.4)", "glowclass": "", "overlaygradient": "from-gray-900 to-[#050510]", "desc": "Newly submitted entity."
            }
            if user['role'] == 'admin': backend.species_db.append(new_spec)
            else: backend.pending_species.append(new_spec)
        elif entity_type == 'habitat':
            backend.habitats_db.append({"id": len(backend.habitats_db) + 1, "name": request.form.get('name'), "location": request.form.get('location'), "latitude": float(request.form.get('latitude') or 0), "longitude": float(request.form.get('longitude') or 0), "climate": request.form.get('climate'), "img": request.form.get('img')})
        return redirect(url_for('home'))
    return render_template('add_entity.html', user=user, selected_type=selected_type)

@app.route('/admin')
def admin_panel():
    if get_current_user().get('role') != 'admin': return "Unauthorized", 403
    return render_template('admin.html', users=backend.users, posts=backend.posts, pending_researchers=[e for e, u in backend.users.items() if u['role'] == 'researcher' and u['status'] == 'pending'], researches=backend.researches_db, pending_species=backend.pending_species, user=get_current_user())

@app.route('/admin/approve_researcher/<email>')
def approve_researcher(email):
    if email in backend.users: backend.users[email]['status'] = 'approved'
    return redirect(url_for('admin_panel'))

@app.route('/admin/strike/<email>')
def strike_user(email):
    if email in backend.users:
        backend.users[email]['strikes'] += 1
        check_strikes(email)
    return redirect(url_for('admin_panel'))

@app.route('/admin/ban/<email>')
def ban_user(email):
    if email in backend.users: backend.users[email]['status'] = 'banned'
    return redirect(request.referrer or url_for('admin_panel'))

@app.route('/admin/delete_post/<int:post_id>')
def delete_post(post_id):
    backend.posts = [p for p in backend.posts if p['id'] != post_id]
    return redirect(url_for('admin_panel'))

@app.route('/admin/flag_research/<int:res_id>')
def flag_research(res_id):
    for r in backend.researches_db:
        if r['id'] == res_id:
            author = r['researcher']
            if author in backend.users:
                backend.users[author]['strikes'] += 1
                check_strikes(author)
    return redirect(request.referrer or url_for('admin_panel'))

@app.route('/admin/approve_species/<int:spec_id>')
def approve_species(spec_id):
    for s in backend.pending_species:
        if s['specid'] == spec_id:
            backend.species_db.append(s)
            backend.pending_species.remove(s)
            break
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)