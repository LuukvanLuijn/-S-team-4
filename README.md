# -S-team-4

Daniel\
abderrahman\
Luuk\
mohammed is er ook\
Amir

---

# Steam Dashboard 

## Inhoudsopgave

- [Inleiding](#inleiding)
- [Doelen en Opdracht](#doelen-en-opdracht)
- [Technologieën en Structuur](#technologieën-en-structuur)
- [SDG: Duurzame Ontwikkelingsdoelen](#sdg-duurzame-ontwikkelingsdoelen)
- [Gebruik](#gebruik)
- [Bijdragen](#bijdragen)

---

## Inleiding

Dit project is ontwikkeld in opdracht van Steam om als startup ondersteuning te bieden aan het platform. Steam, ontwikkeld door Valve Corporation, is een online gameplatform met meer dan 30.000 spellen en 100 miljoen gebruikers. De hoofdopdracht is het ontwikkelen van een grafische weergave die inzicht biedt in het gaminggedrag van vrienden op het Steam-platform, ondersteund door hardwarecomponenten zoals een neopixel en afstandssensor.

## Doelen en Opdracht

Steam wil haar klanten beter begrijpen en bedienen door inzicht te krijgen in het gaminggedrag van gebruikers en klantsegmenten. Het doel van deze opdracht is om verschillende grafieken en analyses te maken die antwoord geven op vragen zoals:
- Welke games spelen mijn vrienden?
- Welke spellen worden het meest gespeeld?
- Wanneer zijn mijn vrienden online?
- Welke aanbevelingen kunnen er gedaan worden om te spelen?

Jullie team fungeert als startup en is verantwoordelijk voor:
1. Het formuleren van een visie, missie, en strategie voor de ondersteuning van Steam.
2. Het opstellen van een requirements specificatie, met zowel functionele als niet-functionele vereisten.
3. Het presenteren van de plannen aan Steam, inclusief een begroting voor virtuele financiering van het project.


## Algemeen

- **SDG - Duurzaamheidsdoel**: Elk teamlid kiest een Duurzaam Ontwikkelingsdoel (SDG) en werkt de voordelen en nadelen hiervan uit in het projectverslag. Het team kiest hieruit één SDG die verder uitgewerkt wordt in het MVP.

#### Basisapplicatie met Data

- **Applicatie in Python**: In de eerste sprint wordt een basisapplicatie in Python ontwikkeld die Steam-data laadt en visualiseert in een Graphical User Interface (GUI) gemaakt met Tkinter of een ander framework (in overleg met de opdrachtgever).
- **Dataweergave**: De basisapplicatie toont data aan de gebruiker in een interactief dashboard en communiceert met:
  - Een dataset voor lineaire regressie en andere AI-technieken.
  - Een niet-lokale database voor aanvullende informatie (bijvoorbeeld Azure PostgreSQL).
  - Een Raspberry Pi Pico W.
- **Statistische Analyse**: Het MVP biedt verschillende statistieken voor inzicht in Steam-data, waaronder:
  - **Beschrijvende Statistiek**: Zelf-geïmplementeerde functies voor gemiddelden, mediaan, enzovoort.
  - **Voorspellende Statistiek**: Lineaire regressie met gradient descent, zonder gebruik van externe Python libraries.

#### Hardware-integratie

- **Neopixel en Afstandssensor**: De basisapplicatie communiceert met een neopixel en afstandssensor voor extra functionaliteiten die het gebruikersgedrag ondersteunen.


## Technologieën en Structuur

- **Frontend**: CustomTkinter
- **Backend**: Python
- **Database**: PostgreSQL in de Azure Cloud
- **Hardware**: Raspberry Pi Pico W, Neopixel, Afstandssensor
- **AI en Machine Learning**: Zelf-ontwikkelde algoritmen voor beschrijvende en voorspellende statistieken
- **Cloud en Cyber Security**: Gebruik van een externe database in de cloud (Azure)

## SDG: Duurzame Ontwikkelingsdoelen

Het project ondersteunt de volgende SDG's:

- **4. Kwaliteitsonderwijs**: Door het analyseren van gamegedrag kunnen educatieve platforms inzicht krijgen in hoe jongeren leren en spelen, wat nuttig kan zijn bij het ontwerpen van educatieve content.
- **8. Waardig Werk en Economische Groei**: Door het bieden van inzichtelijke data aan ontwikkelaars en bedrijven in de gamingindustrie ondersteunt dit project economische groei.
- **9. Industrie, Innovatie en Infrastructuur**: Met gebruik van data-analyse en hardware-interactie biedt dit project een innovatieve benadering voor data-gebaseerde oplossingen in de gamingwereld.


## Gebruik

1. Start de GUI en bekijk verschillende statistieken over gaminggedrag.
2. Gebruik de filters om specifieke data te bekijken, zoals populaire games en online tijden van vrienden.
3. Verken de interactie met hardwarecomponenten, zoals de neopixel- en afstandssensorfuncties.

## Bijdragen

Bijdragen aan dit project zijn welkom! Volg deze stappen:

1. Fork de repository.
2. Maak een nieuwe branch voor je wijzigingen.
3. Commit en push je wijzigingen.
4. Open een pull request.
