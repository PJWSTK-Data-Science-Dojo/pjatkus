
# Core Idea:

Robot pjatkuś to robot, który wchodzi w interakcje z przechodzacymi obok niego ludźmi.
Zaczepia ich w miły sposób, zwracając uwagę na ich wygląd, zachowanie albo ich reakcje - np. machnięcie ręką -> odpowiedź: "cześć!".

Dwie fazy projektu ( z wyłączeniem części tworzenia robota, my zajmujemy się jedynie softem high-level)

Proof of Concept -> jedyna implementacja to ta, która byłaby w stanie zostać odpalona na laptopie/ew. czymkolwiek z kamerą.

Embedded -> zamiana kodu z PoF na taki, który byłby w stanie być odpalony na arduino + dodana obsługa arduino

## 1. Proof of Concept

Rozbicie na: Cases i Features (np. 5 na każdy).

#### Cases ( przykładowe schematy akcji - reakcji robota wchodzącego w interakcje z innymi)

#### Features ( przykładowe funkcje robota, co może wykonać i jak może zareagować biorąc pod uwagę otoczenie )


### 1.1 POF components

app -> główna pętla programu

vision -> obsługa CV2 na razie

voice -> text-to-voice

llm -> prompt-to-text

features: obsługa zdarzeń. sprawdzane jest kilka warunków równocześnie i spośród nich wybierana jest odpowiednia reakcja w "features" biorąc pod uwagę otoczenie i okoliczności.

### 1.2 POF Key Capabilities

Obsługa, która zdecyduje nad:

a. wyborem osoby, z którą robot powinien wejść w interakcję
b. wyborem sposobu interakcji, jaką robot powininen wykonać
c. kontynuowaniem interakcji (osoba odeszła, nie odpowiedziała, pożegnała się itd.)
d. sprawdzeniem z iloma osobami rozmawia (albo z którą, i czy ta osoba do której ma się odezwać to ta, w którą początkowo weszła w interakcję)

### 1.3 Features

###### - Kolor ubrania

Detekcja: HSV/RGB w obszarze koszulki/spodni lub: wzięcie próbki z środka obwodu detekcji obiektu
###### - Lista Gestów

Detekcja: Machanie, Kciuk w górę

###### - Wyraz twarzy

Detekcja: Sad, Joy, Happines, None (z podziałem na piorytet, albo will_react: true/false)

###### - Ilość ludzi w okolicy

Detekcja: bounding boxes, albo people_detected = number

###### - Dialog

Detekcja: Pytanie podobne do tych z listy, lub z możliwością na odpowiedź -> odpowiedź z zakresu możliwych odpowiedzi SFW (słownik)



### 1.4 Cases

| **Case ID** | **Trigger**                     | **Akcja Robota**                                            | **Priorytet** | **Warunek Zakończenia**                      |
| ----------- | ------------------------------- | ----------------------------------------------------------- | ------------- | -------------------------------------------- |
| C1          | Machnięcie ręką                 | "Cześć! Jak się dziś masz?" + animacja LED                  | 1             | Osoba odchodzi lub brak odpowiedzi przez 10s |
| C2          | Dominujący kolor (np. czerwony) | "Uwielbiam twój czerwony sweter! Pasuje do Twojej energii!" | 2             | Brak zaangażowania (brak gestu w odpowiedzi) |
| C3          | Uśmiech skierowany w kamerę     | "Widzę, że masz dobry humor! To zaraźliwe!"                 | 3             | Osoba przestaje się uśmiechać                |
| C4          | Grupa 3+ osób                   | "Hej, ekipo! Szukacie może przewodnika?"                    | 4             | Rozproszenie grupy                           |
| C5          | Słowo kluczowe (np. "pa")       | "Do zobaczenia! Miłego dnia!" + pożegnalna animacja         | 1             | Osoba znika z kadru                          |
| C6          | Słowo kluczowe (np. "cześć")    | "Hej, jak się masz?"                                        | 1             | Osoba odchodzi lub brak odpowiedzi przez 10s |

### 1.5 Algorytmy Decydujące o wyborze odpowiedzi

### 1.6 Obsługa błędów
( co jeśli się nie powiedzie jedna z funkcji, pipeline zostanie przerwany, osoba przestanie być rozpoznawana itd.)

### 1.


obsługa inputów -> kamera , mikrofon

obsługa outputów -> 


1_ PoF features
2_ PoF loop z features i prostą decezyjnością -> jako return print(feature)
3_ wyodrębnioną obsługę vision i audio -> nasłuchiwanie
4_ llm
5_ voice

add: stan_interakcji , standby mode itd.

do przegadania z robolabem:
- test PoC na jakimś jednym arduino - to na 5tce, musimy poczekać, generalnie git
- ~~kiedy spotkanie~~
- ~~moce obliczeniowe na rasp do LLMa - 8gb~~ 
- wytyczne do robota: jakie ma mieć dodatkowe funkcje, np. jaki os, jak wgrać paczki, jak podłączyć się do niego żeby go zdebuggowac jak źle zacznie działać itd.
- jaka będzie miał pamięć i ile będzie mógł zmieścić (dysk) - karta sd 256/128GB, na akcelatorze dysk SATA
- ~~termin spotkania na żywo~~
- ~~jak im idzie generalnie i gdzie już są,~~ jak wyglądać będzie pjatkus, na czym stoją, czy mają jakieś problemy, czy chcą się zintegrować i tez coś porobić wokół data Science
- obraz z kamery - przejrzysty, ISO itd. - kamera z logitecha, albo taka na raspberry bezposrednia, dostrojanie obrazu automatycznie 12mpx

6 marzec - od tego czasu, robolab do ustalenia data spotkania

bedzie akcelerator

linux

case z patrzeniem sie na pjatkusia - wtedy moze rozmawiac z pjatkusiem

zrobimy test pjatkusia na VM

poproisc o WIDEO na ktorym moglibysmy pracowac

podlaczyc sie po RJ45 zeby debuggowac

oczka na wyswietlaczu - beda przez robolaba zrobione

biblioteki w C - porty COM do obslugi output input 

4 miesiace, raczej nie zdazymy do konca semestru - korpus

mikro bedzie do ogarniecia - co wybrac

glosniczek bedzie 

frame = 5

pipeline 

nasluchiwanie i oczekiwanie na interakcje

jak nikt nie gada - to patrzy

enum z states : jestem w interakcji - nie jestem

odpowiadam - albo nasluchuje co on mowi, ale jestem nadal w interakcji

state - zaczepienie ludzi

jesli minelo duzo czasu od interakcji z czlowiekiem -> zrob interakcje 

RAG z chatbota pjatka-gpt

slownik rozdzielic na zaczepki / odpowiedzi 

randomsampling z malego kwadratu - maxa albo najbardziej wyrozniajacy sie

whisperx

settings file

slownik - na embedding - gotowa odpowiedz, prawdopodobienstwo procentowe, jak bardzo podobne do tego

trzeba pamietac o tym - ile ramu nam zostanie?

redis - do uzycia jako cache

oddzielic "app" jako sama petle programu do ogarniania cache, DB, ramu, RAG itd.