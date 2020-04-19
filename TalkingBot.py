import os
import random
from pyswip import Prolog
import sys
import asyncio
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

class PrologInteractor(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(PrologInteractor, self).__init__(*args, **kwargs)
        self.prolog = Prolog()
        self.prolog.consult('Talkingbox.pl')
        self.current_state = 'mood'
        self.mood = ''
        self.pain = ''
        self.symptom = ''
        self.diagnose = ''
        self.previous_msg = ''
        print('Initialzing...')
        

    async def on_chat_message(self, msg):
        _, _, id = telepot.glance(msg)
        gesture = list(self.prolog.query('generate_gesture(X)', maxresult=1))
        gesture = '<{}> \n'.format(gesture[0]['X'])
        print('Text:' + msg['text'])
        print('State:'+ self.current_state)
        print('Mood:' + self.mood)
        print('Pain:' + self.pain)
        print('Symptom:' + self.symptom)
        print('Diagnose:' + self.diagnose)
        print('\n')

        if (self.current_state == 'mood'):
            if (msg['text'] == '/start'):
                mood = list(self.prolog.query('ask_mood(X)', maxresult=1))
                self.mood = mood[0]['X']
                gesture = '<greet> \n' 
                question = 'Hi, I am Doctor Sympathy. How are you feeling today? Feeling ' + self.mood + '?'
                self.prolog.assertz('asked({})'.format(self.mood))
                kb = ReplyKeyboardMarkup(keyboard=[['Yes', 'No']])
                await bot.sendMessage(id, gesture+question, reply_markup=kb)
        
            elif (msg['text'] == 'No'):
                intro = list(self.prolog.query('generate_question(X)', maxresult=1))
                mood = list(self.prolog.query('ask_mood(X)', maxresult=1))
                self.mood = mood[0]['X']
                question = intro[0]['X'] + self.mood + '?'
                self.prolog.assertz('asked({})'.format(self.mood))
                kb = ReplyKeyboardMarkup(keyboard=[['Yes', 'No']])
                await bot.sendMessage(id, gesture+question, reply_markup=kb)
            
            elif (msg['text'] == 'Yes'):
                self.prolog.assertz('mood({})'.format(self.mood))
                kb = ReplyKeyboardMarkup(keyboard=[['Yes', 'No']])
                question = "Ok... Is it correct to say that you are not in pain?"
                await bot.sendMessage(id, gesture+question, reply_markup=kb)
                self.prolog.assertz('asked({})'.format("no_pain"))
                self.pain = 'no_pain' 
                self.current_state = 'pain'

        elif (self.current_state == 'pain'):
            if (msg['text'] == 'No'):
                intro = list(self.prolog.query('generate_question(X)', maxresult=1))
                pain = list(self.prolog.query('ask_pain(X)', maxresult=1))
                self.pain = pain[0]['X']
                question = intro[0]['X'] + self.pain + '?'
                self.prolog.assertz('asked({})'.format(self.pain))
                kb = ReplyKeyboardMarkup(keyboard=[['Yes', 'No']])
                await bot.sendMessage(id, gesture+question, reply_markup=kb)
            elif (msg['text'] == 'Yes'):
                self.prolog.assertz('pain({})'.format(self.pain))
                symptom = list(self.prolog.query('ask_related(X,{})'.format(self.pain), maxresult=1))
                self.symptom = symptom[0]['X']
                question = "I see... For the past few days, do you have {}?".format(self.symptom) 
                kb = ReplyKeyboardMarkup(keyboard=[['Yes', 'No']])
                await bot.sendMessage(id, gesture+question, reply_markup=kb)
                self.current_state = 'symptom'  

        elif (self.current_state == 'symptom'):
            if (msg['text'] == 'No'):
                self.prolog.assertz('not_symptoms({})'.format(self.symptom))
                intro = list(self.prolog.query('generate_question_2(X)', maxresult=1))
                symptom = list(self.prolog.query('ask_random(X)', maxresult=1))
                if (symptom!=[]):
                    self.symptom = symptom[0]['X']
                    question = intro[0]['X'] + self.symptom + '?'
                    kb = ReplyKeyboardMarkup(keyboard=[['Yes', 'No']])
                    await bot.sendMessage(id, gesture+question, reply_markup=kb)
                else:
                    kb = ReplyKeyboardMarkup(keyboard=[['Diagnose']], one_time_keyboard=True)
                    await bot.sendMessage(id, 'Your result is ready. Please select \'Diagnose\' to continue.', reply_markup=kb)
                self.previous_msg = 'No'

            elif (msg['text'] == 'Yes'):
                self.prolog.assertz('symptoms({})'.format(self.symptom))
                intro = list(self.prolog.query('generate_question_2(X)', maxresult=1))
                symptom = list(self.prolog.query('ask_related(X,{})'.format(self.symptom), maxresult=1))
                if (symptom!=[]):
                    self.symptom = symptom[0]['X']
                    question = intro[0]['X'] + self.symptom + '?'
                    kb = ReplyKeyboardMarkup(keyboard=[['Yes', 'No']])
                    await bot.sendMessage(id, gesture+question, reply_markup=kb)
                else:
                    if (self.previous_msg == 'Yes'):
                        kb = ReplyKeyboardMarkup(keyboard=[['Diagnose']], one_time_keyboard=True)
                        await bot.sendMessage(id, 'Your result is ready. Please select \'Diagnose\' to continue.', reply_markup=kb)
                    else:
                        symptom = list(self.prolog.query('ask_random(X)', maxresult=1))
                        self.symptom = symptom[0]['X']
                        question = intro[0]['X'] + self.symptom + '?'
                        kb = ReplyKeyboardMarkup(keyboard=[['Yes', 'No']])
                        await bot.sendMessage(id, gesture+question, reply_markup=kb)
                self.previous_msg = 'Yes'
                
            elif (msg['text'] == 'Diagnose'):
                diagnose = list(self.prolog.query('diagnose(X)', maxresult=1))
                self.diagnose = diagnose[0]['X'] 
                if(self.diagnose=='no_illness'):
                    outcome = 'You are perfectly healthy! Do continue to exercise and keep fit!'
                else:
                    outcome = 'Based on the symptom(s), you are likely to have {}. Please visit the nearby clinic to get help.'.format(self.diagnose)
                await bot.sendMessage(id, outcome)
                exit()



TOKEN = "1150310497:AAEYmBDdkP21yfCmQR6xd4E2VSPR5p0UNnY"

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, PrologInteractor, timeout=500),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()