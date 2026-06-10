*** Settings ***
Library    RPA.HTTP
Library    RPA.JSON
Library    Collections
Library    OperatingSystem
Library    String

*** Variables ***
${BASE_URL}      https://jsonplaceholder.typicode.com
${OUTPUT_DIR}    ${CURDIR}/../results

*** Tasks ***
Hole Benutzer Daten von API
    [Documentation]    Holt echte Daten von einer API und verarbeitet sie

    Log    ===== SCHRITT 1: GET - Einen Benutzer holen =====    console=True

    # --- Einen Benutzer holen (ID = 1) ---
    ${response}=    GET    ${BASE_URL}/users/1    expected_status=200

    # JSON parsen
    ${user}=    Convert String To JSON    ${response.text}

    # Felder extrahieren
    ${name}=        Get Value From JSON    ${user}    $.name
    ${email}=       Get Value From JSON    ${user}    $.email
    ${city}=        Get Value From JSON    ${user}    $.address.city
    ${company}=     Get Value From JSON    ${user}    $.company.name

    Log    Name    : ${name}       console=True
    Log    Email   : ${email}      console=True
    Log    Stadt   : ${city}       console=True
    Log    Firma   : ${company}    console=True

    Log    ===== SCHRITT 2: GET - Alle Posts von diesem User =====    console=True

    # --- Posts von User ID=1 holen ---
    ${response2}=    GET
    ...    ${BASE_URL}/posts?userId=1
    ...    expected_status=200

    ${posts}=        Convert String To JSON    ${response2.text}
    ${anzahl}=       Get Length    ${posts}

    Log    Dieser User hat ${anzahl} Posts geschrieben    console=True

    # Ersten Post anzeigen
    ${erster_post}=    Get From List    ${posts}    0
    ${titel}=          Get Value From JSON    ${erster_post}    $.title
    ${body}=           Get Value From JSON    ${erster_post}    $.body

    Log    Erster Post Titel : ${titel}    console=True
    Log    Inhalt            : ${body}     console=True

    Log    ===== SCHRITT 3: POST - Neuen Eintrag erstellen =====    console=True

    # --- Neuen Post senden (simuliert) ---
    ${neuer_post}=    Create Dictionary
    ...    title=Mein RPA Robot Post
    ...    body=Dieser Post wurde von einem Robocorp Robot erstellt!
    ...    userId=1

    ${response3}=    POST
    ...    ${BASE_URL}/posts
    ...    json=${neuer_post}
    ...    expected_status=201

    ${erstellt}=    Convert String To JSON    ${response3.text}
    ${neue_id}=     Get Value From JSON    ${erstellt}    $.id

    Log    ✅ Neuer Post erstellt mit ID: ${neue_id}    console=True

    Log    ===== SCHRITT 4: Ergebnisse speichern =====    console=True

    # Ergebnis als Text speichern
    ${bericht}=    Catenate    SEPARATOR=\n
    ...    ========================================
    ...    API ROBOT - ERGEBNISSE
    ...    ========================================
    ...    BENUTZER INFORMATIONEN:
    ...    Name    : ${name}
    ...    Email   : ${email}
    ...    Stadt   : ${city}
    ...    Firma   : ${company}
    ...    ----------------------------------------
    ...    POSTS:
    ...    Anzahl Posts    : ${anzahl}
    ...    Erster Titel    : ${titel}
    ...    ----------------------------------------
    ...    ERSTELLT:
    ...    Neuer Post ID   : ${neue_id}
    ...    ========================================

    Create File    ${OUTPUT_DIR}/ergebnis.txt    ${bericht}
    Log    Bericht gespeichert in: results/ergebnis.txt    console=True
