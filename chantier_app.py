import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date, datetime, timedelta

# --- 1. CONFIGURATION INITIALE ---
st.set_page_config(page_title="EGY RENOVATION - Master", layout="wide", page_icon="🏗️")

# --- 2. GESTION DES DOSSIERS & STRUCTURES ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Définition stricte des colonnes pour éviter les erreurs KeyError sur GitHub/Cloud
COLUMNS = {
    "chantiers": ["ID", "Nom du chantier", "Client", "État", "Équipe", "Date Début", "Date Fin", "Prix Devis TTC", "Lots", "Commentaires Techniques"],
    "clients": ["Nom", "Email", "Téléphone", "Adresse"],
    "stocks": ["Référence", "Libellé", "Catégorie", "Quantité", "Unité", "Prix Achat", "Seuil Alerte"],
    "mouvements": ["Date", "Référence", "Libellé", "Quantité", "Type", "Chantier"],
    "materiaux": ["ID Chantier", "Nom Chantier", "Référence", "Désignation", "Quantité", "Unité", "Source", "Statut"]
}

FILES = {k: os.path.join(DATA_DIR, f"{k}_master.csv") for k in COLUMNS.keys()}

# --- 3. OPTIONS & CONSTANTES ---
LOTS_OPTIONS = [
    "🧱 Maçonnerie / Démolition", "🏗️ Plâtrerie / Isolation", "🎨 Peinture (Murs/Plafonds)",
    "🪵 Menuiserie Intérieure", "🪟 Menuiserie Extérieure", "🚿 Sols Durs (Carrelage/Faïence)",
    "🧶 Sols Souples (PVC/Moquette)", "🌳 Parquet (Flottant/Collé)", "🏠 Façade",
    "⚡ Électricité", "💧 Plomberie", "🧹 Nettoyage"
]

EQUIPES = ["Non assigné", "Équipe Issam", "Équipe MG", "Équipe TAM", "Équipe Momo DZ", 
           "Équipe Hamada", "Équipe AR", "Équipe Diaa", "Équipe M.abdo", 
           "Équipe Mansour", "Équipe M.hassan"]

CATEGORIES_STOCK = ["Peinture", "Plâtrerie", "Isolation", "Sol/Carrelage", "Sol/Parquet", "Façade", "Consommable", "Outillage", "Électricité", "Plomberie"]

# --- 4. FONCTIONS DE CHARGEMENT SÉCURISÉES ---
def load_data(key):
    path = FILES[key]
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        # Initialisation avec colonnes vides si le fichier n'existe pas
        df = pd.DataFrame(columns=COLUMNS[key])
        if key == "stocks": # On remet un stock de base par défaut
            df = pd.DataFrame([
                {"Référence": "PEINT-MAT-B", "Libellé": "Peinture Mate Blanche", "Quantité": 20, "Unité": "Pot 15L", "Catégorie": "Peinture", "Prix Achat": 75.0, "Seuil Alerte": 5},
                {"Référence": "PLACO-STD", "Libellé": "Plaque BA13 Standard", "Quantité": 50, "Unité": "Plaque", "Catégorie": "Plâtrerie", "Prix Achat": 9.0, "Seuil Alerte": 10}
            ])
        df.to_csv(path, index=False)
        return df.to_dict(orient="records")
    
    df = pd.read_csv(path)
    # Vérification que toutes les colonnes requises sont présentes
    for col in COLUMNS[key]:
        if col not in df.columns:
            df[col] = ""
    return df.to_dict(orient="records")

def save_data(key, data):
    df = pd.DataFrame(data)
    df.to_csv(FILES[key], index=False)

def safe_float(val):
    try:
        if pd.isna(val) or str(val).strip() == "": return 0.0
        return float(str(val).replace(",", ".").replace("€", "").replace(" ", "").strip())
    except: return 0.0

# Initialisation du Session State
if "data_loaded" not in st.session_state:
    for k in COLUMNS.keys():
        st.session_state[k] = load_data(k)
    st.session_state["data_loaded"] = True

# --- 5. NAVIGATION ---
st.sidebar.title("🏗️ EGY RENOVATION")
page = st.sidebar.radio("Menu Principal", ["📊 Tableau de Bord", "🚧 Gestion Chantiers", "🛒 Fournitures & Commandes", "📦 Stock Dépôt", "👥 Clients"])

# --- 6. PAGES ---

if page == "📊 Tableau de Bord":
    st.title("📊 Vue d'ensemble")
    df_c = pd.DataFrame(st.session_state["chantiers"])
    df_s = pd.DataFrame(st.session_state["stocks"])
    
    val_stock = sum(df_s.apply(lambda x: safe_float(x.get("Quantité")) * safe_float(x.get("Prix Achat")), axis=1)) if not df_s.empty else 0
    nb_encours = len(df_c[df_c["État"] == "En cours"]) if not df_c.empty else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Chantiers En cours", nb_encours)
    col2.metric("Valeur Stock", f"{val_stock:,.2f} €")
    col3.metric("Clients", len(st.session_state["clients"]))

    st.divider()
    if not df_c.empty:
        st.subheader("📅 Planning Global")
        df_c["Date Début"] = pd.to_datetime(df_c["Date Début"], errors='coerce')
        df_c["Date Fin"] = pd.to_datetime(df_c["Date Fin"], errors='coerce')
        df_plan = df_c.dropna(subset=["Date Début", "Date Fin"])
        if not df_plan.empty:
            fig = px.timeline(df_plan, x_start="Date Début", x_end="Date Fin", y="Nom du chantier", color="Équipe", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

elif page == "🚧 Gestion Chantiers":
    st.title("🚧 Suivi des Chantiers")
    t1, t2, t3 = st.tabs(["📋 Liste & Planning", "🛠️ Fiche Technique", "➕ Nouveau"])
    
    with t1:
        df_ch = pd.DataFrame(st.session_state["chantiers"])
        ed_ch = st.data_editor(df_ch, num_rows="dynamic", use_container_width=True, key="ed_ch",
                                column_config={
                                    "État": st.column_config.SelectboxColumn(options=["Devis", "En cours", "Terminé"]),
                                    "Équipe": st.column_config.SelectboxColumn(options=EQUIPES),
                                    "Date Début": st.column_config.DateColumn(),
                                    "Date Fin": st.column_config.DateColumn()
                                })
        if st.button("💾 Enregistrer Chantiers"):
            st.session_state["chantiers"] = ed_ch.to_dict(orient="records")
            save_data("chantiers", st.session_state["chantiers"])
            st.rerun()

    with t2:
        names = [c.get("Nom du chantier") for c in st.session_state["chantiers"] if c.get("Nom du chantier")]
        sel = st.selectbox("Chantier", names)
        if sel:
            idx = next(i for i, c in enumerate(st.session_state["chantiers"]) if c["Nom du chantier"] == sel)
            with st.form("f_tech"):
                st.session_state["chantiers"][idx]["Lots"] = st.multiselect("Lots", LOTS_OPTIONS, default=[l.strip() for l in str(st.session_state["chantiers"][idx].get("Lots", "")).split(",") if l.strip() in LOTS_OPTIONS])
                st.session_state["chantiers"][idx]["Commentaires Techniques"] = st.text_area("Notes", st.session_state["chantiers"][idx].get("Commentaires Techniques", ""))
                if st.form_submit_button("Sauvegarder Fiche"):
                    st.session_state["chantiers"][idx]["Lots"] = ", ".join(st.session_state["chantiers"][idx]["Lots"])
                    save_data("chantiers", st.session_state["chantiers"])
                    st.success("Fiche mise à jour")

    with t3:
        with st.form("n_ch"):
            n = st.text_input("Nom du chantier")
            cl = st.text_input("Client")
            d1 = st.date_input("Début")
            d2 = st.date_input("Fin", value=date.today() + timedelta(days=10))
            if st.form_submit_button("Créer"):
                st.session_state["chantiers"].append({"ID": f"C{len(st.session_state['chantiers'])+1}", "Nom du chantier": n, "Client": cl, "Date Début": d1, "Date Fin": d2, "État": "Devis", "Équipe": "Non assigné"})
                save_data("chantiers", st.session_state["chantiers"])
                st.rerun()

elif page == "🛒 Fournitures & Commandes":
    st.title("🛒 Besoins Matériaux")
    ch_list = [c["Nom du chantier"] for c in st.session_state["chantiers"]]
    sel_ch = st.selectbox("Sélectionner Chantier", ch_list)
    
    if sel_ch:
        col_a, col_b = st.columns([1,2])
        with col_a:
            st.subheader("Ajouter")
            src = st.radio("Source", ["Dépôt", "Fournisseur"])
            if src == "Dépôt":
                prods = {f"{p['Libellé']} ({p['Quantité']} dispos)": p for p in st.session_state["stocks"]}
                p_sel = st.selectbox("Produit", list(prods.keys()))
                q_v = st.number_input("Quantité", 1.0)
                if st.button("Valider Sortie Stock"):
                    p_data = prods[p_sel]
                    idx_s = st.session_state["stocks"].index(p_data)
                    st.session_state["stocks"][idx_s]["Quantité"] = safe_float(p_data["Quantité"]) - q_v
                    st.session_state["materiaux"].append({"Nom Chantier": sel_ch, "Désignation": p_data["Libellé"], "Quantité": q_v, "Source": "Stock", "Statut": "Pris"})
                    save_data("stocks", st.session_state["stocks"])
                    save_data("materiaux", st.session_state["materiaux"])
                    st.rerun()
            else:
                d_f = st.text_input("Produit")
                q_f = st.number_input("Quantité", 1.0)
                if st.button("Ajouter à commander"):
                    st.session_state["materiaux"].append({"Nom Chantier": sel_ch, "Désignation": d_f, "Quantité": q_f, "Source": "Fournisseur", "Statut": "À Commander"})
                    save_data("materiaux", st.session_state["materiaux"])
                    st.rerun()
        with col_b:
            df_m = pd.DataFrame(st.session_state["materiaux"])
            if not df_m.empty:
                st.dataframe(df_m[df_m["Nom Chantier"] == sel_ch], use_container_width=True)

elif page == "📦 Stock Dépôt":
    st.title("📦 Inventaire & Prix")
    
    # Formulaire d'ajout rapide (pour éviter les erreurs de saisie dans le tableau)
    with st.expander("➕ Nouveau produit au catalogue"):
        with st.form("add_stock"):
            c1, c2, c3 = st.columns(3)
            r = c1.text_input("Référence")
            l = c2.text_input("Libellé")
            cat = c3.selectbox("Catégorie", CATEGORIES_STOCK)
            if st.form_submit_button("Ajouter"):
                st.session_state["stocks"].append({"Référence": r, "Libellé": l, "Catégorie": cat, "Quantité": 0, "Unité": "unité", "Prix Achat": 0, "Seuil Alerte": 5})
                save_data("stocks", st.session_state["stocks"])
                st.rerun()

    df_s = pd.DataFrame(st.session_state["stocks"])
    ed_s = st.data_editor(df_s, num_rows="dynamic", use_container_width=True, key="ed_stock",
                          column_config={
                              "Catégorie": st.column_config.SelectboxColumn(options=CATEGORIES_STOCK),
                              "Prix Achat": st.column_config.NumberColumn(format="%.2f €")
                          })
    if st.button("💾 SAUVEGARDER STOCK & PRIX"):
        st.session_state["stocks"] = ed_s.to_dict(orient="records")
        save_data("stocks", st.session_state["stocks"])
        st.success("Stock mis à jour")

elif page == "👥 Clients":
    st.title("👥 Base Clients")
    df_cl = pd.DataFrame(st.session_state["clients"])
    ed_cl = st.data_editor(df_cl, num_rows="dynamic", use_container_width=True, key="ed_clients")
    if st.button("💾 SAUVEGARDER CLIENTS"):
        st.session_state["clients"] = ed_cl.to_dict(orient="records")
        save_data("clients", st.session_state["clients"])
        st.success("Clients sauvegardés")
