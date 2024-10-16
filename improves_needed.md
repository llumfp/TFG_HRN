# AGENT RECEPTION
## try_agent_reception_20241011-141555.csv:
**Problemes**
- Quan no hi ha cap tasca desfavorable, moltes vegades surten totes les altres favorables. 
  Només volem que surtin tasques favorables quan la condició és de preferència a fer aquella tasca.
- De vegades hi han tasques desfavorables i totes les altres es fiquen com a desfavorables.


**Solucions**
- Prompt tunning explicant millor que es considera per desfavorable i desfavorable
- Detecció per separat de tasques favorables i desfavorables:
    - opció 1: sentiment analysis per veure si és una frase positiva o negativa i després extreure les tasques corresponents
    - opció 2: fer 2 prompts de forma separada, una per favorables i l'altres per desfavorables


Potser simplificar centrar-nos en preferències desfavorables. El consepte d'afavorir és ambigu. 
Provar això.

Preferències al principi i després anar fent propostes mútuament. 

"Negociar GOALS!!", les subtasques són més dirigides a la planificació.

Costos individuals
Preferències i costos estàndards
Costos de tasca d'equip -> haviem dit només temps. Afegir el concepte d'urgència / prioritat d'execució.
        Cost temporal + temps en que el visitant s'espera, per exemple
        + cost extra si arribem tard a l'hora establerta per la visita guiada

RECORDA: variable assignar qui fa la tasca.

Intentar ficar weights diferents. Intentar pintar on apareixen aquests 3 punts en l'espai 3D. 


