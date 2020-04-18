:- dynamic symptoms/1.
:- dynamic not_symptoms/1.
:- dynamic pain/1.
:- dynamic mood/1.
:- dynamic asked/1.

generate_question(X):- questions_mood_pain(L), random_member(X,L).
generate_question_2(X):- questions_symptoms(L), random_member(X,L).

generate_gesture():-
    (   (mood(weepy); mood(stressed), mood(fear); pain(manageable_pain); pain(mild_pain)), calming_gesture(L); 
    (mood(angry); pain(unbearable_pain); pain(lot_of_pain)), polite_gesture(L);
    (pain(no_pain); mood(calm)), normal_gesture(L)),
    random_member(G, L).

ask_mood(X):-
    mood_library(L), not_askedList(L,R), member(X,R).
ask_pain(X):-
    pain_library(L), not_askedList(L,R), member(X,R).
ask_related(M, Y):-
    findnsols(100,X,related(X,Y),L), validList(L, R), member(M, R).
ask_random(X):-
    fever(A), cold(B), injury(C), food_poisoning(D), allergy(E), 
    append(A,B,AB), append(AB,C,ABC), append(ABC,D,ABCD), append(ABCD,E,ABCDE), 
    validList(ABCDE, R), random_member(X, R).
not_askedList(L, R):- 
    findnsols(100,X,asked(X),History), list_to_set(L,S), list_to_set(History,H), subtract(L,H,R).
validList(L, R):-
    findnsols(100,X,symptoms(X),SymptomsList), findnsols(100,X,not_symptoms(X),Not_symptomsList), append(SymptomsList,Not_symptomsList,History),
    pain_library(PainList), mood_library(MoodList), append(PainList, MoodList, Pain_mood), 
	list_to_set(L,S), list_to_set(History,H), list_to_set(Pain_mood, P),
    subtract(S,H,R1), subtract(R1,P,R).

diagnose(Y):- 
    aggregate_all(count, symptoms(X), Count), 
    (Count==1-> Y = no_illness; Count>1 ->  
    (   aggregate_all(count, isSymptomOfFever(X), FeverCount),
    aggregate_all(count, isSymptomOfCold(X), ColdCount),
    aggregate_all(count, isSymptomOfInjury(X), InjuryCount),
    aggregate_all(count, isSymptomOfFood_poisoning(X), FoodPoisoningCount),
    aggregate_all(count, isSymptomOfAllergy(X), AllergyCount),
    (max_member(FeverCount, [FeverCount, ColdCount, InjuryCount, FoodPoisoningCount, AllergyCount]) ->  Y = fever;
    max_member(ColdCount, [FeverCount, ColdCount, InjuryCount, FoodPoisoningCount, AllergyCount]) ->  Y = cold;
    max_member(InjuryCount, [FeverCount, ColdCount, InjuryCount, FoodPoisoningCount, AllergyCount]) ->  Y = injury;
    max_member(FoodPoisoningCount, [FeverCount, ColdCount, InjuryCount, FoodPoisoningCount, AllergyCount]) ->  Y = food_poisoning;
    max_member(AllergyCount, [FeverCount, ColdCount, InjuryCount, FoodPoisoningCount, AllergyCount]) ->  Y = allergy))).  

isSymptomOfFever(X):- symptoms(X), fever(L), member(X,L).
isSymptomOfCold(X):- symptoms(X), cold(L), member(X,L).
isSymptomOfInjury(X):- symptoms(X), injury(L), member(X,L).
isSymptomOfFood_poisoning(X):- symptoms(X), food_poisoning(L), member(X,L).
isSymptomOfAllergy(X):- symptoms(X), allergy(L), member(X,L).

append([A | B], C, [A | D]) :- append(B, C, D).
append([], A, A).

member(X,[X|_]).
member(X,[_|R]) :- member(X,R).

related(X,Y):-
	fever(L),member(X,L),member(Y,L);
	cold(L),member(X,L),member(Y,L);
	injury(L),member(X,L),member(Y,L);
	food_poisoning(L),member(X,L),member(Y,L);
	allergy(L),member(X,L),member(Y,L).

pain(X).
mood(X).
pain_library([no_pain,  mild_pain, moderate_pain, lots_of_pain, unbearable_pain]).
mood_library([calm, angry, weepy, stressed, fear]).

polite_gesture([look_concerned, mellow_voice, light_touch, faint_smile]).
calming_gesture([look_composed, look_attentive, gentle_voice]).
normal_gesture([broad_smile, beaming_voice]).

fever([high_temperature, sweat, no_pain, weepy, fatigue]).
cold([sneeze, cough, fatigue, calm, no_pain]).
injury([bleeding, new_wound, lots_of_pain, unbearable_pain, weepy]).
food_poisoning([diarrhea, no_appetite, mild_pain, moderate_pain, high_temperature]).
allergy([itch, red_spots, stressed, watery_eyes, no_pain]).

symptoms(X).
not_symptoms(X).
asked(X).

questions_mood_pain(['Are you feeling ',
                  'Perhaps you are feeling ',
                  'Do you feel ',
                  'Hmm... I guess you feel ',
                  'Maybe you feel ']).

questions_symptoms(['What about ',
                    'Hmm... Do you have ',
                    'How about ',
                    'And ',
                    'Then do you have ']).