import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# Chemins des fichiers pour la persistance des données
CHANTIERS_FILE = "chantiers_data.csv"
FACTURES_FILE = "factures_data.csv"
DEVIS_FILE = "devis_data.csv"
CLIENTS_FILE = "clients_data.csv"

# Chargement et sauvegarde des données
def load_data(file, parse_dates=None):
    if os.path.exists(file):
        return pd.read_csv(file, parse_dates=parse_dates).to_dict(orient="records")
    return []

def save_data(data, file):
    df = pd.DataFrame(data)
    df.to_csv(file, index=False)

# Initialisation des données dans st.session_state
if "data" not in st.session_state:
    st.session_state["data"] = load_data(CHANTIERS_FILE, parse_dates=["Date de début", "Date de fin"])

if "factures" not in st.session_state:
    st.session_state["factures"] = load_data(FACTURES_FILE)

if "devis" not in st.session_state:
    st.session_state["devis"] = load_data(DEVIS_FILE)

if "clients" not in st.session_state:
    st.session_state["clients"] = load_data(CLIENTS_FILE)

if "equipes" not in st.session_state:
    st.session_state["equipes"] = [
        "Équipe Issam", "Équipe MG", "Équipe TAM", "Équipe Momo DZ",
        "Équipe Hamada", "Équipe AR", "Équipe Diaa", "Équipe M.abdo",
        "Équipe Mansour", "Équipe M.hassan"
    ]

# Tarifs professionnels pour les matériaux
tarifs_materiaux = {
    "Peinture Glycéro": 20.0,
    "Peinture Acrylique": 15.0,
    "Peinture Satinée": 18.0,
    "Peinture Mate": 16.0,
    "Peinture spéciale pièces humides": 22.0,
    "Enduit de rebouchage": 5.0,
    "Enduit de lissage": 6.0,
    "Enduit de dégrossissage": 4.0,
    "Enduit gouttelettes": 7.0,
    "Revêtement mural standard": 10.0,
    "Revêtement mural premium": 15.0,
    "Revêtement de sol": 25.0,
}

# --- SECTION 1: Navigation par onglets ---
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choisissez une section",
    ["Tableau de bord", "Suivi de chantier", "Planning des équipes", 
     "Calendrier interactif", "Modifier ou annuler un chantier", 
     "Gestion des Factures", "Gestion des Devis", "Gestion des Clients"]
)

# --- SECTION 2: Tableau de bord ---
if page == "Tableau de bord":
    st.title("Tableau de bord")
    total_chantiers = len(st.session_state["data"])
    consommation_totale = sum([d["Quantité nécessaire"] for d in st.session_state["data"] if "Quantité nécessaire" in d])
    cout_total = sum([d["Coût estimé (€)"] for d in st.session_state["data"] if "Coût estimé (€)" in d])
    chantiers_termines = sum(1 for d in st.session_state["data"] if d.get("État des travaux") == "Terminé")
    total_factures = len(st.session_state["factures"])
    total_devis = len(st.session_state["devis"])
    total_clients = len(st.session_state["clients"])
    total_revenu = sum([f["Montant total (€)"] for f in st.session_state["factures"]])
    devis_acceptes = sum(1 for d in st.session_state["devis"] if d["Statut"] == "Accepté")
    devis_refuses = sum(1 for d in st.session_state["devis"] if d["Statut"] == "Refusé")

    st.header("Statistiques générales")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total chantiers", total_chantiers)
    col2.metric("Total factures", total_factures)
    col3.metric("Total devis", total_devis)
    col4.metric("Total clients", total_clients)

    st.header("Finances")
    col5, col6, col7 = st.columns(3)
    col5.metric("Revenus totaux (€)", f"{total_revenu:.2f}")
    col6.metric("Devis acceptés", devis_acceptes)
    col7.metric("Devis refusés", devis_refuses)

    # Graphiques
    if st.session_state["data"]:
        st.header("Répartition des travaux par type")
        df = pd.DataFrame(st.session_state["data"])
        fig = px.pie(df, names="Type de travaux", title="Répartition des travaux")
        st.plotly_chart(fig)

    if st.session_state["factures"]:
        st.header("Revenus par chantier")
        df_factures = pd.DataFrame(st.session_state["factures"])
        fig_factures = px.bar(df_factures, x="Chantier", y="Montant total (€)", title="Revenus par chantier")
        st.plotly_chart(fig_factures)

# --- SECTION 3: Suivi de chantier ---
elif page == "Suivi de chantier":
    st.title("Suivi de chantier")
    nom_chantier = st.text_input("Nom du chantier")
    surface = st.number_input("Surface à couvrir (en m²)", min_value=1, step=1)
    type_travail = st.selectbox("Type de travaux", ["Peinture", "Enduit", "Revêtement mural", "Revêtement de sol"])
    materiau = None
    prix_unitaire = 0

    # Sélection des matériaux
    if type_travail == "Peinture":
        materiau = st.selectbox(
            "Type de peinture",
            ["Peinture Glycéro", "Peinture Acrylique", "Peinture Satinée", "Peinture Mate", "Peinture spéciale pièces humides"]
        )
        couches = st.number_input("Nombre de couches", min_value=1, max_value=5, step=1, value=2)
        prix_unitaire = tarifs_materiaux[materiau]
    elif type_travail == "Enduit":
        materiau = st.selectbox(
            "Type d'enduit",
            ["Enduit de rebouchage", "Enduit de lissage", "Enduit de dégrossissage", "Enduit gouttelettes"]
        )
        prix_unitaire = tarifs_materiaux[materiau]
    elif type_travail == "Revêtement mural":
        materiau = st.selectbox(
            "Type de revêtement mural",
            ["Revêtement mural standard", "Revêtement mural premium"]
        )
        prix_unitaire = tarifs_materiaux[materiau]
    elif type_travail == "Revêtement de sol":
        materiau = "Revêtement de sol"
        prix_unitaire = tarifs_materiaux[materiau]

    date_debut = st.date_input("Date de début des travaux", min_value=date.today())
    date_fin = st.date_input("Date de fin des travaux", min_value=date_debut)
    etat = st.selectbox("État des travaux", ["Non commencé", "En cours", "Terminé"])
    nb_personnes = st.number_input("Nombre de personnes affectées", min_value=1, max_value=20, step=1, value=3)

    if st.button("Calculer"):
        if type_travail == "Peinture":
            consommation = surface * 0.15 * couches
        else:
            consommation = surface  # Consommation simplifiée pour d'autres types de travaux
        cout = consommation * prix_unitaire  # Calcul du coût total

        st.session_state["consommation"] = consommation
        st.session_state["cout"] = cout

        st.write(f"Matériau choisi : **{materiau}**")
        st.write(f"Quantité nécessaire : **{consommation:.2f} unités**")
        st.write(f"Coût estimé : **{cout:.2f} €**")

    if st.button("Ajouter au tableau"):
        if st.session_state.get("consommation") is not None:
            st.session_state["data"].append({
                "Nom du chantier": nom_chantier,
                "Surface (m²)": surface,
                "Type de travaux": type_travail,
                "Matériau": materiau,
                "Quantité nécessaire": st.session_state["consommation"],
                "Coût estimé (€)": st.session_state["cout"],
                "Date de début": date_debut,
                "Date de fin": date_fin,
                "Nombre de personnes": nb_personnes,
                "État des travaux": etat,
                "Équipe assignée": None
            })
            save_data(st.session_state["data"], CHANTIERS_FILE)
            st.success("Tâche ajoutée avec succès !")
            st.session_state["consommation"] = None
            st.session_state["cout"] = None
        else:
            st.warning("Veuillez d'abord calculer les estimations.")

# --- SECTION 4: Planning des équipes ---
elif page == "Planning des équipes":
    st.title("Planning des équipes")

    chantier = st.selectbox("Choisir un chantier", [d["Nom du chantier"] for d in st.session_state["data"]])
    equipe = st.selectbox("Choisir une équipe", st.session_state["equipes"])

    if st.button("Assigner l'équipe"):
        for d in st.session_state["data"]:
            if d["Nom du chantier"] == chantier:
                d["Équipe assignée"] = equipe
                save_data(st.session_state["data"], CHANTIERS_FILE)
                st.success(f"L'équipe {equipe} a été assignée au chantier {chantier}.")

# --- SECTION 5: Calendrier interactif ---
elif page == "Calendrier interactif":
    st.title("Calendrier interactif")

    if st.session_state["data"]:
        df_calendar = pd.DataFrame(st.session_state["data"])
        df_calendar["Date de début"] = pd.to_datetime(df_calendar["Date de début"])
        df_calendar["Date de fin"] = pd.to_datetime(df_calendar["Date de fin"])
        fig_calendar = px.timeline(
            df_calendar,
            x_start="Date de début",
            x_end="Date de fin",
            y="Nom du chantier",
            color="Équipe assignée",
            title="Calendrier des chantiers"
        )
        st.plotly_chart(fig_calendar)
    else:
        st.write("Aucune donnée disponible pour le calendrier.")

# --- SECTION 6: Modifier ou annuler un chantier ---
elif page == "Modifier ou annuler un chantier":
    st.title("Modifier ou annuler un chantier")

    chantier = st.selectbox("Sélectionner un chantier", [d["Nom du chantier"] for d in st.session_state["data"]])

    if chantier:
        chantier_data = next((d for d in st.session_state["data"] if d["Nom du chantier"] == chantier), None)

        if chantier_data:
            new_date_debut = st.date_input("Nouvelle date de début", chantier_data["Date de début"])
            new_date_fin = st.date_input("Nouvelle date de fin", chantier_data["Date de fin"])
            new_equipe = st.selectbox("Nouvelle équipe assignée", st.session_state["equipes"], index=st.session_state["equipes"].index(chantier_data.get("Équipe assignée", "")))

            if st.button("Modifier le chantier"):
                chantier_data["Date de début"] = new_date_debut
                chantier_data["Date de fin"] = new_date_fin
                chantier_data["Équipe assignée"] = new_equipe
                save_data(st.session_state["data"], CHANTIERS_FILE)
                st.success(f"Le chantier {chantier} a été mis à jour.")

            if st.button("Annuler le chantier"):
                st.session_state["data"].remove(chantier_data)
                save_data(st.session_state["data"], CHANTIERS_FILE)
                st.success(f"Le chantier {chantier} a été annulé.")

# --- SECTION 7: Gestion des Factures ---
elif page == "Gestion des Factures":
    st.title("Gestion des Factures")
    
    facture_action = st.radio("Que souhaitez-vous faire ?", ["Ajouter une facture", "Modifier une facture"])

    if facture_action == "Ajouter une facture":
        # Formulaire d'ajout de facture
        chantier = st.selectbox("Sélectionnez un chantier", [d["Nom du chantier"] for d in st.session_state["data"]])
        facture_num = st.text_input("Numéro de facture")
        montant = st.number_input("Montant total (€)", min_value=0.0, step=0.01)
        tva = st.number_input("TVA (%)", min_value=0.0, max_value=100.0, step=1.0)
        date_emission = st.date_input("Date d'émission", min_value=date.today())
        date_limite = st.date_input("Date limite de paiement", min_value=date_emission)
        statut = st.selectbox("Statut de la facture", ["Payée", "En attente", "En retard"])

        if st.button("Ajouter la facture"):
            facture = {
                "Numéro de facture": facture_num,
                "Chantier": chantier,
                "Montant total (€)": montant,
                "TVA (%)": tva,
                "Date d'émission": date_emission,
                "Date limite de paiement": date_limite,
                "Statut": statut
            }
            st.session_state["factures"].append(facture)
            save_data(st.session_state["factures"], FACTURES_FILE)
            st.success("Facture ajoutée avec succès !")

    elif facture_action == "Modifier une facture":
        # Sélectionner une facture existante à modifier
        facture = st.selectbox("Sélectionnez une facture", [f["Numéro de facture"] for f in st.session_state["factures"]])
        
        # Trouver la facture sélectionnée
        facture_data = next((f for f in st.session_state["factures"] if f["Numéro de facture"] == facture), None)
        
        if facture_data:
            facture_num = st.text_input("Numéro de facture", value=facture_data["Numéro de facture"])
            montant = st.number_input("Montant total (€)", value=facture_data["Montant total (€)"], min_value=0.0, step=0.01)
            tva = st.number_input("TVA (%)", value=facture_data["TVA (%)"], min_value=0.0, max_value=100.0, step=1.0)
            statut = st.selectbox("Statut de la facture", ["Payée", "En attente", "En retard"], index=["Payée", "En attente", "En retard"].index(facture_data["Statut"]))
            
            if st.button("Modifier la facture"):
                facture_data["Numéro de facture"] = facture_num
                facture_data["Montant total (€)"] = montant
                facture_data["TVA (%)"] = tva
                facture_data["Statut"] = statut
                save_data(st.session_state["factures"], FACTURES_FILE)
                st.success("Facture modifiée avec succès !")

# --- SECTION 8: Gestion des Devis ---
elif page == "Gestion des Devis":
    st.title("Gestion des Devis")
    
    devis_action = st.radio("Que souhaitez-vous faire ?", ["Ajouter un devis", "Modifier un devis"])

    if devis_action == "Ajouter un devis":
        # Formulaire d'ajout de devis
        client = st.selectbox("Sélectionnez un client", [c["Nom"] for c in st.session_state["clients"]])
        devis_num = st.text_input("Numéro de devis")
        montant = st.number_input("Montant total (€)", min_value=0.0, step=0.01)
        date_emission = st.date_input("Date d'émission", min_value=date.today())
        validite = st.date_input("Date de validité", min_value=date_emission)
        statut = st.selectbox("Statut du devis", ["En attente", "Accepté", "Refusé"])

        if st.button("Ajouter le devis"):
            devis = {
                "Numéro de devis": devis_num,
                "Client": client,
                "Montant total (€)": montant,
                "Date d'émission": date_emission,
                "Date de validité": validite,
                "Statut": statut
            }
            st.session_state["devis"].append(devis)
            save_data(st.session_state["devis"], DEVIS_FILE)
            st.success("Devis ajouté avec succès !")

    elif devis_action == "Modifier un devis":
        # Sélectionner un devis existant à modifier
        devis = st.selectbox("Sélectionnez un devis", [d["Numéro de devis"] for d in st.session_state["devis"]])
        
        # Trouver le devis sélectionné
        devis_data = next((d for d in st.session_state["devis"] if d["Numéro de devis"] == devis), None)
        
        if devis_data:
            devis_num = st.text_input("Numéro de devis", value=devis_data["Numéro de devis"])
            montant = st.number_input("Montant total (€)", value=devis_data["Montant total (€)"], min_value=0.0, step=0.01)
            statut = st.selectbox("Statut du devis", ["En attente", "Accepté", "Refusé"], index=["En attente", "Accepté", "Refusé"].index(devis_data["Statut"]))
            
            if st.button("Modifier le devis"):
                devis_data["Numéro de devis"] = devis_num
                devis_data["Montant total (€)"] = montant
                devis_data["Statut"] = statut
                save_data(st.session_state["devis"], DEVIS_FILE)
                st.success("Devis modifié avec succès !")

# --- SECTION 9: Gestion des Clients ---
elif page == "Gestion des Clients":
    st.title("Gestion des Clients")
    
    client_action = st.radio("Que souhaitez-vous faire ?", ["Ajouter un client", "Modifier un client"])

    if client_action == "Ajouter un client":
        # Formulaire d'ajout de client
        nom_client = st.text_input("Nom du client")
        email = st.text_input("Email")
        telephone = st.text_input("Téléphone")
        adresse = st.text_area("Adresse")
        statut = st.selectbox("Statut du client", ["Actif", "Potentiel", "Inactif"])

        if st.button("Ajouter le client"):
            client = {
                "Nom": nom_client,
                "Email": email,
                "Téléphone": telephone,
                "Adresse": adresse,
                "Statut": statut
            }
            st.session_state["clients"].append(client)
            save_data(st.session_state["clients"], CLIENTS_FILE)
            st.success("Client ajouté avec succès !")

    elif client_action == "Modifier un client":
        # Sélectionner un client existant à modifier
        client = st.selectbox("Sélectionnez un client", [c["Nom"] for c in st.session_state["clients"]])
        
        # Trouver le client sélectionné
        client_data = next((c for c in st.session_state["clients"] if c["Nom"] == client), None)
        
        if client_data:
            nom_client = st.text_input("Nom du client", value=client_data["Nom"])
            email = st.text_input("Email", value=client_data["Email"])
            telephone = st.text_input("Téléphone", value=client_data["Téléphone"])
            adresse = st.text_area("Adresse", value=client_data["Adresse"])
            statut = st.selectbox("Statut du client", ["Actif", "Potentiel", "Inactif"], index=["Actif", "Potentiel", "Inactif"].index(client_data["Statut"]))
            
            if st.button("Modifier le client"):
                client_data["Nom"] = nom_client
                client_data["Email"] = email
                client_data["Téléphone"] = telephone
                client_data["Adresse"] = adresse
                client_data["Statut"] = statut
                save_data(st.session_state["clients"], CLIENTS_FILE)
                st.success("Client modifié avec succès !")

