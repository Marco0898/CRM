statut
        }
        st.session_state["factures"].append(facture)
        save_data(st.session_state["factures"], FACTURES_FILE)
        st.success("Facture ajoutée avec succès !")

    # Modifier une facture existante
    if st.session_state["factures"]:
        st.header("Modifier une facture existante")
        facture_a_modifier = st.selectbox(
            "Sélectionnez une facture à modifier",
            [f["Numéro de facture"] for f in st.session_state["factures"]]
        )
        if facture_a_modifier:
            facture_data = next((f for f in st.session_state["factures"] if f["Numéro de facture"] == facture_a_modifier), None)
            if facture_data:
                new_montant = st.number_input("Nouveau montant (€)", value=facture_data["Montant total (€)"], min_value=0.0, step=0.01)
                new_statut = st.selectbox("Nouveau statut", ["Payée", "En attente", "En retard"], index=["Payée", "En attente", "En retard"].index(facture_data["Statut"]))
                if st.button("Enregistrer les modifications"):
                    facture_data["Montant total (€)"] = new_montant
                    facture_data["Statut"] = new_statut
                    save_data(st.session_state["factures"], FACTURES_FILE)
                    st.success("Facture modifiée avec succès !")

# --- SECTION 8: Gestion des Devis ---
elif page == "Gestion des Devis":
    st.title("Gestion des Devis")

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

    # Modifier un devis existant
    if st.session_state["devis"]:
        st.header("Modifier un devis existant")
        devis_a_modifier = st.selectbox(
            "Sélectionnez un devis à modifier",
            [d["Numéro de devis"] for d in st.session_state["devis"]]
        )
        if devis_a_modifier:
            devis_data = next((d for d in st.session_state["devis"] if d["Numéro de devis"] == devis_a_modifier), None)
            if devis_data:
                new_montant = st.number_input("Nouveau montant (€)", value=devis_data["Montant total (€)"], min_value=0.0, step=0.01)
                new_statut = st.selectbox("Nouveau statut", ["En attente", "Accepté", "Refusé"], index=["En attente", "Accepté", "Refusé"].index(devis_data["Statut"]))
                if st.button("Enregistrer les modifications"):
                    devis_data["Montant total (€)"] = new_montant
                    devis_data["Statut"] = new_statut
                    save_data(st.session_state["devis"], DEVIS_FILE)
                    st.success("Devis modifié avec succès !")

# --- SECTION 9: Gestion des Clients ---
elif page == "Gestion des Clients":
    st.title("Gestion des Clients")

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

    # Modifier un client existant
    if st.session_state["clients"]:
        st.header("Modifier un client existant")
        client_a_modifier = st.selectbox(
            "Sélectionnez un client à modifier",
            [c["Nom"] for c in st.session_state["clients"]]
        )
        if client_a_modifier:
            client_data = next((c for c in st.session_state["clients"] if c["Nom"] == client_a_modifier), None)
            if client_data:
                new_email = st.text_input("Nouveau email", value=client_data["Email"])
                new_statut = st.selectbox("Nouveau statut", ["Actif", "Potentiel", "Inactif"], index=["Actif", "Potentiel", "Inactif"].index(client_data["Statut"]))
                if st.button("Enregistrer les modifications"):
                    client_data["Email"] = new_email
                    client_data["Statut"] = new_statut
                    save_data(st.session_state["clients"], CLIENTS_FILE)
                    st.success("Client modifié avec succès !")

