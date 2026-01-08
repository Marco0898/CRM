import streamlit as st
import pandas as pd
import plotly.express as px
import os
import urllib.parse
from datetime import date, datetime, timedelta

# --- 1. CONFIGURATION INITIALE ---
st.set_page_config(page_title="EGY RENOVATION - Master", layout="wide", page_icon="🏗️")

# --- 2. GESTION DES DOSSIERS & FICHIERS ---
DATA_DIR = "data"
DOCS_DIR = os.path.join(DATA_DIR, "bordereaux")

# Création des dossiers si inexistants
for d in [DATA_DIR, DOCS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

# Chemins des fichiers (On garde les mêmes noms pour ne pas perdre vos données si elles existent)
FILES = {
    "chantiers": os.path.join(DATA_DIR, "chantiers_master.csv"),
    "clients": os.path.join(DATA_DIR, "clients_master.csv"),
    "stocks": os.path.join(DATA_DIR, "stocks_master.csv"),
    "mouvements": os.path.join(DATA_DIR, "mouvements_master.csv"),
    "materiaux": os.path.join(DATA_DIR, "materiaux_chantier_master.csv")
}

# --- 3. DÉFINITION DES DONNÉES & STRUCTURES ---
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

# Stock de démarrage (Uniquement si fichier vide)
INITIAL_STOCK = [
    {"Référence": "PEINT-MAT-B", "Libellé": "Peinture Mate Blanche", "Quantité": 20, "Unité": "Pot 15L", "Catégorie": "Peinture", "Prix Achat": 75.0, "Seuil Alerte": 5},
    {"Référence": "PEINT-VEL-B", "Libellé": "Peinture Velours Blanche", "Quantité": 25, "Unité": "Pot 15L", "Catégorie": "Peinture", "Prix Achat": 85.0, "Seuil Alerte": 5},
    {"Référence": "PLACO-STD", "Libellé": "Plaque BA13 Standard", "Quantité": 50, "Unité": "Plaque", "Catégorie": "Plâtrerie", "Prix Achat": 9.00, "Seuil Alerte": 10},
    {"Référence": "RAIL-48", "Libellé": "Rail R48 (3m)", "Quantité": 100, "Unité": "Unité", "Catégorie": "Plâtrerie", "Prix Achat": 2.50, "Seuil Alerte": 20},
    {"Référence": "CARR-GRES", "Libellé": "Carrelage Grès Cérame 60x60", "Quantité": 40, "Unité": "m²", "Catégorie": "Sol/Carrelage", "Prix Achat": 28.00, "Seuil Alerte": 5},
]

# --- 4. FONCTIONS UTILITAIRES ---
def safe_float(val):
    """Convertit en float de manière sécurisée."""
    try:
        if pd.isna(val) or str(val).strip() == "": return 0.0
        return float(str(val).replace(",", ".").replace("€", "").replace(" ", "").strip())
    except:
        return 0.0

def load_data(key, parse_dates=None):
    """Charge les données et force la création si vide."""
    path = FILES[key]
    try:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            # Si vide, on initialise
            if key == "stocks":
                df = pd.DataFrame(INITIAL_STOCK)
            else:
                df = pd.DataFrame() # Vide pour les autres
            df.to_csv(path, index=False)
            return df.to_dict(orient="records")
        
        df = pd.read_csv(path, parse_dates=parse_dates)
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        st.error(f"Erreur lecture fichier {key}: {e}")
        return []

def save_data(key, data):
    """Sauvegarde les données dans le CSV."""
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data
    df.to_csv(FILES[key], index=False)

# --- 5. INITIALISATION SESSION STATE ---
if "data_loaded" not in st.session_state:
    st.session_state["chantiers"] = load_data("chantiers", parse_dates=["Date Début", "Date Fin"])
    st.session_state["clients"] = load_data("clients")
    st.session_state["stocks"] = load_data("stocks")
    st.session_state["mouvements"] = load_data("mouvements")
    st.session_state["materiaux"] = load_data("materiaux")
    st.session_state["data_loaded"] = True

# --- 6. NAVIGATION ---
st.sidebar.title("🏗️ EGY RENOVATION")
page = st.sidebar.radio("Menu Principal", [
    "📊 Tableau de Bord", 
    "🚧 Gestion Chantiers", 
    "🛒 Fournitures & Commandes", 
    "📦 Stock Dépôt", 
    "👥 Clients"
])

# =========================================================
# PAGE 1 : TABLEAU DE BORD
# =========================================================
if page == "📊 Tableau de Bord":
    st.title("📊 Vue d'ensemble")
    
    df_c = pd.DataFrame(st.session_state["chantiers"])
    nb_encours = len(df_c[df_c["État"] == "En cours"]) if not df_c.empty and "État" in df_c.columns else 0
    
    df_s = pd.DataFrame(st.session_state["stocks"])
    val_stock = 0.0
    if not df_s.empty:
        # Calcul sécurisé
        val_stock = sum(df_s.apply(lambda x: safe_float(x.get("Quantité")) * safe_float(x.get("Prix Achat")), axis=1))

    col1, col2, col3 = st.columns(3)
    col1.metric("Chantiers En cours", nb_encours)
    col2.metric("Valeur Stock", f"{val_stock:,.2f} €")
    col3.metric("Clients", len(st.session_state["clients"]))
    
    st.divider()
    
    if not df_c.empty and "Date Début" in df_c.columns:
        st.subheader("📅 Planning Global")
        plot_df = df_c.copy()
        # Conversion forcée des dates
        plot_df["Date Début"] = pd.to_datetime(plot_df["Date Début"], errors='coerce')
        plot_df["Date Fin"] = pd.to_datetime(plot_df["Date Fin"], errors='coerce')
        plot_df = plot_df.dropna(subset=["Date Début", "Date Fin"])
        
        if not plot_df.empty:
            fig = px.timeline(plot_df, x_start="Date Début", x_end="Date Fin", y="Nom du chantier", color="Équipe")
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

# =========================================================
# PAGE 2 : GESTION CHANTIERS
# =========================================================
elif page == "🚧 Gestion Chantiers":
    st.title("🚧 Suivi des Chantiers")
    
    tab1, tab2, tab3 = st.tabs(["📋 Liste & Planning", "🛠️ Fiche Technique", "➕ Nouveau Chantier"])
    
    # --- LISTE ÉDITABLE ---
    with tab1:
        st.info("💡 Modifiez directement dans le tableau (Double-clic). Cochez et appuyez sur 'Suppr' pour effacer une ligne.")
        
        df_chantiers = pd.DataFrame(st.session_state["chantiers"])
        
        # Configuration éditeur
        edited_chantiers = st.data_editor(
            df_chantiers,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_chantiers",
            column_config={
                "État": st.column_config.SelectboxColumn(options=["Devis", "En cours", "Terminé", "Annulé"]),
                "Équipe": st.column_config.SelectboxColumn(options=EQUIPES),
                "Date Début": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Date Fin": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Prix Devis TTC": st.column_config.NumberColumn(format="%.2f €"),
            }
        )
        
        if st.button("💾 Enregistrer modifications Chantiers", type="primary"):
            st.session_state["chantiers"] = edited_chantiers.to_dict(orient="records")
            save_data("chantiers", st.session_state["chantiers"])
            st.success("Mise à jour réussie !")
            st.rerun()

    # --- FICHE TECHNIQUE ---
    with tab2:
        # Sélecteur robuste
        opts_c = {c.get("Nom du chantier", "Inconnu"): c for c in st.session_state["chantiers"]}
        sel_c = st.selectbox("Sélectionner un chantier :", list(opts_c.keys()))
        
        if sel_c:
            chantier = opts_c[sel_c]
            idx = st.session_state["chantiers"].index(chantier)
            
            st.write(f"**Client :** {chantier.get('Client', '')} | **Budget :** {chantier.get('Prix Devis TTC', 0)}€")
            
            with st.form("tech_details"):
                # Gestion des lots
                lots_str = str(chantier.get("Lots", ""))
                current_lots = [l.strip() for l in lots_str.split(",") if l.strip() in LOTS_OPTIONS]
                new_lots = st.multiselect("Corps d'états concernés :", LOTS_OPTIONS, default=current_lots)
                
                comments = st.text_area("Notes Techniques / Accès", value=str(chantier.get("Commentaires Techniques", "")))
                
                if st.form_submit_button("Mettre à jour Fiche"):
                    st.session_state["chantiers"][idx]["Lots"] = ", ".join(new_lots)
                    st.session_state["chantiers"][idx]["Commentaires Techniques"] = comments
                    save_data("chantiers", st.session_state["chantiers"])
                    st.success("Enregistré !")

    # --- NOUVEAU CHANTIER ---
    with tab3:
        with st.form("new_ch"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nom Chantier")
            n_cli = c2.text_input("Nom Client") # Texte libre plus simple
            
            c3, c4 = st.columns(2)
            n_deb = c3.date_input("Début", date.today())
            n_fin = c4.date_input("Fin", date.today() + timedelta(days=7))
            n_prix = st.number_input("Devis TTC (€)", 0.0)
            
            if st.form_submit_button("Créer Chantier"):
                new_id = f"C{len(st.session_state['chantiers'])+100}"
                entry = {
                    "ID": new_id, "Nom du chantier": n_nom, "Client": n_cli,
                    "Date Début": n_deb, "Date Fin": n_fin, "Prix Devis TTC": n_prix,
                    "État": "Devis", "Équipe": "Non assigné"
                }
                st.session_state["chantiers"].append(entry)
                save_data("chantiers", st.session_state["chantiers"])
                st.success("Chantier créé !")
                st.rerun()

# =========================================================
# PAGE 3 : FOURNITURES
# =========================================================
elif page == "🛒 Fournitures & Commandes":
    st.title("🛒 Matériaux par Chantier")
    
    # 1. Sélection Chantier
    active_chantiers = [c for c in st.session_state["chantiers"] if c.get("État") != "Terminé"]
    choices = {c.get("Nom du chantier"): c for c in active_chantiers}
    
    sel_name = st.selectbox("Choisir le chantier :", list(choices.keys()))
    
    if sel_name:
        chantier_obj = choices[sel_name]
        
        c_add, c_list = st.columns([1, 2])
        
        # --- FORMULAIRE D'AJOUT ---
        with c_add:
            st.markdown("### Ajouter Produit")
            source = st.radio("Source :", ["📦 Stock Dépôt", "🚛 Commande Fournisseur"])
            
            with st.form("add_mat_form"):
                if source == "📦 Stock Dépôt":
                    # Création liste déroulante sécurisée
                    stock_list = st.session_state["stocks"]
                    # On filtre pour afficher label propre
                    stock_options = {f"{s.get('Libellé', 'Inc')} ({s.get('Unité', 'u')}) - Reste: {s.get('Quantité', 0)}": s for s in stock_list}
                    
                    p_sel_key = st.selectbox("Produit en stock", list(stock_options.keys())) if stock_options else None
                    q_val = st.number_input("Quantité", min_value=1.0)
                    
                    if st.form_submit_button("Sortir du Stock"):
                        if p_sel_key:
                            prod_data = stock_options[p_sel_key]
                            # Logique Stock
                            q_dispo = safe_float(prod_data.get("Quantité"))
                            q_sortie = min(q_dispo, q_val)
                            
                            # Mise à jour Stock global
                            idx = stock_list.index(prod_data)
                            st.session_state["stocks"][idx]["Quantité"] = q_dispo - q_sortie
                            save_data("stocks", st.session_state["stocks"])
                            
                            # Ajout Liste Chantier
                            st.session_state["materiaux"].append({
                                "ID Chantier": chantier_obj.get("ID"),
                                "Nom Chantier": sel_name,
                                "Référence": prod_data.get("Référence"),
                                "Désignation": prod_data.get("Libellé"),
                                "Quantité": q_sortie,
                                "Unité": prod_data.get("Unité"),
                                "Source": "Stock",
                                "Statut": "Pris"
                            })
                            save_data("materiaux", st.session_state["materiaux"])
                            st.success(f"{q_sortie} sortis du stock !")
                            st.rerun()
                        else:
                            st.error("Stock vide ou introuvable.")
                
                else: # Commande Fournisseur
                    desc = st.text_input("Désignation (ex: Parquet Chêne)")
                    q_com = st.number_input("Quantité", min_value=1.0)
                    u_com = st.text_input("Unité", "m²")
                    
                    if st.form_submit_button("Ajouter à commander"):
                        st.session_state["materiaux"].append({
                            "ID Chantier": chantier_obj.get("ID"),
                            "Nom Chantier": sel_name,
                            "Référence": "CMD",
                            "Désignation": desc,
                            "Quantité": q_com,
                            "Unité": u_com,
                            "Source": "Fournisseur",
                            "Statut": "À Commander"
                        })
                        save_data("materiaux", st.session_state["materiaux"])
                        st.success("Ajouté à la liste !")
                        st.rerun()

        # --- LISTE DES MATÉRIAUX ---
        with c_list:
            st.markdown(f"### Liste : {sel_name}")
            df_m = pd.DataFrame(st.session_state["materiaux"])
            
            if not df_m.empty:
                # Filtrer pour ce chantier
                df_filtre = df_m[df_m["Nom Chantier"] == sel_name]
                st.dataframe(df_filtre[["Désignation", "Quantité", "Unité", "Source", "Statut"]], use_container_width=True)
                
                # Bouton Email
                items_cmd = df_filtre[df_filtre["Source"] == "Fournisseur"]
                if not items_cmd.empty:
                    st.divider()
                    st.markdown("📧 **Générer texte commande**")
                    txt = f"Bonjour,\nCommande pour le chantier {sel_name} :\n"
                    for _, r in items_cmd.iterrows():
                        txt += f"- {r['Quantité']} {r['Unité']} : {r['Désignation']}\n"
                    st.text_area("Copier-coller dans votre mail :", txt, height=150)

# =========================================================
# PAGE 4 : STOCK (CORRIGÉ & ÉDITABLE)
# =========================================================
elif page == "📦 Stock Dépôt":
    st.title("📦 Inventaire Dépôt")
    
    # 1. Ajout Rapide
    with st.expander("➕ Ajouter un nouveau produit au catalogue", expanded=False):
        with st.form("new_prod_stock"):
            c1, c2, c3 = st.columns(3)
            ref = c1.text_input("Référence (ex: PEINT-01)")
            lib = c2.text_input("Libellé (ex: Peinture Bleue)")
            cat = c3.selectbox("Catégorie", CATEGORIES_STOCK)
            
            c4, c5, c6 = st.columns(3)
            qte = c4.number_input("Quantité Initiale", 0.0)
            unit = c5.text_input("Unité (Pot, m², pce...)", "Unité")
            prix = c6.number_input("Prix Achat (€)", 0.0)
            
            if st.form_submit_button("Ajouter au Stock"):
                new_p = {
                    "Référence": ref, "Libellé": lib, "Catégorie": cat,
                    "Quantité": qte, "Unité": unit, "Prix Achat": prix, "Seuil Alerte": 5
                }
                st.session_state["stocks"].append(new_p)
                save_data("stocks", st.session_state["stocks"])
                st.success("Produit ajouté !")
                st.rerun()

    # 2. Tableau Éditable (La demande principale)
    st.markdown("### 📝 Modifier le stock (Prix, Quantités)")
    df_s = pd.DataFrame(st.session_state["stocks"])
    
    if df_s.empty:
        st.warning("Le stock est vide. Utilisez le formulaire ci-dessus pour commencer.")
    else:
        # Configuration pour modification facile
        edited_stock = st.data_editor(
            df_s,
            num_rows="dynamic", # Permet ajout/suppression lignes
            use_container_width=True,
            key="editor_stock",
            column_config={
                "Prix Achat": st.column_config.NumberColumn(format="%.2f €"),
                "Quantité": st.column_config.NumberColumn(step=1),
                "Catégorie": st.column_config.SelectboxColumn(options=CATEGORIES_STOCK)
            }
        )
        
        if st.button("💾 SAUVEGARDER MODIFICATIONS STOCK", type="primary"):
            st.session_state["stocks"] = edited_stock.to_dict(orient="records")
            save_data("stocks", st.session_state["stocks"])
            st.success("Stock mis à jour avec succès !")

# =========================================================
# PAGE 5 : CLIENTS (CORRIGÉ & ÉDITABLE)
# =========================================================
elif page == "👥 Clients":
    st.title("👥 Base Clients")
    
    # 1. Ajout Rapide
    with st.expander("➕ Ajouter un Client", expanded=False):
        with st.form("new_cli"):
            n = st.text_input("Nom / Entreprise")
            e = st.text_input("Email")
            t = st.text_input("Téléphone")
            if st.form_submit_button("Ajouter"):
                st.session_state["clients"].append({"Nom": n, "Email": e, "Téléphone": t, "Adresse": ""})
                save_data("clients", st.session_state["clients"])
                st.success("Client ajouté !")
                st.rerun()

    # 2. Tableau Éditable
    st.markdown("### 📝 Liste des Clients")
    df_cli = pd.DataFrame(st.session_state["clients"])
    
    edited_clients = st.data_editor(
        df_cli,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_clients",
        column_config={
            "Email": st.column_config.LinkColumn(display_text="Envoyer mail")
        }
    )
    
    if st.button("💾 SAUVEGARDER CLIENTS", type="primary"):
        st.session_state["clients"] = edited_clients.to_dict(orient="records")
        save_data("clients", st.session_state["clients"])
        st.success("Base clients sauvegardée !")
