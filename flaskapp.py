#--------------------------
'''Welcome to the Modern Application Project by Allan Pais'''

#--------------------------------------------------------------------------------------------------------------
#Imports


from enum import unique
import os
import time
from re import template
from flask import Flask,redirect
from flask import render_template
from flask import request,url_for
from flask.scaffold import F
from flask_restful import Resource,Api,fields,marshal_with
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import Session
current_dir=os.path.abspath(os.path.dirname(__file__))

app=None
api=None

def create_app():
    db=SQLAlchemy()
    app=Flask(__name__, template_folder="templates")
    db.init_app(app)
    api=Api(app)
    app.app_context().push()
    return app,api

app,api=create_app()

db=SQLAlchemy()
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(current_dir,"Flashcard.sqlite3")
db= SQLAlchemy(app)
db.init_app(app)
api = Api(app)
app.app_context().push()

#--------------------------------------------------------------------------------------------------------------
#Models

class DataStore(db.Model):
    __tablename__='Data_store'
    Email_id=db.Column(db.String,db.ForeignKey("Login_information.Email_id"),nullable=True,primary_key=True)
    Deck=db.Column(db.String,nullable=False,primary_key=True)
    Score=db.Column(db.Integer,nullable=False)
    Last_visited=db.Column(db.String,nullable=False)
    Num_cards=db.Column(db.Integer,nullable=False)

class LoginInformation(db.Model):
    __tablename__='Login_information'
    f_name=db.Column(db.String, nullable=False)
    last_name=db.Column(db.String,nullable=False)
    Email_id=db.Column(db.String,nullable=False,unique=True,primary_key=True)
    Password=db.Column(db.String,nullable=False)

class FlashcardStore(db.Model):
    __tablename__='Flashcard_store'
    Email_id=db.Column(db.String,db.ForeignKey("Login_information.Email_id"),nullable=True,primary_key=True)
    Deck_name=db.Column(db.String,nullable=False,primary_key=True)
    Question=db.Column(db.String,nullable=False,primary_key=True)
    Answer=db.Column(db.String,nullable=False)
    

db.create_all()
db.session.commit()

engine= create_engine("sqlite:///./Flashcard.sqlite3")

#--------------------------------------------------------------------------------------------------------------
#Controllers

@app.route("/",methods=["GET","POST"])

def Login ():
    if request.method=="GET":
        return render_template("Loginpage.html")
    if request.method=="POST":
        eid=request.form["Email_id"]
        pswd=request.form["Password"]
        su=request.form["keyval"]
        if su=='1':

            return render_template("signup.html")


        if su=='0':
            Login_info=LoginInformation.query.distinct().filter_by(Email_id=eid).first()
            
            if (Login_info==None):
                return render_template("Loginpage.html")

            else:
                Login=Login_info.Email_id
                Pasw=Login_info.Password
                
                if (eid!=Login or pswd!=Pasw):
                    print("No match ")
                    return render_template("Loginpage.html")
                                
                else:    
                    return redirect(f"/decks.html/{eid}")
        
        if su=='2':
            return redirect(f"/api/AdminApi/{0}")
                
 
    print("---------------Start------------")
    print(eid,pswd,su)
    print("---------------End------------")
   
    return ("Some error has occured!")

@app.route("/signup.html",methods=["GET","POST"])

def Signup():
    if request.method=="POST":
        fname=request.form["f_name"]
        lname=request.form["l_name"]
        eid=request.form["Email_id"]
        pswd=request.form["Password"]
        
        print("---------------Start------------")
        print(fname,lname,eid,pswd)
        print("---------------End------------")

        
        try:
            db.session.begin()
            s=LoginInformation(f_name=fname,last_name=lname,Email_id=eid,Password=pswd)
            db.session.add(s)
            db.session.flush()
            db.session.commit()
            
        except:

            print("Rolling back due to an exception occurence")
            db.session.rollback()
            return render_template("signup.html")

        finally:
            db.session.commit()
            print("commiting changes")
            return render_template("Loginpage.html")
          
        

@app.route("/decks.html/<user_name>",methods=["GET","POST"])

def Selectroute(user_name):
    card_nos=[]
    deck_names=[]
    card_scores=[]
    last_viewed=[]
    indsend=0

    [card_nos.append(x.Num_cards) for x in DataStore.query.filter_by(Email_id=user_name).all()]
    [deck_names.append(x.Deck) for x in DataStore.query.filter_by(Email_id=user_name).all()]
    [card_scores.append(x.Score) for x in DataStore.query.filter_by(Email_id=user_name).all()]
    [last_viewed.append(x.Last_visited) for x in DataStore.query.filter_by(Email_id=user_name).all()]
        

    if request.method=="GET":
        print(user_name)
        
        print("---------------Start------------")
        print(card_nos)
        print(deck_names)
        print(card_scores)
        print(last_viewed)
        print("---------------End------------") 
        send_list=[]
        for i in range(len(deck_names)):
            send_list.append([card_nos[i],deck_names[i],card_scores[i],last_viewed[i]])
        print(send_list)
        return render_template("decks.html", send_list=send_list, count=1)
       
    
    if request.method=="POST":
      
       bval=request.form["button_value"]
       
       if bval=='01':

           r_button=request.form["user_deck_choice"]
           deck_value=(deck_names[int(r_button)-1])
           
           return redirect(f"/Addcard.html/{user_name}/{deck_value}")
       elif bval=='02':

           r_button=request.form["user_deck_choice"]
           deck_value=(deck_names[int(r_button)-1])

           return redirect(f"/deletecard.html/{user_name}/{deck_value}")
       elif bval=='03':

            r_button=request.form["user_deck_choice"]
            deck_value=(deck_names[int(r_button)-1])

            deck_name=deck_names[int(r_button)-1]
            DataStore.query.filter_by(Deck=deck_name,Email_id=user_name).delete()
            FlashcardStore.query.filter_by(Deck_name=deck_name,Email_id=user_name).delete()
            db.session.commit()
            return redirect(f"/decks.html/{user_name}")

       elif bval=='04':
           return redirect(f"/Add_deck.html/{user_name}")
       elif bval=='05':

           r_button=request.form["user_deck_choice"]
           deck_value=(deck_names[int(r_button)-1])

           return redirect(f"/Practice.html/{user_name}/{deck_value}/{indsend}/{0}")
       elif bval=='06':
           r_button=request.form["user_deck_choice"]
           deck_value=(deck_names[int(r_button)-1])
           return redirect(f"/Exammode.html/{user_name}/{deck_value}/{indsend}/{0}")
       return("Sucess")  
      
@app.route("/Addcard.html/<user_name>/<deck_name>",methods=["GET","POST"])

def addcard(user_name,deck_name):

    if request.method=="GET":
       return render_template("Addcard.html",user_name=user_name,deck_name=deck_name)

    if request.method=="POST":
        question=request.form["Question"]
        answer=request.form["Answer"]
        option=request.form["choice"]
        if option=="00":
            print("insider")
            db.session.begin()
            data=FlashcardStore(Email_id=user_name,Deck_name=deck_name,Question=question,Answer=answer)
            
            db.session.add(data)
            db.session.commit()
            db.session.close()

            return render_template("Addcard.html",user_name=user_name,deck_name=deck_name)
        elif option=="01":
            return redirect(f"/decks.html/{user_name}")


@app.route("/deletecard.html/<user_name>/<deck_name>",methods=["GET","POST"])

def deletecard(user_name,deck_name):
    deck_name_pass=[]
    card_question=[]

    [deck_name_pass.append(x.Deck_name) for x in FlashcardStore.query.filter_by(Email_id=user_name,Deck_name=deck_name).all()]
    [card_question.append(x.Question) for x in FlashcardStore.query.filter_by(Email_id=user_name,Deck_name=deck_name).all()]

    if request.method=="GET":

        delete_cards=[]
        for i in range(len(card_question)):
            delete_cards.append([deck_name_pass[i],card_question[i]])
     
        return render_template("deletecard.html",delete_cards=delete_cards, user_name=user_name, deck_name=deck_name)
        
    if request.method=="POST":

        delete_select=int(request.form["delete_select"])
        option=request.form["choice"]
        print(delete_select,option)
        

        if option=="00":
            print(deck_name_pass)
            deck_name_delete=deck_name_pass[int(delete_select-1)]
            card_question_delete=card_question[int(delete_select-1)]
            FlashcardStore.query.filter_by(Deck_name=deck_name_delete,Question=card_question_delete).delete()          
            db.session.commit()
            print("deleted")

            return redirect(f"/decks.html/{user_name}")



@app.route("/Add_deck.html/<user_name>",methods=["GET","POST"])

def add_deck(user_name):

    if request.method=="GET":
        return render_template("Add_deck.html",user_name=user_name)

    if request.method=="POST":
        deckinfo=request.form["Add_deck"]
        choice=request.form["option"]

        data=DataStore(Email_id=user_name,Deck=deckinfo,Score=0,Last_visited=str(time.strftime("%d/%m/%Y")),Num_cards=0)
            
        db.session.add(data)
        db.session.commit()
    return redirect(f"/decks.html/{user_name}")   
        


@app.route("/Practice.html/<user_name>/<deck_name>/<index_value>/<score>",methods=["GET","POST"])

def practice(user_name,deck_name,index_value,score):
    
    questions=[]
    answers=[]
    score_easy=int(score)
    score_med=0
    score_hard=0
    i=int(index_value)

    [questions.append(x.Question) for x in FlashcardStore.query.filter_by(Email_id=user_name,Deck_name=deck_name).all()]
    [answers.append(x.Answer) for x in FlashcardStore.query.filter_by(Email_id=user_name,Deck_name=deck_name).all()]
    
   
    if request.method=="GET":
            question_send_01=0
            question_send_02=questions[0]
            question_send_03=answers[0]
            return render_template("Practice.html",question_01=question_send_01,question_02=question_send_02,question_03=question_send_03,user_name=user_name,deck_name=deck_name,score_easy=int(score_easy),score_med=int(score_med),score_hard=int(score_hard),index_value=int(index_value))
    
    if request.method=="POST":
        
        if i>=len(questions):

            
            hardness=request.form["hardness"]
            if hardness=="0":
                score_easy+=(1/len(questions))*100
            elif hardness=="1":
                score_med+=(1/len(questions))*100
            elif hardness=="2":
                score_med+=(1/len(questions))*100
            
            data_update=DataStore.query.filter_by(Email_id=user_name,Deck=deck_name).first()
            data_update.Score=int(score_easy)
            data_update.Num_cards=len(questions)
            data_update.Last_visited=str(time.strftime("%d/%m/%Y"))
            

            db.session.commit()
            return redirect(f"/decks.html/{user_name}")

        question_send_01=i
        question_send_02=questions[i]
        question_send_03=answers[i]

        print("value of I is",i)    
       
        if i>len(questions):

            hardness=request.form["hardness"]
            if hardness=="0":
                score_easy+=(1/len(questions))*100
            elif hardness=="1":
                score_med+=(1/len(questions))*100
            elif hardness=="2":
                score_med+=(1/len(questions))*100
            
            data_update=DataStore.query.filter_by(Email_id=user_name,Deck=deck_name).first()
            data_update.Score=int(score_easy)
            data_update.Num_cards=len(questions)
            data_update.Last_visited=str(time.strftime("%d/%m/%Y"))
            db.session.commit()
            return redirect(f"/decks.html/{user_name}")
        
        hardness=request.form["hardness"]
        if hardness=="0":
            score_easy+=(1/len(questions))*100
        elif hardness=="1":
            score_med+=(1/len(questions))*100
        elif hardness=="2":
            score_med+=(1/len(questions))*100

        elif hardness=="10":
            print("redir called")

            data_update=DataStore.query.filter_by(Email_id=user_name,Deck=deck_name).first()
            data_update.Score=int(score_easy)
            data_update.Num_cards=len(questions)
            data_update.Last_visited=str(time.strftime("%d/%m/%Y"))
            db.session.commit()

            return redirect(f"/decks.html/{user_name}")
        return render_template("Practice.html",question_01=question_send_01,question_02=question_send_02,question_03=question_send_03,user_name=user_name,deck_name=deck_name,score_easy=int(score_easy),score_med=int(score_med),score_hard=int(score_hard),index_value=int(index_value))

        
   
@app.route("/Exammode.html/<user_name>/<deck_name>/<index_value>/<score>",methods=["GET","POST"])

def Exam_mode(user_name,deck_name,index_value,score):
    
    questions=[]
    answers=[]
    score_easy=int(score)
    score_med=0
    score_hard=0
    i=int(index_value)

    [questions.append(x.Question) for x in FlashcardStore.query.filter_by(Deck_name=deck_name).all()]
    [answers.append(x.Answer) for x in FlashcardStore.query.filter_by(Deck_name=deck_name).all()]
    
    print("Printing exam questions",questions)
    if request.method=="GET":
            question_send_01=0
            question_send_02=questions[0]
            question_send_03=answers[0]
            return render_template("Exammode.html",question_01=question_send_01,question_02=question_send_02,question_03=question_send_03,user_name=user_name,deck_name=deck_name,score_easy=int(score_easy),score_med=score_med,score_hard=score_hard,index_value=int(index_value))
    
    if request.method=="POST":
        
        if i==len(questions):

            hardness=request.form["hardness"]
            if hardness=="0":
               score_easy+=(1/len(questions))*100
            elif hardness=="1":
               score_med+=(1/len(questions))*100
            elif hardness=="2":
               score_med+=(1/len(questions))*100  
            return redirect(f"/decks.html/{user_name}")

        
        question_send_01=i
        question_send_02=questions[i]
        question_send_03=answers[i]

        print("value of I is",i)    
       
        hardness=request.form["hardness"]
        if hardness=="0":
            score_easy+=(1/len(questions))*100
        elif hardness=="1":
            score_med+=(1/len(questions))*100
        elif hardness=="2":
            score_med+=(1/len(questions))*100

        elif hardness=="10":
            print("redir called")
           
            return redirect(f"/decks.html/{user_name}")
        return render_template("Exammode.html",question_01=question_send_01,question_02=question_send_02,question_03=question_send_03,user_name=user_name,deck_name=deck_name,score_easy=int(score_easy),score_med=score_med,score_hard=score_hard,index_value=int(index_value))
    
    return("Sucess")  
      
#--------------------------------------------------------------------------------------------------------------
#API

class AdminAPI(Resource): 
    
    def get(self,idval):
        print("In AdminApi GET Method")
        
        user_name_pass=[]
        deck_name_pass=[]
        nc=[]
        Num_count=0
        
        [user_name_pass.append(x.Email_id) for x in DataStore.query.all()]
        [deck_name_pass.append(x.Deck) for x in DataStore.query.all()]
        [nc.append(int(x.Num_cards)) for x in DataStore.query.all()]
        
        for i in range(len(nc)):
            Num_count+=nc[i]


        final_user=[]
        for x in user_name_pass:
            if x in final_user:
                pass
            else:
                final_user.append(x)

        print(deck_name_pass)
        print(final_user)
       
        print(Num_count)
        if idval==0:
            return("Admin login")

        if idval ==1272345243:
            return (deck_name_pass)
        if idval ==1285524235:
            return (final_user)
        if idval==12924354345:
            return (Num_count)
        return (user_name_pass)

api.add_resource(AdminAPI,'/api/AdminApi/<int:idval>')

if __name__=="__main__":
    app.run(
        host='0.0.0.0',
        debug=False,
        port=8080
    )



