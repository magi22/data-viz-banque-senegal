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

/* BACK TO TOP */
#back-top {
    position: fixed; bottom: 96px; right: 24px; z-index: 500;
    width: 40px; height: 40px; border-radius: 50%;
    background: var(--ink); color: #fff; border: none; cursor: pointer;
    font-size: 18px; display: none; align-items: center; justify-content: center;
    box-shadow: 0 4px 16px rgba(0,0,0,.18); transition: background .2s, transform .2s;
}
#back-top:hover { background: var(--teal); transform: translateY(-2px); }
#back-top.show { display: flex; }

/* CHATBOT */
#chat-btn {
    position: fixed; bottom: 24px; right: 24px; z-index: 600;
    width: 52px; height: 52px; border-radius: 50%;
    background: var(--teal); color: #fff; border: none; cursor: pointer;
    font-size: 22px; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 20px rgba(15,118,110,.35); transition: transform .2s, background .2s;
}
#chat-btn:hover { transform: scale(1.08); background: var(--teal2); }
#chat-win {
    position: fixed; bottom: 88px; right: 24px; z-index: 600;
    width: 320px; max-height: 480px; background: #fff;
    border-radius: 18px; box-shadow: 0 8px 40px rgba(0,0,0,.15);
    border: 1px solid var(--border); display: none; flex-direction: column;
    overflow: hidden;
}
#chat-win.open { display: flex; }
.chat-head {
    background: var(--ink); color: #fff; padding: 14px 18px;
    display: flex; align-items: center; justify-content: space-between;
}
.chat-head-title { font-size: 14px; font-weight: 700; }
.chat-head-sub { font-size: 10px; color: #94a3b8; margin-top: 2px; }
#chat-close { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 18px; line-height: 1; }
#chat-close:hover { color: #fff; }
.chat-msgs {
    flex: 1; overflow-y: auto; padding: 14px 14px 8px;
    display: flex; flex-direction: column; gap: 10px;
}
.chat-msgs::-webkit-scrollbar { width: 3px; }
.chat-msgs::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 2px; }
.msg { max-width: 88%; padding: 9px 12px; border-radius: 12px; font-size: 12px; line-height: 1.6; }
.msg.bot { background: #f1f5f9; color: var(--ink); align-self: flex-start; border-bottom-left-radius: 4px; }
.msg.user { background: var(--teal); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; }
.chat-topics {
    padding: 6px 14px 10px; display: flex; flex-wrap: wrap; gap: 6px;
}
.topic-btn {
    font-size: 11px; font-weight: 600; color: var(--teal);
    background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 20px;
    padding: 4px 12px; cursor: pointer; transition: background .15s;
    white-space: nowrap;
}
.topic-btn:hover { background: #ccfbf1; }
.chat-input-row {
    padding: 10px 14px 14px; display: flex; gap: 8px;
    border-top: 1px solid var(--border);
}
#chat-input {
    flex: 1; border: 1px solid var(--border); border-radius: 20px;
    padding: 7px 14px; font-size: 12px; outline: none;
    font-family: inherit;
}
#chat-input:focus { border-color: var(--teal); }
#chat-send {
    background: var(--teal); color: #fff; border: none; border-radius: 50%;
    width: 32px; height: 32px; cursor: pointer; font-size: 14px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: background .15s;
}
#chat-send:hover { background: var(--teal2); }
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
            sur la période 2015–2022, à partir des données officielles BCEAO
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
            <span class="stat-row-val">180</span>
        </div>
        <div class="stat-row">
            <span class="stat-row-label">Années couvertes</span>
            <span class="stat-row-val">8 <span>2015–2022</span></span>
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
                    <strong>Rapport BCEAO 2022</strong>
                    <a href="https://www.bceao.int/fr/publications/bilans-et-comptes-de-resultats-des-banques-etablissements-financiers-et-compagnies" target="_blank" rel="noopener" style="color:var(--teal);font-size:12px;">Bilans et comptes de résultat UMOA — bceao.int ↗</a>
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

<!-- BACK TO TOP -->
<button id="back-top" onclick="window.scrollTo({top:0,behavior:'smooth'})" title="Retour en haut">↑</button>

<!-- CHATBOT AIDE -->
<button id="chat-btn" onclick="toggleChat()" title="Aide">💬</button>

<div id="chat-win">
  <div class="chat-head">
    <div>
      <div class="chat-head-title">🏦 Aide SenBank Analytics</div>
      <div class="chat-head-sub">Réponse instantanée</div>
    </div>
    <button id="chat-close" onclick="toggleChat()">×</button>
  </div>
  <div class="chat-msgs" id="chat-msgs">
    <div class="msg bot">Bonjour ! Je suis l'assistant de <strong>SenBank Analytics</strong>. Comment puis-je vous aider ?</div>
  </div>
  <div class="chat-topics" id="chat-topics">
    <button class="topic-btn" onclick="askTopic('charger')">📂 Charger des données</button>
    <button class="topic-btn" onclick="askTopic('dashboard')">📊 Utiliser le dashboard</button>
    <button class="topic-btn" onclick="askTopic('filtres')">🔍 Les filtres</button>
    <button class="topic-btn" onclick="askTopic('pdf')">📄 Rapport PDF</button>
    <button class="topic-btn" onclick="askTopic('sources')">📖 Sources</button>
    <button class="topic-btn" onclick="askTopic('ratios')">📈 Les ratios</button>
  </div>
  <div class="chat-input-row">
    <input id="chat-input" type="text" placeholder="Posez votre question..." onkeydown="if(event.key==='Enter')sendMsg()">
    <button id="chat-send" onclick="sendMsg()">→</button>
  </div>
</div>

<script>
const REPLIES = {
  charger: "Pour charger vos données :<br><br>1. Cliquez sur <strong>Ouvrir le dashboard</strong><br>2. Si aucune donnée n'est détectée, une zone d'import apparaît<br>3. Glissez-déposez votre fichier <strong>BASE_SENEGAL2.xlsx</strong> ou <strong>banques_clean.csv</strong><br>4. Le dashboard se charge automatiquement.",
  dashboard: "Le dashboard bancaire propose :<br><br>• <strong>Vue d'ensemble</strong> — classement et parts de marché<br>• <strong>Analyse approfondie</strong> — scatter, treemap, carte, scores<br>• <strong>Rapport & Données</strong> — tableau complet et export PDF<br><br>Utilisez la barre latérale gauche pour filtrer par année, banque ou groupe.",
  filtres: "Les filtres se trouvent dans la <strong>barre latérale gauche</strong> du dashboard :<br><br>• <strong>Année</strong> — sélectionner l'exercice (2015–2022)<br>• <strong>Banque(s)</strong> — une ou plusieurs banques<br>• <strong>Groupe</strong> — Locaux, Continentaux, Internationaux…<br>• <strong>Indicateur</strong> — changer la métrique des graphiques<br><br>Ils restent visibles en permanence, même en scrollant.",
  pdf: "Pour générer un rapport PDF :<br><br>1. Dans la sidebar gauche, descendez jusqu'à <strong>Rapport PDF</strong><br>2. Sélectionnez la banque dans la liste déroulante<br>3. Cliquez <strong>↓ Télécharger</strong><br><br>Le PDF contient les indicateurs clés et l'historique complet de la banque.",
  sources: "Les données proviennent de deux sources :<br><br>• <strong>BASE_SENEGAL2.xlsx</strong> — données 2015–2020 collectées auprès des banques<br>• <strong>Rapport BCEAO 2022</strong> — données 2021–2022 extraites du rapport officiel UMOA<br><br>Couverture : <strong>24 banques, 8 ans, 180 observations</strong>.",
  ratios: "Les ratios calculés automatiquement :<br><br>• <strong>ROA</strong> — Résultat net / Bilan × 100<br>• <strong>Coeff. d'exploitation</strong> — Charges / PNB × 100 (norme &lt; 60%)<br>• <strong>Taux de transformation</strong> — Emplois / Ressources × 100<br>• <strong>Solvabilité</strong> — Fonds propres / Bilan × 100<br>• <strong>Score global</strong> — Score composite sur 100 pts",
};

const KEYWORDS = [
  [['charger','upload','fichier','excel','csv','importer','données'], 'charger'],
  [['dashboard','tableau de bord','graphique','chart','visualis'], 'dashboard'],
  [['filtre','filtrer','année','banque','groupe','indicateur'], 'filtres'],
  [['pdf','rapport','télécharger','download'], 'pdf'],
  [['source','bceao','données','base','origine'], 'sources'],
  [['ratio','roa','coefficient','solvabilité','taux','score'], 'ratios'],
];

function toggleChat(){
  const w=document.getElementById('chat-win');
  w.classList.toggle('open');
}

function addMsg(txt, cls){
  const d=document.createElement('div');
  d.className='msg '+cls;
  d.innerHTML=txt;
  const c=document.getElementById('chat-msgs');
  c.appendChild(d);
  c.scrollTop=c.scrollHeight;
}

function askTopic(key){
  const labels={'charger':'Charger des données','dashboard':'Utiliser le dashboard',
    'filtres':'Les filtres','pdf':'Rapport PDF','sources':'Sources','ratios':'Les ratios'};
  addMsg(labels[key],'user');
  setTimeout(()=>addMsg(REPLIES[key],'bot'),300);
  document.getElementById('chat-topics').style.display='none';
}

function sendMsg(){
  const inp=document.getElementById('chat-input');
  const txt=inp.value.trim();
  if(!txt) return;
  addMsg(txt,'user');
  inp.value='';
  document.getElementById('chat-topics').style.display='none';
  const low=txt.toLowerCase();
  let reply="Je n'ai pas trouvé de réponse précise. Essayez un des sujets ci-dessous ou contactez le responsable de la plateforme.";
  for(const [kws,key] of KEYWORDS){
    if(kws.some(k=>low.includes(k))){ reply=REPLIES[key]; break; }
  }
  setTimeout(()=>{
    addMsg(reply,'bot');
    // Remettre les topics si pas de résultat clair
    if(reply.startsWith("Je n'ai pas")){
      document.getElementById('chat-topics').style.display='flex';
    }
  },350);
}

// Back to top visibility
window.addEventListener('scroll',()=>{
  document.getElementById('back-top').classList.toggle('show', window.scrollY > 300);
});
</script>
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
