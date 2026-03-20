import os
from flask import Flask, render_template_string

app = Flask(__name__)

from dashboard import creer_dashboard
dash_bancaire = creer_dashboard(app)

from dash import Dash, html
import dash_bootstrap_components as dbc


def creer_placeholder(server, nom, chemin, emoji):
    d = Dash(__name__, server=server, url_base_pathname=chemin,
             external_stylesheets=[dbc.themes.FLATLY])
    d.layout = dbc.Container([
        dbc.Row([dbc.Col([
            html.Span(emoji + " ", style={"fontSize": "28px"}),
            html.H3(f"Secteur {nom}", className="d-inline fw-bold"),
            html.P("En cours de développement", className="text-muted mt-1"),
        ], className="p-4 border-bottom")]),
        dbc.Alert("Ce dashboard sera disponible prochainement.", color="info", className="mt-4"),
        html.A("← Retour", href="/", className="btn btn-outline-secondary btn-sm"),
    ], className="mt-4")
    return d


dash_energie   = creer_placeholder(app, "Énergétique", "/energetique/", "⚡")
dash_assurance = creer_placeholder(app, "Assurance",   "/assurance/",   "🛡️")


PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SenBank Analytics — Tableau de bord bancaire</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root {
    --teal:   #0f766e;
    --teal2:  #0d9488;
    --amber:  #d97706;
    --ink:    #1e293b;
    --muted:  #64748b;
    --border: #e2e8f0;
    --bg:     #f8fafc;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { font-family: 'Inter', system-ui, sans-serif; background: #fff; color: var(--ink); }

/* NAV */
.nav {
    background: #fff;
    border-bottom: 1px solid var(--border);
    padding: 0 48px;
    height: 60px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
}
.nav-brand {
    font-size: 17px; font-weight: 900; color: var(--ink);
    letter-spacing: -0.5px; text-decoration: none;
}
.nav-brand span { color: var(--teal); }
.nav-links { display: flex; gap: 32px; }
.nav-links a {
    font-size: 13px; font-weight: 600; color: var(--muted);
    text-decoration: none; transition: color .2s;
}
.nav-links a:hover { color: var(--ink); }
.nav-tag {
    font-size: 11px; font-weight: 700; color: var(--teal);
    background: #f0fdfa; border: 1px solid #99f6e4;
    border-radius: 20px; padding: 4px 12px;
}

/* HERO */
.hero {
    padding: 80px 48px 72px;
    display: grid; grid-template-columns: 1fr 420px; gap: 64px;
    align-items: center; max-width: 1200px; margin: 0 auto;
}
.hero-eyebrow {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 2px; color: var(--teal); margin-bottom: 20px;
}
.hero h1 {
    font-size: 52px; font-weight: 900; line-height: 1.05;
    letter-spacing: -2.5px; color: var(--ink); margin-bottom: 20px;
}
.hero h1 strong { color: var(--teal); }
.hero-desc {
    font-size: 16px; color: var(--muted); line-height: 1.8;
    max-width: 480px; margin-bottom: 36px; font-weight: 400;
}
.hero-actions { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.btn-primary {
    background: var(--ink); color: #fff;
    padding: 13px 28px; border-radius: 10px;
    font-size: 14px; font-weight: 700; text-decoration: none;
    display: inline-block; transition: background .2s;
}
.btn-primary:hover { background: #0f172a; color: #fff; }
.btn-outline {
    background: #fff; color: var(--ink);
    border: 1.5px solid var(--border);
    padding: 13px 24px; border-radius: 10px;
    font-size: 14px; font-weight: 600; text-decoration: none;
    display: inline-block; transition: border-color .2s;
}
.btn-outline:hover { border-color: var(--ink); color: var(--ink); }

/* STATS CARD (right side of hero) */
.stats-card {
    background: var(--ink);
    border-radius: 20px; padding: 32px;
    color: #fff;
}
.stats-card-title {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 2px; color: #94a3b8; margin-bottom: 24px;
}
.stat-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 0; border-bottom: 1px solid #334155;
}
.stat-row:last-child { border-bottom: none; }
.stat-row-label { font-size: 13px; color: #94a3b8; font-weight: 500; }
.stat-row-val {
    font-size: 22px; font-weight: 900; color: #fff; letter-spacing: -1px;
}
.stat-row-val span { font-size: 12px; color: #10b981; font-weight: 700; margin-left: 6px; }

/* DIVIDER */
.section-divider {
    border: none; border-top: 1px solid var(--border);
    margin: 0 48px;
}

/* SECTORS */
.sectors {
    padding: 72px 48px;
    max-width: 1200px; margin: 0 auto;
}
.sectors-header { margin-bottom: 48px; }
.sectors-header h2 {
    font-size: 36px; font-weight: 900; letter-spacing: -1.5px;
    margin-bottom: 8px;
}
.sectors-header p { font-size: 15px; color: var(--muted); }
.sectors-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
}
.sector-card {
    border: 1.5px solid var(--border);
    border-radius: 16px; padding: 28px;
    transition: border-color .25s, box-shadow .25s;
    position: relative;
    display: flex; flex-direction: column;
}
.sector-card:hover {
    border-color: var(--teal); box-shadow: 0 8px 32px rgba(15,118,110,.08);
}
.sector-num {
    font-size: 48px; font-weight: 900; letter-spacing: -3px;
    color: var(--border); margin-bottom: 20px; line-height: 1;
}
.sector-card.active .sector-num { color: var(--teal); opacity: .25; }
.sector-status {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.5px; padding: 4px 10px; border-radius: 6px;
    display: inline-flex; align-items: center; gap: 5px;
    margin-bottom: 16px; width: fit-content;
}
.status-live { background: #f0fdfa; color: var(--teal); }
.status-soon { background: var(--bg); color: #94a3b8; }
.status-live::before { content: "●"; font-size: 7px; }
.sector-card h3 {
    font-size: 22px; font-weight: 800; letter-spacing: -0.5px;
    margin-bottom: 10px;
}
.sector-card p {
    font-size: 13px; color: var(--muted); line-height: 1.75;
    margin-bottom: 24px; flex-grow: 1;
}
.sector-kpis { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 24px; }
.kpi-tag {
    font-size: 11px; font-weight: 600; color: var(--muted);
    background: var(--bg); border: 1px solid var(--border);
    padding: 4px 10px; border-radius: 6px;
}
.sector-link {
    font-size: 13px; font-weight: 700; color: var(--teal);
    text-decoration: none; display: inline-flex; align-items: center; gap: 6px;
    transition: gap .2s;
}
.sector-link:hover { gap: 10px; color: var(--teal2); }
.sector-link-dis {
    font-size: 13px; font-weight: 600; color: #cbd5e1;
    display: inline-flex; align-items: center; gap: 6px;
}

/* DATA SECTION */
.data-section {
    background: var(--bg); border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 56px 48px;
}
.data-inner {
    max-width: 1200px; margin: 0 auto;
    display: grid; grid-template-columns: 1fr 1fr; gap: 64px;
    align-items: center;
}
.data-section h2 {
    font-size: 32px; font-weight: 900; letter-spacing: -1.5px;
    margin-bottom: 16px;
}
.data-section p { font-size: 14px; color: var(--muted); line-height: 1.8; }
.method-list { list-style: none; margin-top: 24px; }
.method-list li {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid var(--border);
    font-size: 13px; color: var(--muted);
}
.method-list li:last-child { border-bottom: none; }
.method-list li strong { color: var(--ink); font-weight: 700; display: block; margin-bottom: 2px; }
.m-icon { font-size: 18px; flex-shrink: 0; margin-top: 1px; }

/* FOOTER */
footer {
    padding: 28px 48px;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 12px;
    font-size: 12px; color: #94a3b8;
    border-top: 1px solid var(--border);
}
footer strong { color: var(--ink); }

@media(max-width: 900px) {
    .hero { grid-template-columns: 1fr; }
    .stats-card { display: none; }
    .sectors-grid { grid-template-columns: 1fr; }
    .data-inner { grid-template-columns: 1fr; }
    .nav { padding: 0 20px; }
    .nav-links { display: none; }
    .hero, .sectors { padding-left: 20px; padding-right: 20px; }
    .data-section { padding: 40px 20px; }
    footer { padding: 20px; }
}
</style>
</head>
<body>

<nav class="nav">
    <a class="nav-brand" href="/">Sen<span>Bank</span> Analytics</a>
    <div class="nav-links">
        <a href="#secteurs">Secteurs</a>
        <a href="#donnees">Données</a>
        <a href="/bancaire/">Dashboard</a>
    </div>
    <span class="nav-tag">BCEAO · 2015–2020</span>
</nav>

<section class="hero">
    <div>
        <div class="hero-eyebrow">Plateforme d'analyse décisionnelle · Sénégal</div>
        <h1>Suivi des<br>performances<br><strong>bancaires</strong></h1>
        <p class="hero-desc">
            Analyse comparative de 24 établissements bancaires sénégalais
            sur la période 2015–2020, à partir des données officielles BCEAO
            et de la base BASE_SENEGAL2.
        </p>
        <div class="hero-actions">
            <a href="/bancaire/" class="btn-primary">Ouvrir le dashboard →</a>
            <a href="#secteurs" class="btn-outline">Voir les secteurs</a>
        </div>
    </div>
    <div class="stats-card">
        <div class="stats-card-title">Données de la plateforme</div>
        <div class="stat-row">
            <span class="stat-row-label">Banques analysées</span>
            <span class="stat-row-val">24</span>
        </div>
        <div class="stat-row">
            <span class="stat-row-label">Observations</span>
            <span class="stat-row-val">134</span>
        </div>
        <div class="stat-row">
            <span class="stat-row-label">Années couvertes</span>
            <span class="stat-row-val">6 <span>2015–2020</span></span>
        </div>
        <div class="stat-row">
            <span class="stat-row-label">Indicateurs clés</span>
            <span class="stat-row-val">10+</span>
        </div>
        <div class="stat-row">
            <span class="stat-row-label">Source principale</span>
            <span class="stat-row-val" style="font-size:14px;">BCEAO</span>
        </div>
    </div>
</section>

<hr class="section-divider">

<section class="sectors" id="secteurs">
    <div class="sectors-header">
        <h2>Secteurs d'analyse</h2>
        <p>Chaque module couvre un secteur distinct avec ses propres indicateurs et visualisations.</p>
    </div>
    <div class="sectors-grid">

        <div class="sector-card active">
            <div class="sector-num">01</div>
            <span class="sector-status status-live">Disponible</span>
            <h3>Bancaire</h3>
            <p>Positionnement des 24 banques agréées au Sénégal : bilans, PNB, ratios
               prudentiels, solvabilité, liquidité et score de positionnement BCEAO.</p>
            <div class="sector-kpis">
                <span class="kpi-tag">Bilan</span>
                <span class="kpi-tag">PNB</span>
                <span class="kpi-tag">ROA</span>
                <span class="kpi-tag">Solvabilité</span>
                <span class="kpi-tag">Coeff. exploit.</span>
            </div>
            <a href="/bancaire/" class="sector-link">Accéder au dashboard →</a>
        </div>

        <div class="sector-card">
            <div class="sector-num">02</div>
            <span class="sector-status status-soon">En développement</span>
            <h3>Énergétique</h3>
            <p>Suivi de la production énergétique sénégalaise, analyse de la capacité
               installée, du rendement et des indicateurs de performance du secteur.</p>
            <div class="sector-kpis">
                <span class="kpi-tag">Production</span>
                <span class="kpi-tag">Rendement</span>
                <span class="kpi-tag">Capacité</span>
            </div>
            <span class="sector-link-dis">Bientôt disponible</span>
        </div>

        <div class="sector-card">
            <div class="sector-num">03</div>
            <span class="sector-status status-soon">En développement</span>
            <h3>Assurance</h3>
            <p>Pilotage du portefeuille assurance : sinistralité, segmentation du risque,
               primes encaissées et analyse de la rentabilité par zone géographique.</p>
            <div class="sector-kpis">
                <span class="kpi-tag">Sinistres</span>
                <span class="kpi-tag">Primes</span>
                <span class="kpi-tag">Loss Ratio</span>
            </div>
            <span class="sector-link-dis">Bientôt disponible</span>
        </div>

    </div>
</section>

<section class="data-section" id="donnees">
    <div class="data-inner">
        <div>
            <h2>Sources et<br>méthodologie</h2>
            <p>
                Les données proviennent de deux sources complémentaires :
                la base BASE_SENEGAL2 couvrant 2015–2020, et les rapports
                annuels BCEAO. Le pipeline de traitement inclut le nettoyage,
                le calcul des ratios financiers et le stockage dans MongoDB Atlas.
            </p>
        </div>
        <ul class="method-list">
            <li>
                <span class="m-icon">🗄️</span>
                <div>
                    <strong>MongoDB Atlas</strong>
                    Base de données cloud — 134 observations nettoyées
                </div>
            </li>
            <li>
                <span class="m-icon">🐍</span>
                <div>
                    <strong>Flask + Dash + Plotly</strong>
                    Orchestration multi-secteurs et visualisations interactives
                </div>
            </li>
            <li>
                <span class="m-icon">📄</span>
                <div>
                    <strong>Extraction PDF (pdfplumber)</strong>
                    Traitement automatisé des rapports BCEAO
                </div>
            </li>
            <li>
                <span class="m-icon">🚀</span>
                <div>
                    <strong>Déploiement Render</strong>
                    Production via Gunicorn — Python 3.11
                </div>
            </li>
        </ul>
    </div>
</section>

<footer>
    <span>© 2025 <strong>SenBank Analytics</strong> — Sénégal</span>
    <span>Adote Mario-Giovani ADUAYI-AKUE</span>
    <a href="/bancaire/" style="color: var(--teal); font-weight: 700; text-decoration: none;">Dashboard Bancaire →</a>
</footer>

</body>
</html>"""


@app.route("/")
def accueil():
    return render_template_string(PAGE)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=port)
