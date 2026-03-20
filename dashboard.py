
import os
import io
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from pymongo import MongoClient
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors as rl_colors

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

BLUE   = "#2563eb"; GREEN  = "#10b981"; AMBER  = "#f59e0b"
RED    = "#ef4444"; PURPLE = "#8b5cf6"; TEAL   = "#0891b2"
SLATE  = "#64748b"; INK    = "#0f172a"
PALETTE = [BLUE, GREEN, AMBER, RED, PURPLE, TEAL, "#ec4899", "#84cc16", "#f97316"]

CHART_CFG = dict(
    font=dict(family="Inter, system-ui, sans-serif", size=11, color=INK),
    plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
    margin=dict(l=8, r=8, t=28, b=8),
    legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", font_size=10),
)

COORDS = {
    "SGBS":(14.6937,-17.4441),"CBAO":(14.6928,-17.4467),"BICIS":(14.6945,-17.4389),
    "ECOBANK":(14.7167,-17.4677),"BOA":(14.6892,-17.4423),"UBA":(14.7012,-17.4512),
    "ORABANK":(14.7089,-17.4398),"CITIBANK":(14.6956,-17.4356),"BIS":(14.6843,-17.4534),
    "BHS":(14.6901,-17.4478),"BNDE":(14.6987,-17.4289),"CDS":(14.6923,-17.4501),
    "LBA":(14.7134,-17.4623),"BSIC":(14.6867,-17.4412),"BDK":(14.6978,-17.4345),
    "BGFI":(14.7056,-17.4467),"FBNBANK":(14.6912,-17.4523),
}

RENAME_EXCEL = {
    "Sigle":"sigle","Goupe_Bancaire":"groupe","ANNEE":"annee","EMPLOI":"emploi",
    "BILAN":"bilan","RESSOURCES":"ressources","FONDS.PROPRE":"fonds_propres",
    "EFFECTIF":"effectif","AGENCE":"agences","PRODUIT.NET.BANCAIRE":"pnb",
    "RESULTAT.NET":"resultat_net","CHARGES.GENERALES.D'EXPLOITATION":"charges_exploit",
    "RESULTAT.BRUT.D'EXPLOITATION":"rbe","COÛT.DU.RISQUE":"cout_risque",
    "INTERETS.ET.PRODUITS.ASSIMILES":"interets_produits",
    "NTERETS.ET.CHARGES.ASSIMILEES":"interets_charges",
}

GROUPES_MAP = {
    "SGBS":"Internationaux","BICIS":"Internationaux","CITIBANK":"Internationaux",
    "UBA":"Internationaux","FBNBANK":"Internationaux",
    "CBAO":"Continentaux","CDS":"Continentaux","ECOBANK":"Continentaux",
    "ORABANK":"Continentaux","BOA":"Continentaux","BSIC":"Continentaux",
    "BIMAO":"Continentaux","BA-S":"Continentaux","BAS":"Continentaux",
    "NSIA":"Continentaux","BGFI":"Continentaux",
    "BHS":"Locaux","LBA":"Locaux","BIS":"Locaux","BRM":"Locaux",
    "BNDE":"Locaux","BDK":"Locaux","LBO":"Locaux","BCIM":"Locaux","CISA":"Locaux","CI":"Locaux",
    "CBI":"Régionaux",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*{box-sizing:border-box;}
html,body{font-family:'Inter',system-ui,sans-serif!important;background:#f1f5f9!important;margin:0;}
.dash-nav{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 55%,#2563eb 100%);padding:0 32px;height:58px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:1000;}
.nav-back{color:rgba(255,255,255,.65);font-size:13px;font-weight:600;text-decoration:none;transition:color .2s;}
.nav-back:hover{color:#fff;}
.nav-center{display:flex;align-items:center;gap:10px;}
.nav-logo-box{width:34px;height:34px;border-radius:9px;background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;font-size:17px;}
.nav-title{font-size:15px;font-weight:800;color:#fff;letter-spacing:-.3px;}
.nav-right{display:flex;align-items:center;gap:8px;}
.status-badge{font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.2);color:rgba(255,255,255,.7);}
.status-ok{color:#34d399!important;border-color:rgba(52,211,153,.4)!important;background:rgba(52,211,153,.1)!important;}
.status-err{color:#fca5a5!important;border-color:rgba(252,165,165,.4)!important;background:rgba(252,165,165,.1)!important;}
.filter-bar{background:#fff;border-bottom:1px solid #e2e8f0;padding:10px 32px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;box-shadow:0 1px 4px rgba(0,0,0,.05);}
.fg{display:flex;align-items:center;gap:8px;}
.fg label{font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;white-space:nowrap;}
.kpi-strip{display:grid;grid-template-columns:repeat(4,1fr);background:#e2e8f0;border-bottom:1px solid #e2e8f0;}
.kpi-cell{background:#fff;padding:18px 24px;position:relative;overflow:hidden;}
.kpi-cell+.kpi-cell{border-left:1px solid #e2e8f0;}
.kpi-cell::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;}
.kc-blue::after{background:linear-gradient(90deg,#2563eb,#7c3aed);}
.kc-green::after{background:linear-gradient(90deg,#10b981,#0ea5e9);}
.kc-amber::after{background:linear-gradient(90deg,#f59e0b,#f97316);}
.kc-purple::after{background:linear-gradient(90deg,#8b5cf6,#ec4899);}
.kpi-top2{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}
.kpi-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;color:#94a3b8;}
.kpi-ico{font-size:20px;} .kpi-num{font-size:26px;font-weight:900;color:#0f172a;letter-spacing:-1.5px;line-height:1;margin-bottom:6px;}
.kpi-dt{font-size:11px;font-weight:600;} .dt-up{color:#10b981;} .dt-dn{color:#ef4444;} .dt-na{color:#94a3b8;}
.insights-row{display:flex;gap:12px;overflow-x:auto;padding:14px 32px;background:#f8fafc;border-bottom:1px solid #e2e8f0;}
.insights-row::-webkit-scrollbar{height:3px;}
.insights-row::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:2px;}
.ipill{flex-shrink:0;display:flex;align-items:center;gap:12px;background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:11px 16px;min-width:190px;transition:box-shadow .2s;}
.ipill:hover{box-shadow:0 4px 16px rgba(0,0,0,.08);}
.ipill.ok{border-left:3px solid #10b981;} .ipill.warn{border-left:3px solid #f59e0b;}
.ipill.bad{border-left:3px solid #ef4444;} .ipill.info{border-left:3px solid #2563eb;}
.ip-ico{font-size:24px;} .ip-lbl{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#94a3b8;}
.ip-val{font-size:16px;font-weight:800;color:#0f172a;line-height:1.1;} .ip-desc{font-size:10px;color:#64748b;margin-top:1px;}
.pad{padding:20px 32px;}
.ch{background:#fff;border:1px solid #e2e8f0;border-radius:16px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04);}
.ch-h{padding:13px 18px 9px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between;}
.ch-t{font-size:13px;font-weight:700;color:#0f172a;} .ch-b{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;padding:3px 10px;border-radius:20px;}
.bb{background:#eff6ff;color:#2563eb;} .bg{background:#ecfdf5;color:#10b981;} .bp{background:#f5f3ff;color:#8b5cf6;} .ba{background:#fef3c7;color:#d97706;} .bt{background:#ecfeff;color:#0891b2;}
.ch-bd{padding:6px;}
.r2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;}
.r3a{display:grid;grid-template-columns:5fr 4fr;gap:16px;margin-bottom:16px;}
.mb{margin-bottom:16px;} .tw{overflow-x:auto;} .pdf-r{display:flex;align-items:center;gap:12px;padding:14px 18px;flex-wrap:wrap;}
.upload-section{display:flex;align-items:center;justify-content:center;min-height:calc(100vh - 58px);padding:40px;}
.upload-card{background:#fff;border:1px solid #e2e8f0;border-radius:20px;padding:48px;max-width:580px;width:100%;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,.06);}
.upload-card h2{font-size:22px;font-weight:800;color:#0f172a;margin-bottom:8px;letter-spacing:-.5px;}
.upload-card p{font-size:14px;color:#64748b;margin-bottom:28px;line-height:1.7;}
.upload-zone{border:2px dashed #cbd5e1;border-radius:14px;padding:36px 24px;cursor:pointer;transition:border-color .2s,background .2s;margin-bottom:16px;}
.upload-zone:hover{border-color:#2563eb;background:#eff6ff;}
.u-ico{font-size:38px;margin-bottom:10px;} .u-title{font-size:15px;font-weight:700;color:#0f172a;margin-bottom:4px;} .u-sub{font-size:12px;color:#94a3b8;}
.upload-formats{display:flex;gap:8px;justify-content:center;margin-bottom:16px;}
.fmt-pill{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:6px 14px;font-size:12px;font-weight:700;color:#475569;}
.fmt-pill.active{background:#eff6ff;border-color:#bfdbfe;color:#2563eb;}
.upload-info{background:#f8fafc;border-radius:10px;padding:12px 16px;text-align:left;}
.upload-info p{font-size:11px;color:#64748b;margin:0;line-height:1.7;}
.ul-ok{font-size:12px;color:#10b981;font-weight:600;margin-top:10px;padding:8px 12px;background:#ecfdf5;border-radius:8px;}
.ul-err{font-size:12px;color:#ef4444;font-weight:600;margin-top:10px;padding:8px 12px;background:#fef2f2;border-radius:8px;}
.changer-btn{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;color:#64748b;cursor:pointer;padding:6px 12px;border-radius:8px;border:1px solid #e2e8f0;background:#fff;transition:border-color .2s;}
.changer-btn:hover{border-color:#2563eb;color:#2563eb;}
@media(max-width:900px){.kpi-strip{grid-template-columns:repeat(2,1fr);}.r2,.r3a{grid-template-columns:1fr;}.pad{padding:16px;}.filter-bar,.insights-row{padding:12px 16px;}.upload-section{padding:20px;}}
"""


def charger_donnees():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.server_info()
        docs = list(client["banques_senegal"]["indicateurs"].find({}, {"_id": 0}))
        if docs:
            return pd.DataFrame(docs)
    except Exception:
        pass
    for path in ["data/banques_clean.csv", "banques_clean.csv"]:
        if os.path.exists(path):
            try:
                return pd.read_csv(path)
            except Exception:
                pass
    return pd.DataFrame()


def calculer_ratios(df):
    if "resultat_net" in df.columns and "bilan" in df.columns:
        df["roa"] = (df["resultat_net"] / df["bilan"] * 100).round(2)
        df.loc[df["roa"].abs() > 100, "roa"] = None
    if "charges_exploit" in df.columns and "pnb" in df.columns:
        df["coeff_exploit"] = (df["charges_exploit"] / df["pnb"] * 100).round(2)
        df.loc[df["coeff_exploit"].abs() > 500, "coeff_exploit"] = None
    if "emploi" in df.columns and "ressources" in df.columns:
        df["taux_transfo"] = (df["emploi"] / df["ressources"] * 100).round(2)
        df.loc[(df["taux_transfo"] <= 0) | (df["taux_transfo"] > 300), "taux_transfo"] = None
    if "fonds_propres" in df.columns and "bilan" in df.columns:
        df["solvabilite"] = (df["fonds_propres"] / df["bilan"] * 100).round(2)
    if "ressources" in df.columns and "bilan" in df.columns:
        df["liquidite"] = (df["ressources"] / df["bilan"] * 100).round(2)
        df.loc[(df["liquidite"] <= 0) | (df["liquidite"] > 200), "liquidite"] = None
    return df


def calculer_score(df):
    criteres = [c for c in ["bilan", "pnb", "roa", "solvabilite"] if c in df.columns]
    if not criteres or "sigle" not in df.columns:
        return df
    synthese = df.groupby("sigle")[criteres].mean()
    for col in criteres:
        mn, mx = synthese[col].min(), synthese[col].max()
        synthese[f"{col}_s"] = ((synthese[col] - mn) / (mx - mn) * 100).round(1) if mx > mn else 50.0
    synthese["score_global"] = synthese[[f"{c}_s" for c in criteres]].mean(axis=1).round(1)
    df = df.merge(synthese[["score_global"]].reset_index(), on="sigle", how="left", suffixes=("_old", ""))
    if "score_global_old" in df.columns:
        df.drop(columns=["score_global_old"], inplace=True)
    return df


def traiter_excel(df):
    df = df.rename(columns={k: v for k, v in RENAME_EXCEL.items() if k in df.columns})
    if "sigle" in df.columns:
        df["sigle"] = df["sigle"].astype(str).str.strip().str.upper()
    num_cols = ["bilan","emploi","ressources","fonds_propres","pnb","resultat_net",
                "charges_exploit","rbe","cout_risque","effectif","agences"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["sigle", "annee"])
    if "groupe" not in df.columns or df["groupe"].isna().all():
        df["groupe"] = df["sigle"].map(GROUPES_MAP).fillna("Autres")
    else:
        df["groupe"] = df["groupe"].fillna(df["sigle"].map(GROUPES_MAP)).fillna("Autres")
    df = calculer_ratios(df)
    df = calculer_score(df)
    return df


def parse_upload(contents, filename=""):
    try:
        _, cs = contents.split(",", 1)
        decoded = base64.b64decode(cs)
        fname = filename.lower()
        if fname.endswith(".xlsx") or fname.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(decoded))
            df = traiter_excel(df)
        else:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        return df
    except Exception:
        return pd.DataFrame()


def generer_rapport_pdf(banque, data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    c = [Paragraph(f"Rapport — {banque}", styles["Title"]), Spacer(1, 8),
         Paragraph("SenBank Analytics · BCEAO / BASE_SENEGAL2", styles["Normal"]), Spacer(1, 12)]
    df_b = data[data["sigle"] == banque].sort_values("annee")
    if df_b.empty:
        c.append(Paragraph("Aucune donnée disponible.", styles["Normal"]))
    else:
        latest = df_b.iloc[-1]
        c.append(Paragraph(f"<b>Dernière année : {int(latest.get('annee', 0))}</b>", styles["Normal"]))
        c.append(Spacer(1, 8))
        for k, lbl in [("bilan","Bilan"),("pnb","PNB"),("resultat_net","Résultat net"),
                        ("roa","ROA (%)"),("solvabilite","Solvabilité (%)"),("score_global","Score")]:
            if k in latest and pd.notna(latest[k]):
                c.append(Paragraph(f"<b>{lbl} :</b> {latest[k]:,.2f}", styles["Normal"]))
        c.append(Spacer(1, 12))
        cols = ["annee","bilan","pnb","resultat_net","roa","coeff_exploit","solvabilite","score_global"]
        cd = [x for x in cols if x in df_b.columns]
        rows = [cd] + [[str(round(v,2) if isinstance(v,float) else v) for v in row]
                       for row in df_b[cd].fillna("—").values.tolist()]
        t = Table(rows)
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),rl_colors.HexColor("#2563eb")),
            ("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("GRID",(0,0),(-1,-1),0.4,rl_colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.white,rl_colors.HexColor("#f8fafc")]),
        ]))
        c.append(t)
    doc.build(c)
    buf.seek(0)
    return buf


def get_df(data):
    return pd.DataFrame(data) if data else pd.DataFrame()

def ao(d): return [{"label":str(a),"value":a} for a in sorted(d["annee"].dropna().unique().astype(int).tolist())] if not d.empty else []
def bo(d): return [{"label":b,"value":b} for b in sorted(d["sigle"].unique())] if not d.empty else []
def go_(d): return ([{"label":"Tous","value":"Tous"}]+[{"label":g,"value":g} for g in sorted(d["groupe"].unique())]) if "groupe" in d.columns else [{"label":"Tous","value":"Tous"}]


def creer_dashboard(server):
    app = Dash(__name__, server=server, url_base_pathname="/bancaire/",
               external_stylesheets=[dbc.themes.FLATLY])

    app.index_string = f"""<!DOCTYPE html>
<html lang="fr"><head>{{%metas%}}<title>Banking Intelligence — BCEAO Sénégal</title>
{{%favicon%}}{{%css%}}<style>{CSS}</style></head>
<body>{{%app_entry%}}<footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer></body></html>"""

    def ef(msg="Aucune donnée"):
        f = go.Figure()
        f.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5,
                         showarrow=False, font=dict(size=13, color="#94a3b8"))
        f.update_layout(**CHART_CFG, height=280)
        return f

    def ch(title, badge, bcls, gid, h=300):
        return html.Div([
            html.Div([html.Span(title,className="ch-t"), html.Span(badge,className=f"ch-b {bcls}")],className="ch-h"),
            html.Div(dcc.Graph(id=gid, config={"displayModeBar":False}, style={"height":f"{h}px"}),className="ch-bd"),
        ], className="ch")

    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="store", storage_type="session"),
        dcc.Download(id="dl-pdf"),

        # NAV
        html.Div([
            html.A("← Accueil", href="/", className="nav-back"),
            html.Div([html.Div("🏦",className="nav-logo-box"),
                      html.Span("Banking Intelligence — Sénégal",className="nav-title")],className="nav-center"),
            html.Div([
                html.Img(src="https://flagcdn.com/w32/sn.png",style={"height":"20px","borderRadius":"3px"}),
                html.Span(id="status", children="⟳", className="status-badge"),
            ], className="nav-right"),
        ], className="dash-nav"),

        # UPLOAD SECTION (visible quand pas de données)
        html.Div(id="upload-section", children=[
            html.Div([
                html.H2("Charger les données"),
                html.P([
                    "Importez votre fichier de données pour afficher le dashboard.",
                    html.Br(),
                    "Formats acceptés : ", html.Strong("Excel (.xlsx)"), " et ", html.Strong("CSV (.csv)"), "."
                ]),
                html.Div([
                    html.Span("📊 .xlsx", className="fmt-pill active"),
                    html.Span("📄 .csv", className="fmt-pill active"),
                ], className="upload-formats"),
                dcc.Upload(
                    id="ul",
                    children=html.Div([
                        html.Div("📂", className="u-ico"),
                        html.Div("Glisser-déposer ici ou cliquer pour parcourir", className="u-title"),
                        html.Div("BASE_SENEGAL2.xlsx  ou  banques_clean.csv", className="u-sub"),
                    ]),
                    accept=".csv,.xlsx,.xls",
                    className="upload-zone",
                    multiple=False,
                ),
                html.Div(id="ul-msg"),
                html.Div([
                    html.P([
                        html.Strong("Pour BASE_SENEGAL2.xlsx :"),
                        " le fichier sera traité automatiquement (renommage colonnes, calcul ratios, score).",
                        html.Br(),
                        html.Strong("Pour banques_clean.csv :"),
                        " données déjà nettoyées chargées directement.",
                    ])
                ], className="upload-info"),
            ], className="upload-card"),
        ], className="upload-section"),

        # DASHBOARD SECTION
        html.Div(id="dashboard-section", style={"display":"none"}, children=[

            # FILTER BAR
            html.Div([
                html.Div([html.Label("Année"),
                          dcc.Dropdown(id="f-an",options=[],value=None,clearable=False,style={"minWidth":"95px"})],className="fg"),
                html.Div([html.Label("Banque(s)"),
                          dcc.Dropdown(id="f-bq",options=[],value=None,multi=True,style={"minWidth":"260px"})],className="fg"),
                html.Div([html.Label("Groupe"),
                          dcc.Dropdown(id="f-gr",options=[],value="Tous",clearable=False,style={"minWidth":"130px"})],className="fg"),
                html.Div([html.Label("Indicateur"),
                          dcc.Dropdown(id="f-ind",
                                       options=[{"label":"Bilan","value":"bilan"},{"label":"PNB","value":"pnb"},
                                                {"label":"Emploi","value":"emploi"},{"label":"Ressources","value":"ressources"},
                                                {"label":"Fonds propres","value":"fonds_propres"},{"label":"Résultat net","value":"resultat_net"},
                                                {"label":"ROA","value":"roa"},{"label":"Solvabilité","value":"solvabilite"},
                                                {"label":"Coeff. exploit.","value":"coeff_exploit"},{"label":"Taux transfo.","value":"taux_transfo"},
                                                {"label":"Liquidité","value":"liquidite"}],
                                       value="bilan",clearable=False,style={"minWidth":"155px"})],className="fg"),
                html.Div([
                    dcc.Upload(id="ul-bar", accept=".csv,.xlsx,.xls", multiple=False,
                               children=html.Span("📂 Changer les données", className="changer-btn")),
                    html.Div(id="ul-bar-msg", style={"fontSize":"11px","color":GREEN}),
                ], style={"marginLeft":"auto","display":"flex","alignItems":"center","gap":"8px"}),
            ], className="filter-bar"),

            html.Div(id="kpi-strip", className="kpi-strip"),
            html.Div(id="insights-row", className="insights-row"),

            html.Div([
                html.Div([
                    ch("Classement des banques","RANKING","bb","g-rank",320),
                    ch("Répartition par groupe","MARKET SHARE","bp","g-pie",320),
                ], className="r3a"),
                html.Div([
                    ch("Évolution dans le temps","TREND ANALYSIS","bt","g-evol",300),
                    ch("Distribution du ROA par groupe","RISK PROFILING","ba","g-box",300),
                ], className="r3a"),
                html.Div([
                    ch("ROA vs Coeff. d'exploitation","SCATTER ANALYSIS","bb","g-scat",310),
                    ch("Répartition hiérarchique du bilan","TREEMAP","bg","g-tree",310),
                ], className="r2"),
                html.Div([ch("Carte des établissements — Grand Dakar","GÉOGRAPHIE","bt","g-map",390)],className="mb"),
                html.Div([
                    html.Div([
                        html.Div([html.Span("Score de positionnement global",className="ch-t"),
                                  html.Span("COMPETITIVE INTELLIGENCE",className="ch-b bp")],className="ch-h"),
                        html.Div(dcc.Graph(id="g-score",config={"displayModeBar":False}),className="ch-bd"),
                    ], className="ch"),
                ], className="mb"),
                html.Div([
                    html.Div([html.Span("Tableau des indicateurs",className="ch-t"),
                              html.Span("DATA TABLE",className="ch-b bb")],className="ch-h"),
                    html.Div(id="tableau",className="tw"),
                ], className="ch mb"),
                html.Div([
                    html.Div([html.Span("📄 Rapport PDF par banque",className="ch-t")],className="ch-h"),
                    html.Div([
                        dcc.Dropdown(id="bq-pdf",options=[],value=None,clearable=False,
                                     style={"minWidth":"200px","flex":"1"}),
                        dbc.Button("↓ Télécharger",id="btn-pdf",color="primary",
                                   style={"fontWeight":"700","borderRadius":"8px","flexShrink":"0"}),
                        html.Div(id="msg-pdf"),
                    ], className="pdf-r"),
                ], className="ch mb"),
            ], className="pad"),
        ]),
    ])

    # ── CALLBACKS ──────────────────────────────────────

    def filt(data, annee, banques, groupe):
        d = get_df(data)
        if d.empty: return pd.DataFrame(), pd.DataFrame()
        if groupe and groupe != "Tous" and "groupe" in d.columns:
            d = d[d["groupe"] == groupe]
        if banques:
            d = d[d["sigle"].isin(banques)]
        da = d[d["annee"] == annee] if annee and not d.empty else d
        return d, da

    # LOAD DATA
    @app.callback(
        Output("store","data"),
        Output("status","children"), Output("status","className"),
        Output("ul-msg","children"), Output("ul-bar-msg","children"),
        Input("url","pathname"),
        Input("ul","contents"), Input("ul-bar","contents"),
        State("ul","filename"), State("ul-bar","filename"),
        State("store","data"),
    )
    def load_data(_, ul_c, ulb_c, ul_f, ulb_f, existing):
        d = charger_donnees()
        ul_msg = ""; bar_msg = ""

        if d.empty and (ul_c or ulb_c):
            contents = ul_c or ulb_c
            fname = ul_f or ulb_f or ""
            d = parse_upload(contents, fname)
            if not d.empty:
                ul_msg = html.Div(f"✓ {fname} chargé — {len(d)} lignes", className="ul-ok")
                bar_msg = f"✓ {fname}"
            else:
                ul_msg = html.Div("✗ Format non reconnu. Vérifiez le fichier.", className="ul-err")
        elif ul_c or ulb_c:
            contents = ul_c or ulb_c
            fname = ul_f or ulb_f or ""
            d2 = parse_upload(contents, fname)
            if not d2.empty:
                d = d2
                bar_msg = f"✓ {fname}"
                ul_msg = html.Div(f"✓ {fname} — {len(d)} lignes", className="ul-ok")

        if not d.empty:
            st, cls = f"✓ {len(d)} obs · {d['sigle'].nunique()} banques", "status-badge status-ok"
            return d.to_dict("records"), st, cls, ul_msg, bar_msg
        return (existing or []), "⚠ Aucune donnée", "status-badge status-err", ul_msg, bar_msg

    # TOGGLE SECTIONS
    @app.callback(
        Output("upload-section","style"), Output("dashboard-section","style"),
        Input("store","data"),
    )
    def toggle(data):
        if data:
            return {"display":"none"}, {"display":"block"}
        return {"display":"flex","alignItems":"center","justifyContent":"center",
                "minHeight":"calc(100vh - 58px)","padding":"40px"}, {"display":"none"}

    # INIT DROPDOWNS
    @app.callback(
        Output("f-an","options"), Output("f-an","value"),
        Output("f-bq","options"), Output("f-bq","value"),
        Output("f-gr","options"),
        Output("bq-pdf","options"), Output("bq-pdf","value"),
        Input("store","data"),
    )
    def init_dd(data):
        d = get_df(data)
        a = ao(d); b = bo(d); g = go_(d)
        bdef = [x["value"] for x in b[:6]] if len(b)>=6 else [x["value"] for x in b]
        adef = a[-1]["value"] if a else None
        return a, adef, b, bdef, g, b, b[0]["value"] if b else None

    # KPI STRIP
    @app.callback(Output("kpi-strip","children"),
                  Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),State("store","data"))
    def upd_kpi(annee, banques, groupe, data):
        _, da = filt(data, annee, banques, groupe)
        prev = (annee-1) if annee else None
        _, dp = filt(data, prev, banques, groupe)
        pct_cols = ("roa","solvabilite","coeff_exploit","liquidite","taux_transfo")
        def cell(lbl, col, ico, cls, is_sum=True):
            v = None
            if not da.empty and col in da.columns and not da[col].isna().all():
                v = da[col].sum() if is_sum else da[col].mean()
            vstr = "N/A" if v is None else (f"{v:.1f}%" if col in pct_cols else f"{v:,.0f}")
            delta = html.Span("— vs n-1", className="kpi-dt dt-na")
            if v is not None and not dp.empty and col in dp.columns:
                vp = dp[col].sum() if is_sum else dp[col].mean()
                if pd.notna(vp) and vp != 0:
                    pct = (v-vp)/abs(vp)*100
                    delta = html.Span(f"{'▲' if pct>0 else '▼'} {abs(pct):.1f}% vs {prev}",
                                      className=f"kpi-dt {'dt-up' if pct>0 else 'dt-dn'}")
            return html.Div([
                html.Div([html.Div(lbl,className="kpi-lbl"),html.Div(ico,className="kpi-ico")],className="kpi-top2"),
                html.Div(vstr,className="kpi-num"), delta,
            ], className=f"kpi-cell {cls}")
        return [
            cell("Bilan total (MFCFA)","bilan","🏦","kc-blue"),
            cell("PNB moyen (MFCFA)","pnb","💰","kc-green",is_sum=False),
            cell("Résultat net total","resultat_net","📈","kc-amber"),
            cell("ROA moyen (%)","roa","🎯","kc-purple",is_sum=False),
        ]

    # INSIGHTS
    @app.callback(Output("insights-row","children"),
                  Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),State("store","data"))
    def upd_ins(annee, banques, groupe, data):
        _, da = filt(data, annee, banques, groupe)
        if da.empty:
            return html.Div("Aucune donnée.", style={"color":SLATE,"fontSize":"13px"})
        def pill(ico, lbl, val, desc, cls):
            return html.Div([html.Div(ico,className="ip-ico"),
                             html.Div([html.Div(lbl,className="ip-lbl"),html.Div(val,className="ip-val"),
                                       html.Div(desc,className="ip-desc")])],className=f"ipill {cls}")
        pills = []
        if "roa" in da.columns:
            best = da.dropna(subset=["roa"]).nlargest(1,"roa")
            if not best.empty: pills.append(pill("⭐","MEILLEUR ROA",best.iloc[0]["sigle"],f"{best.iloc[0]['roa']:.2f}%","ok"))
        if "resultat_net" in da.columns:
            n_pos=(da["resultat_net"]>0).sum(); n_tot=da["resultat_net"].notna().sum()
            if n_tot>0:
                pct=n_pos/n_tot*100
                pills.append(pill("💹","BANQUES RENTABLES",f"{n_pos}/{int(n_tot)}",f"{pct:.0f}% positif",
                                  "ok" if pct>=70 else("warn" if pct>=40 else "bad")))
        if "solvabilite" in da.columns:
            avg=da["solvabilite"].mean()
            if pd.notna(avg): pills.append(pill("🛡️","SOLVABILITÉ MOY.",f"{avg:.1f}%",f"Norme ≥8% {'✓' if avg>=8 else '⚠'}","ok" if avg>=8 else "bad"))
        if "score_global" in da.columns:
            top=da.dropna(subset=["score_global"]).nlargest(1,"score_global")
            if not top.empty: pills.append(pill("🏆","LEADER",top.iloc[0]["sigle"],f"Score {top.iloc[0]['score_global']:.0f}/100","info"))
        if "taux_transfo" in da.columns:
            avg_t=da["taux_transfo"].mean()
            if pd.notna(avg_t): pills.append(pill("🔄","TAUX TRANSFO.",f"{avg_t:.1f}%","Emplois/ressources","ok" if 60<=avg_t<=110 else "warn"))
        if "bilan" in da.columns:
            total=da["bilan"].sum()
            if pd.notna(total): pills.append(pill("📊","ACTIF AGRÉGÉ",f"{total/1000:.1f}B","MFCFA total secteur","info"))
        return pills

    @app.callback(Output("g-rank","figure"),Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),Input("f-ind","value"),State("store","data"))
    def g_rank(an,bq,gr,ind,data):
        _,da=filt(data,an,bq,gr)
        if da.empty or ind not in da.columns: return ef()
        da=da.dropna(subset=[ind]).sort_values(ind)
        fig=px.bar(da,x=ind,y="sigle",orientation="h",color="groupe" if "groupe" in da.columns else None,color_discrete_sequence=PALETTE,labels={ind:ind.upper(),"sigle":""})
        fig.update_traces(marker_line_width=0); fig.update_layout(**CHART_CFG,height=320); return fig

    @app.callback(Output("g-evol","figure"),Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),Input("f-ind","value"),State("store","data"))
    def g_evol(an,bq,gr,ind,data):
        d,_=filt(data,an,bq,gr)
        if d.empty or ind not in d.columns: return ef()
        d=d.dropna(subset=[ind,"annee"]).sort_values("annee")
        fig=px.line(d,x="annee",y=ind,color="sigle",markers=True,color_discrete_sequence=PALETTE,labels={ind:ind.upper(),"annee":"Année"})
        fig.update_traces(line_width=2.5,marker_size=5); fig.update_layout(**CHART_CFG,height=300); return fig

    @app.callback(Output("g-scat","figure"),Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),State("store","data"))
    def g_scat(an,bq,gr,data):
        _,da=filt(data,an,bq,gr)
        if da.empty or "roa" not in da.columns or "coeff_exploit" not in da.columns: return ef()
        da=da.dropna(subset=["roa","coeff_exploit"]); da=da[(da["coeff_exploit"]>0)&(da["coeff_exploit"]<300)]
        if da.empty: return ef()
        fig=px.scatter(da,x="coeff_exploit",y="roa",text="sigle",color="groupe" if "groupe" in da.columns else None,
                       size="bilan" if "bilan" in da.columns else None,color_discrete_sequence=PALETTE,
                       labels={"coeff_exploit":"Coeff. exploit. (%)","roa":"ROA (%)"},hover_data={"sigle":True,"bilan":True})
        ymax=da["roa"].max()+1
        fig.add_shape(type="rect",x0=0,x1=60,y0=0,y1=ymax,fillcolor="rgba(16,185,129,.06)",line_width=0)
        fig.add_vline(x=60,line_dash="dash",line_color=AMBER,annotation_text="Norme 60%",annotation_font_size=10)
        fig.add_hline(y=0,line_dash="dot",line_color=RED)
        fig.add_annotation(x=15,y=ymax*.85,text="⭐ Zone performante",showarrow=False,font=dict(size=10,color=GREEN))
        fig.update_traces(textposition="top center",textfont_size=9); fig.update_layout(**CHART_CFG,height=310); return fig

    @app.callback(Output("g-pie","figure"),Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),State("store","data"))
    def g_pie(an,bq,gr,data):
        _,da=filt(data,an,bq,gr)
        if da.empty or "groupe" not in da.columns or "bilan" not in da.columns: return ef()
        grp=da.groupby("groupe")["bilan"].sum().reset_index().sort_values("bilan",ascending=False)
        total=grp["bilan"].sum()
        fig=go.Figure(go.Pie(labels=grp["groupe"],values=grp["bilan"],hole=0.54,marker_colors=PALETTE[:len(grp)],textinfo="label+percent",textfont_size=11))
        fig.add_annotation(text=f"<b>{total/1000:.0f}B</b><br>MFCFA",x=0.5,y=0.5,showarrow=False,font=dict(size=13,color=INK))
        fig.update_layout(**CHART_CFG,height=320,legend=dict(orientation="v",x=1.0,y=0.5,font_size=11)); return fig

    @app.callback(Output("g-tree","figure"),Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),State("store","data"))
    def g_tree(an,bq,gr,data):
        _,da=filt(data,an,bq,gr)
        if da.empty or "bilan" not in da.columns or "groupe" not in da.columns: return ef()
        da=da.dropna(subset=["bilan"]).copy(); da["bilan"]=da["bilan"].clip(lower=1)
        fig=px.treemap(da,path=["groupe","sigle"],values="bilan",color="bilan",
                       color_continuous_scale=[[0,"#eff6ff"],[0.5,"#93c5fd"],[1,BLUE]],
                       hover_data={"pnb":True,"roa":True} if "pnb" in da.columns else {})
        fig.update_traces(textinfo="label+value+percent parent",textfont=dict(size=11))
        fig.update_layout(**CHART_CFG,coloraxis_showscale=False,height=310); return fig

    @app.callback(Output("g-box","figure"),Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),State("store","data"))
    def g_box(an,bq,gr,data):
        d,_=filt(data,an,bq,gr)
        if d.empty or "roa" not in d.columns or "groupe" not in d.columns: return ef()
        d=d.dropna(subset=["roa"])
        fig=px.box(d,x="groupe",y="roa",color="groupe",color_discrete_sequence=PALETTE,points="all",
                   labels={"roa":"ROA (%)","groupe":""},hover_data=["sigle","annee"])
        fig.add_hline(y=0,line_dash="dot",line_color=RED,annotation_text="0%",annotation_font_size=10)
        fig.update_layout(**CHART_CFG,height=300,showlegend=False); return fig

    @app.callback(Output("g-map","figure"),Input("f-an","value"),State("store","data"))
    def g_map(an,data):
        d=get_df(data); da=d[d["annee"]==an] if an and not d.empty else d
        rows=[]
        for s,(lat,lon) in COORDS.items():
            row=da[da["sigle"]==s]
            bilan=float(row["bilan"].values[0]) if not row.empty and "bilan" in row.columns and pd.notna(row["bilan"].values[0]) else 0
            pnb=float(row["pnb"].values[0]) if not row.empty and "pnb" in row.columns and pd.notna(row["pnb"].values[0]) else 0
            score=float(row["score_global"].values[0]) if not row.empty and "score_global" in row.columns and pd.notna(row["score_global"].values[0]) else 0
            rows.append({"sigle":s,"lat":lat,"lon":lon,"bilan":bilan,"pnb":pnb,"score":score})
        dfc=pd.DataFrame(rows)
        fig=px.scatter_mapbox(dfc,lat="lat",lon="lon",text="sigle",size="bilan",color="score",
                              color_continuous_scale=[[0,"#fef3c7"],[0.5,"#93c5fd"],[1,BLUE]],
                              size_max=35,zoom=11,center={"lat":14.6928,"lon":-17.4467},
                              mapbox_style="open-street-map",
                              hover_data={"bilan":True,"pnb":True,"score":True,"lat":False,"lon":False})
        fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),coloraxis_colorbar=dict(title="Score",thickness=12,len=0.6)); return fig

    @app.callback(Output("g-score","figure"),Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),State("store","data"))
    def g_score(an,bq,gr,data):
        _,da=filt(data,an,bq,gr)
        if da.empty or "score_global" not in da.columns: return ef()
        da=da.dropna(subset=["score_global"]).sort_values("score_global",ascending=True)
        if da.empty: return ef()
        med=da["score_global"].median()
        fig=go.Figure(go.Bar(x=da["score_global"],y=da["sigle"],orientation="h",
                             marker_color=[GREEN if v>=med else AMBER for v in da["score_global"]],
                             text=da["score_global"].round(1),textposition="outside",
                             hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}/100<extra></extra>"))
        fig.add_vline(x=med,line_dash="dot",line_color=SLATE,annotation_text=f"Médiane {med:.0f}",annotation_font_size=10)
        fig.update_layout(**CHART_CFG,xaxis_range=[0,115],height=max(260,len(da)*30),showlegend=False); return fig

    @app.callback(Output("dl-pdf","data"),Output("msg-pdf","children"),
                  Input("btn-pdf","n_clicks"),Input("bq-pdf","value"),State("store","data"),prevent_initial_call=True)
    def dl_pdf(n,banque,data):
        if not n or not banque: return None,""
        buf=generer_rapport_pdf(banque,get_df(data))
        msg=dbc.Alert(f"✓ {banque} — PDF prêt",color="success",duration=3000,
                      style={"fontSize":"12px","padding":"6px 12px","borderRadius":"8px","margin":"0"})
        return dcc.send_bytes(buf.read(),filename=f"rapport_{banque}.pdf"),msg

    @app.callback(Output("tableau","children"),
                  Input("f-an","value"),Input("f-bq","value"),Input("f-gr","value"),State("store","data"))
    def upd_table(an,bq,gr,data):
        _,da=filt(data,an,bq,gr)
        if da.empty:
            return html.Div([html.Div("😕",style={"fontSize":"40px","marginBottom":"8px"}),html.P("Aucune donnée")],
                            style={"textAlign":"center","padding":"40px","color":"#94a3b8"})
        cols=[c for c in ["sigle","groupe","annee","bilan","emploi","ressources","fonds_propres","pnb",
                          "resultat_net","roa","solvabilite","coeff_exploit","taux_transfo","score_global"] if c in da.columns]
        tab=da[cols].sort_values("score_global" if "score_global" in cols else "bilan",ascending=False,na_position="last").round(2)
        return dash_table.DataTable(
            data=tab.to_dict("records"),
            columns=[{"name":c.replace("_"," ").upper(),"id":c} for c in tab.columns],
            style_table={"overflowX":"auto"},
            style_cell={"textAlign":"left","fontSize":"12px","padding":"9px 14px",
                        "fontFamily":"Inter,system-ui,sans-serif","border":"none","borderBottom":"1px solid #f1f5f9","color":INK},
            style_header={"backgroundColor":"#f8fafc","color":SLATE,"fontWeight":"700","fontSize":"10px",
                          "textTransform":"uppercase","letterSpacing":"0.8px","border":"none","borderBottom":"2px solid #e2e8f0"},
            style_data_conditional=[
                {"if":{"filter_query":"{resultat_net} < 0","column_id":"resultat_net"},"color":RED,"fontWeight":"700"},
                {"if":{"filter_query":"{roa} > 1.5","column_id":"roa"},"color":GREEN,"fontWeight":"700"},
                {"if":{"row_index":"odd"},"backgroundColor":"#fafafa"},
            ],
            page_size=15,sort_action="native",filter_action="native",
        )

    return app
