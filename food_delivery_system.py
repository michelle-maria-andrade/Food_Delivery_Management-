'''FOOD DELIVERY SERVICES'''
import mysql.connector as con
import time
from prettytable import PrettyTable as table

def main():
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\n\n\t\t\t\t")
    str="\t\t\t\t\t\t\t\tFOOD DELIVERY SYSTEM"
    print("\n\n\n\n\n\n\n\t\t ")
    for i in range(len(str)):
        print(str[i],"\a",end='')
        time.sleep(0.5)
    print("\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\t\t\t  PRESENTED BY MICHELLE")
    time.sleep(3)
    print("\n"+'῁'*104)
    print()
    print("\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\t\t\t\tWELCOME TO ANURODH")
    print("\n\n\n\n\n\n")
    print("\n"+'῁'*104)
    input("\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\t\tPress any key to continue........")
    users()
    
    
def users():
    """This function allows users to login and register"""
    mycon=con.connect(host="localhost",user="root",password="carmel",database="anurodh",auth_plugin='caching_sha2_password')
    mycursor=mycon.cursor()
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\n\n\t\t\t\t")
    heading()
    print("\n\n\n\n"+"\t"*13+"HOME\n" + "_" *104)
    print("\n\n\t\t ")
    print("\n"+"\t"*12+"(L) LOGIN"+"\n"+"\t"*12+"(R) REGISTER"+"\n"+"\t"*12+"(E) EXIT\n\n\n" + "_" *104)
    ch=input("\n\t\t\t\t\t\t\t\t\t Would you like to login or register:")
    if ch.upper()=="L":
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n\t\t\t\t")
        heading()
        print("\n\n\n\n"+"\t"*13+"LOGIN\n" + "_" *104)
        print("\n\n\n")
        print("\n"+"\t"*12+"(C) CUSTOMER"+"\n"+"\t"*12+"(R) RESTURANT"+"\n"+"\t"*12+"(E) EXIT\n\n\n" + "_" *104)
        cs=input("\n\t\t\t\t\t\t\t Would you like to sign in as a customer or resturant:")
        global al,ast        
        if cs.upper()=="C":
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            heading()
            print("\n\n\n\n"+"\t"*13+"LOGIN\n" + "_" *104)
            print("\n\n\n\t\t")
            email=input("\t"*10+" Email address :")
            passwd=input("\t"*10+" Password      :")
            sql="select * from customers where email='{}' and psswrd='{}'".format(email,passwd)
            mycursor.execute(sql)
            tr=mycursor.fetchall()
            if tr!=[]:
                al=email
                ast=passwd
                cust(al,ast)
            else:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n")
                print("\n"+'_'*104)
                print("\n\n\n\n"+"\t"*13+"ERROR")
                print("\n"+"\t"*11+"USER DOES NOT EXIST")
                print("\n\n\n"+'_'*104)
                print("\n\n\n"+"\t"*13+"NOTICE")
                print("\n\n\n"+"\t"*4+"  Please try either loging in again with the correct email and password\n"+"\t"*7+"  or try registering using the given email\n\n")
                print("\n"+'_'*104)
                input("\n"+"\t"*9+ "    Press any key to continue....")
                users()
                        
        elif cs.upper()=="R":
            heading()
            print("\n\n\n\n"+"\t"*13+"LOGIN\n" + "_" *104)
            print("\n\n\n\t\t")
            email=input("\t"*10+" Email address :")
            passwd=input("\t"*10+" Password      :")
            sql="select * from resturants where email='{}' and psswrd='{}'".format(email,passwd)
            mycursor.execute(sql)
            tr=mycursor.fetchall()
            if tr!=[]:
                al=email
                ast=passwd
                rest(al,ast)
            else:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n")
                print("\n"+'_'*104)
                print("\n\n\n\n"+"\t"*13+"ERROR")
                print("\n"+"\t"*10+" RESTURANT DOES NOT EXIST")
                print("\n\n\n"+'_'*104)
                print("\n\n\n"+"\t"*13+"NOTICE")
                print("\n\n\n"+"\t"*4+"  Please try either loging in again with the correct email and password\n"+"\t"*7+"  or try registering using the given email\n\n")
                print("\n"+'_'*104)
                input("\n"+"\t"*9+ "    Press any key to continue....")
                users()
                
        elif cs.upper()=="E": 
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
            print("\n\n\n\t\t ")
        else:
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n")
            print("\n"+'_'*104)
            print("\n\n\n\n"+"\t"*13+"ERROR")
            print("\n"+"\t"*12+"INVALID OPTION")
            print("\n\n\n"+'_'*104)
            users()
        
    elif ch.upper()=="R":
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n\t\t\t\t")
        heading()
        print("\n\n\n\n"+"\t"*12+"REGISTRATION\n" + "_" *104)
        print("\n\n\n\t\t ")
        print("\n"+"\t"*12+"(C) CUSTOMER"+"\n"+"\t"*12+"(R) RESTURANT"+"\n"+"\t"*12+"(E) EXIT\n\n\n" + "_" *104)
        cs=input("\n\t\t\t\t\t\t\t Would you like to sign in as a customer or resturant:")
        
        if cs.upper()=="C":
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            heading()
            print("\n\n\n\n"+"\t"*12+"REGISTRATION\n" + "_" *104)
            print("\n\n\n\t\t")
            name=input("\t"*5+"User name                      :")
            no=int(input("\t"*5+"Phone number                   :"))
            email=input("\t"*5+"Email address                  :")
            del_add=input("\t"*5+"Address (Block, Street, City)  :")
            passwd=input("\t"*5+"Password                       :")
            sql="insert into customers (c_name,no, email,del_add, psswrd) values (%s,%s,%s,%s,%s)"
            val=(name,no,email,del_add,passwd)
            mycursor.execute(sql,val)
            mycon.commit()
            print("\n"*4+"\t"*11+"Thank you for registering!")
            al=email
            ast=passwd
            cust(al,ast)
                        
        elif cs.upper()=="R":
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            heading()
            print("\n\n\n\n"+"\t"*12+"REGISTRATION\n" + "_" *104)
            print("\n\n\n\t\t")
            name=input("\t"*5+"User name                      :")
            no=int(input("\t"*5+"Phone number                   :"))
            email=input("\t"*5+"Email address                  :")
            pick_add=input("\t"*5+"Address (Block, Street, City)  :")
            passwd=input("\t"*5+"Password                       :")
            sql="insert into resturants (r_name,no, email,pick_add, psswrd) values (%s,%s,%s,%s,%s)"
            val=(name,no,email,pick_add,passwd)
            mycursor.execute(sql,val)
            mycon.commit()
            print("\t"*10+"Thank you for registering!")
            al=email
            ast=passwd
            na=name
            men(al,ast,na)
            
        elif cs.upper()=="E":
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
            print("\n\n\n\t\t ")
   
    elif ch.upper()=="E":       
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
            print("\n\n\n\t\t ")       
    
    else:
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n")
        print("\n"+'_'*104)
        print("\n\n\n\n"+"\t"*13+"ERROR")
        print("\n"+"\t"*12+"INVALID OPTION")
        print("\n\n\n"+'_'*104)
        users()
    
    mycursor.close()
    mycon.close()
    
    
def men(a,b,c)  :   
    """This function is used to create menus for newly registered resturants"""
    mycon=con.connect(host="localhost",user="root",password="carmel",database="anurodh",auth_plugin='caching_sha2_password')
    mycursor=mycon.cursor()
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\n\n\t\t\t\t")
    heading()
    print("\n\n\n\n"+"\t"*11+"WELCOME TO ANURODH")
    print("\n\n\n\t\t ")
    na=c
    ch=na.replace(" ","")+"_menu"
    sql="create table "+ch+" (item_id integer primary key auto_increment,class varchar(45) not null,item_name varchar(45) not null,description varchar(100),price float(6, 2) not null)"
    mycursor.execute(sql)
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\t\t\t\t")
    print("\n\n"+"\t"*10+" CREATE YOUR MENU",na.upper())
    print("\n\n\n\t\t ")
    while True:
        print("\t"*8+"Please insert a food item into your menu!")
        while True:
            cl=input("\n"+"\t"*2+"Class (Appertizer (A)/ Main (M)/ Dessert (D)/ Drink (W)): ")
            if cl.lower()=="a":
                cl="Appertizer"
                break
            elif cl.lower()=="m":
                cl="Main"
                break
            elif cl.lower()=="d":
                cl="Dessert"
                break
            elif cl.lower()=="w":
                cl="Drink"
                break
            else:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n")
                print("\n"+'_'*104)
                print("\n\n\n\n"+"\t"*13+"ERROR")
                print("\n"+"\t"*12+"INVALID CLASS")
                print("\n\n\n"+'_'*104)
            
        it_n=input("\t"*2+"Item Name                                               :")
        des=input("\t"*2+"Description (100 char lim)                              :")
        while len(des)>100:
            print("\n"+"\t"*7+"Error: please limit item description to 100 characters")
            des=input("\t"*2+"Description (100 char lim)                              :")
        pri=float(input("\t"*2+"Price                                                   :"))
        sql="insert into "+ch+" (class, item_name,description,price) values ('{}','{}','{}',{})".format(cl,it_n,des,pri)
        mycursor.execute(sql)
        mycon.commit()
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\t\t\t\t")
        ans=input("\n"*3+"\t"*7+"Would you like to insert another item (y/n):")
        print("\n\n\n\t\t ")
        if ans.lower()=="n":
            print("\n\n\t\t\t\t")
            print("\n"*3+"\t"*9+"YOUR MENU HAS BEEN CREATED ")
            print("\n\n\n\t\t ")
            break
    print("\n"+"\t"*12+"(L) LOGIN"+"\n"+"\t"*12+"(R) RESTURANT DASHBOARD"+"\n"+"\t"*12+"(E) EXIT\n\n\n" + "_" *104)

    input_1 = input("\n"+"\t"*12+"Enter action: ").upper() 
    if (input_1.lower() == 'l'):
        print("\n" * 10)
        users()
        
    
    if (input_1.lower() == 'r'):
        print("\n" * 10)
        rest(a,b)
       
    if (input_1.lower() == 'e'):
        print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
        print("\n" * 10)
    mycursor.close()
    mycon.close()   
    
            
def cust(al,ast):
    """This function serves as the main UI for customers"""
    mycon=con.connect(host="localhost",user="root",password="carmel",database="anurodh",auth_plugin='caching_sha2_password')
    mycursor=mycon.cursor()
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\n\n\t\t\t\t")
    heading()
    print("\n\n\n\n"+"\t"*12+"WELCOME BACK\n"+ "_" * 104)
    print("\n"*3+"\t"*9+"(L) Look at previous order history"+"\n"+"\t"*9+"(O) Order from resturants\n\n\n"+ "_" *104)
    ch=input("\n"+"\t"*12+"Enter action: ").upper()
    sql="select acc_id from customers where email='{}'".format(al)
    mycursor.execute(sql)
    myvar=mycursor.fetchone()
    var=myvar[0]
    sql="select ord_id,food,total,r_name,date from orders where acc_id={}".format(var)
    mycursor.execute(sql)
    mydata=mycursor.fetchall()
    p=1
    if ch.lower()=="l":
        while True:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n\t\t\t\t")
                print("\n"*3+"*" * 46 + "ORDER HISTORY" + "*" * 45)
                k=table(['NO','ORDER','TOTAL','RESTURANT','DATE'])
                p=1
                if mydata == []:
                    print("\n\n\n\n"+"\t"*10+"    NO ORDER HISTORY")
                    break
                else:
                    for x in mydata:
                        ne=x[0]
                        res=x[2]
                        da=x[3]
                        pri=x[1].replace(",","\n")
                        ques=x[4]
                        k.add_row([ne,pri,res,da,ques])
                        p+=1
                    print(k)
                break
    elif ch.lower()=="o":
        resturant_list()
    else:
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n")
        print("\n"+'_'*104)
        print("\n\n\n\n"+"\t"*13+"ERROR")
        print("\n"+"\t"*12+"INVALID OPTION")
        print("\n\n\n"+'_'*104)
        cust(al,ast)
        
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\n\n\t\t\t\t")  
    print("\n"+"\t"*12+"(L) LOGIN"+"\n"+"\t"*12+"(D) DASHBOARD"+"\n"+"\t"*12+"(E) EXIT\n\n\n" + "_" *104)
    
    input_1 = input("\n"+"\t"*12+"Enter action: ").upper() 
    if (input_1.lower() == 'l'):
        print("\n" * 10)
        users()
         
    if (input_1.lower() == 'd'):
        print("\n" * 10)
        cust(al,ast)
        
    if (input_1.lower() == 'e'):
        print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
        print("\n" * 10)
    mycursor.close()
    mycon.close()
    
        
        
def rest(al,ast):
    """This fucntions serves as the main UI for resturants"""
    mycon=con.connect(host="localhost",user="root",password="carmel",database="anurodh",auth_plugin='caching_sha2_password')
    mycursor=mycon.cursor()
    global name
    sql="select r_name from resturants where email='{}'".format(al)
    mycursor.execute(sql)
    myvar=mycursor.fetchone()
    name=""
    for x in myvar:
        name=name+x
        
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\n\n\t\t\t\t")
    heading()
    print("\n\n\n\n"+"\t"*12+"WELCOME BACK\n"+ "_" * 104)
    print("\n\n\n ") 
    print("\n"+"\t"*12+"(C) CURRENT ORDERS"+"\n"+"\t"*12+"(P) PREVIOUS ORDERS"+"\n"+"\t"*12+"(U) UPDATE MENU\n\n\n" + "_" *104)
    
    ch=input("\n"+"\t"*12+"Enter action: ")
    
    if ch.lower()=='c':
        sql="select r_name from resturants where email='{}'".format(al)
        mycursor.execute(sql)
        myvar=mycursor.fetchone()
        var=myvar[0]
        sql="select ord_id,food,total,date from orders where r_name='{}' and status='incomplete'".format(var)
        mycursor.execute(sql)
        mydata=mycursor.fetchall()
        oh=[]
        q=True
        while q==True:    
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n\t\t\t\t")
                print("\n"*3+"*" * 42 + "CURRENT ORDERS" + "*" * 43)
                k=table(['NO','ORDER','TOTAL','DATE'])
                if mydata == []:
                    print("\n\n\n\n"+"\t"*10+"    NO CURRENT ORDERS")
                    q=False
                    break
                else:
                    for x in mydata:
                        orde=x[0]
                        ne=x[1].replace(",","\n")
                        pri=x[2]
                        dat=x[3]
                        k.add_row([orde,ne,pri,dat])
                        oh.append(orde)
                    print(k)
                    break
            
        while q==True:
            ch=input("\n"*3+"\t"*7+ "Would you like to mark an order as complete (y/n):")
            if ch.lower()=="y":
                cu=int(input("Order ID:"))
                if cu in oh:
                    sql="update orders set status='complete' where ord_id={}".format(cu)
                    mycursor.execute(sql)
                    mycon.commit()
            ans=input("\n"*3+"\t"*9+ "Would you like to continue (y/n):")
            if ans.lower()=="n":
                break
        print("\n"+"\t"*12+"(L) LOGIN"+"\n"+"\t"*12+"(R) RESTURANT DASHBOARD"+"\n"+"\t"*12+"(E) EXIT\n\n\n" + "_" *104)


        input_1 = input("\n"+"\t"*12+"Enter action: ").upper() 
        if (input_1.lower() == 'l'):
            print("\n" * 10)
            users()
             
        if (input_1.lower() == 'r'):
            print("\n" * 10)
            rest(al,ast)
            
        if (input_1.lower() == 'e'):
            print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
            print("\n" * 10)
           
    elif ch.lower()=='p':
        sql="select r_name from resturants where email='{}'".format(al)
        mycursor.execute(sql)
        myvar=mycursor.fetchone()
        var=myvar[0]
        sql="select ord_id,food,total,date from orders where r_name='{}' and status='complete'".format(var)
        mycursor.execute(sql)
        mydata=mycursor.fetchall()
        while True:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n\t\t\t\t")
                print("\n"*3+"*" * 42 + "PREVIOUS ORDERS" + "*" * 42)
                k=table(['NO','ORDER','TOTAL','DATE'])
                if mydata == []:
                    print("\n\n\n\n"+"\t"*10+"    NO CURRENT ORDERS")
                    break
                else:
                    for x in mydata:
                        orde=x[0]
                        ne=x[1].replace(",","\n")
                        pri=x[2]
                        dat=x[3]
                        k.add_row([orde,ne,pri,dat])
                    print(k)
                break
        print("\n"+"\t"*12+"(L) LOGIN"+"\n"+"\t"*12+"(R) RESTURANT DASHBOARD"+"\n"+"\t"*12+"(E) EXIT\n\n\n" + "_" *104)    

        input_1 = input("\n"+"\t"*12+"Enter action: ").upper() 
        if (input_1.lower() == 'l'):
            print("\n" * 10)
            users()
             
        if (input_1.lower() == 'r'):
            print("\n" * 10)
            rest(al,ast)
            
        if (input_1.lower() == 'e'):
            print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
            print("\n" * 10)
            
    elif ch.lower()=='u':
        n_name=name.replace(" ","")+"_menu"
        rest_update(n_name)
         
    else:
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n")
        print("\n"+'_'*104)
        print("\n\n\n\n"+"\t"*13+"ERROR")
        print("\n"+"\t"*12+"INVALID OPTION")
        print("\n\n\n"+'_'*104)
        rest(al,ast)
    mycursor.close()
    mycon.close()
    

def rest_update(a):
     """This function allows restaurants to update their menu"""
     mycon=con.connect(host="localhost",user="root",password="carmel",database="anurodh",auth_plugin='caching_sha2_password')
     mycursor=mycon.cursor()
   
     print("\033[35cm ")
     print("\033")
     print("\n\n\n\n\n\t\t\t\t")
     print("\n\n\n\n"+"\t"*12+"UPDATE MENU\n"+ "_" * 104)
     print("\n\n\n\t\t ")
     print("\n"+"\t"*11+"(U) UPDATE A DISH"+"\n"+"\t"*11+"(A) ADD A DISH"+"\n"+"\t"*11+"(D) DELETE A DISH\n\n\n" + "_" *104)

     ch=input("\n"+"\t"*12+"Enter action: ")
    
     if ch.lower()=='u':
        ans="y"
        while ans.lower()=="y":
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            sql="select item_name, class,price from "+a+" order by class"
            mycursor.execute(sql)
            mydata=mycursor.fetchall()
            count=0
            while True:
                    print("*" * 50 + "MENU" + "*" * 50,"\n")
                    k=table(['NO','NAME','CLASS','PRICE'])
                    p=1
                    for x in mydata:
                        ne=x[0]
                        des=x[1]
                        pri=x[2]
                        k.add_row([p,des,ne,pri])
                        p+=1
                        count+=1
                    print(k)
                    break
            n=int(input("\n"*2+"\t"*9+"Which dish would you like to update:"))
            while n>count or n==0:
                print("\n"*2+"\t"*9+"Item number not on menu. Please re-select")
                n=int(input("\n"*2+"\t"*9+"Which dish would you like to update:"))
            na=mydata[n-1][0]
            print("\n"*2+"\t"*9+"What would you like to change about",na)
            print("\n"+"\t"*11+"1. CLASS"+"\n"+"\t"*11+"2. NAME"+"\n"+"\t"*11+"3. DESCRIPTION"+"\n"+"\t"*11+"4. PRICE\n\n\n" + "_" *104)
            cs=int(input("\n"+"\t"*12+"Enter action: "))
            
            if cs==1:
                while True:
                    cl=input("\n"+"\t"*2+"New Class (Appertizer (A)/ Main (M)/ Dessert (D)/ Drink (W)): ")
                    if cl.lower()=="a":
                        cl="Appertizer"
                        break
                    elif cl.lower()=="m":
                        cl="Main"
                        break
                    elif cl.lower()=="d":
                        cl="Dessert"
                        break
                    elif cl.lower()=="w":
                        cl="Drink"
                        break
                    else:
                        print("\033[35cm ")
                        print("\033")
                        print("\n\n\n\n\n")
                        print("\n"+'_'*104)
                        print("\n\n\n\n"+"\t"*13+"ERROR")
                        print("\n"+"\t"*12+"INVALID CLASS")
                        print("\n\n\n"+'_'*104)

                sql="update "+a+" set class='{}' where item_name='{}'".format(cl,na)
                mycursor.execute(sql)
                mycon.commit()
                
            elif cs==2:
                dnam=input("\t"*2+"New Item Name                                               :")
                sql="update "+a+" set item_name='{}' where item_name='{}' ".format(dnam,na)
                mycursor.execute(sql)
                mycon.commit()
                
            elif cs==3:
                des=input("\t"*2+"New Description (100 char lim)                              :")
                sql="update "+a+" set description='{}' where item_name='{}'".format(des,na)
                mycursor.execute(sql)
                mycon.commit()
                
            elif cs==4:
                price=float(input("\t"*2+"New Price                                                   :"))
                sql="update "+a+" set price='{}' where item_name='{}'".format(price,na)
                mycursor.execute(sql)
                mycon.commit()
                
            else:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n")
                print("\n"+'_'*104)
                print("\n\n\n\n"+"\t"*13+"ERROR")
                print("\n"+"\t"*12+"INVALID CLASS")
                print("\n\n\n"+'_'*104)
                
            ans=input("\n"+"\t"*7+"Would you like to continue updating (y/n):")
            if ans.lower()=='n':
                print("\033[35cm ")
                print("\033")
                print("\n\n\n"+'_'*104)
                print("\n\n\n\n"+"\t"*13+"UPDATE SUCCESSFUL")
                print("\n\n\n"+'_'*104)
                print("\n\n\n\t\t ")
                break
            
     elif ch.lower()=='a':
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n\t\t\t\t")
        
        while True:
            cl=input("\t"*2+" Class (Appertizer (A)/ Main (M)/ Dessert (D)/ Drink (W)): ")
            if cl.lower()=="a":
                cl="Appertizer"
                break
            elif cl.lower()=="m":
                cl="Main"
                break
            elif cl.lower()=="d":
                cl="Dessert"
                break
            elif cl.lower()=="w":
                cl="Drink"
                break
            else:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n")
                print("\n"+'_'*104)
                print("\n\n\n\n"+"\t"*13+"ERROR")
                print("\n"+"\t"*12+"INVALID CLASS")
                print("\n\n\n"+'_'*104)
                
        dnam=input("\t"*2+" Item Name                                               :")
        des=input("\t"*2+" Description (100 char lim)                              :")
        while len(des)>100:
            print("\n"+"\t"*7+"Error: please limit item description to 100 characters")
            des=input("\t"*2+" Description (100 char lim)                              :")
        price=float(input("\t"*2+" Price                                                   :"))
        sql="insert into "+a+"(class, item_name,description,price) values ('{}','{}','{}',{})".format(cl,dnam,des,price)
        mycursor.execute(sql)
        mycon.commit()
        ans=input("\n"+"\t"*10+"Press any key to continue")
     elif ch.lower()=='d':
        ans="y"
        while ans.lower()=="y":
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            sql="select item_name, class,price from "+a+" order by class"
            mycursor.execute(sql)
            mydata=mycursor.fetchall()
            count=0
            heading()
            while True:
                    print("*" * 50 + "MENU" + "*" * 50,"\n")
                    k=table(['NO','NAME','CLASS','PRICE'])
                    p=1
                    for x in mydata:
                        ne=x[0]
                        des=x[1]
                        pri=x[2]
                        k.add_row([p,des,ne,pri])
                        p+=1
                        count+=1
                    print(k)
                    break
            n=int(input("\n"*2+"\t"*9+"Which dish would you like to delete:"))
            while n>count or n==0:
                print("\n"*2+"\t"*9+"Item nunmber not on menu. Please re-select")
                n=int(input("\n"*2+"\t"*9+"Which dish would you like to delete:"))
            na=mydata[n-1][0]
            sql="delete from "+a+" where item_name='{}'".format(na)
            mycursor.execute(sql)
            mycon.commit()
            ans=input("\n"+"\t"*7+"Would you like to continue deleting (y/n):")
            if ans.lower()=='n':
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n\t\t\t\t")
                print("\n\n\n\n"+"\t"*13+"DELETION SUCCESSFUL")
                print("\n\n\n\t\t ",end='')
                break
     
     else:
         print("\033[35cm ")
         print("\033")
         print("\n\n\n\n\n")
         print("\n"+'_'*104)
         print("\n\n\n\n"+"\t"*13+"ERROR")
         print("\n"+"\t"*12+"INVALID CLASS")
         print("\n\n\n"+'_'*104)
         
     print("\n"+"\t"*11+"(L) LOGIN "+"\n"+"\t"*11+"(R) RESTURANT DASHBOARD"+"\n"+"\t"*11+"(E) EXIT\n\n\n" + "_" *104)   
     

     input_1 = input("\n"+"\t"*12+"Enter action: ").upper() 
     if (input_1.lower() == 'l'):
        print("\n" * 10)
        users()
         
     if (input_1.lower() == 'r'):
        print("\n" * 10)
        rest(al,ast)
        
     if (input_1.lower() == 'e'):
        print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
        print("\n" * 10)
     
     mycursor.close()
     mycon.close()
    
        
def resturant_list():
    """This function displays all the resturants currently registered in the app for users choice"""
    mycon=con.connect(host="localhost",user="root",password="carmel",database="anurodh",auth_plugin='caching_sha2_password')
    mycursor=mycon.cursor()
    global n_res 
    global restu   
    sql= "select r_name from resturants"
    mycursor.execute(sql)
    mydata=mycursor.fetchall()
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\t\t\t\t")
    heading()
    print("\n"+"\t"*12+"RESTURANTS"+"\n\n")
    h=1
    g=[]
    for x in mydata:
        for y in x:
            print ("\t"*10,h,".",y.upper(),'\n')
            h+=1
            g.append(y)
    ch=int(input("\n"+"\t"*7+"Which resturant would you like to order from today:"))
    if ch<=len(g) and ch>=0:
        restu=g[ch-1]
        n_res=restu.replace(" ","")+"_menu"
        a="no"
        menu(n_res,restu,a)
    else:
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n")
        print("\n"+'_'*104)
        print("\n\n\n\n"+"\t"*13+"ERROR")
        print("\n"+"\t"*12+"INVALID OPTION")
        print("\n\n\n"+'_'*104)
        resturant_list()
    mycursor.close()
    mycon.close()
    
   
def menu(a,c,ok):
    """This function displays the menu of a particular resturant"""
    mycon=con.connect(host="localhost",user="root",password="carmel",database="anurodh",auth_plugin='caching_sha2_password')
    mycursor=mycon.cursor(buffered=True)
    global gh
    global b
    b=c
    gh=a
    sql="select item_name, class,price from "+a+" order by class"
    mycursor.execute(sql)
    mydata=mycursor.fetchall()
    count=0
    while True:
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            heading()
            print("\n"+"\t"*12+"MENU - "+b.upper())
            sql="select pick_add from resturants where r_name="+'"'+c+'"'
            mycursor.execute(sql)
            var=mycursor.fetchall()
            addr=var[0][0]
            print("\n"+"\t"*10+ addr.upper() +" "+"_" *104)
            k=table(['NO','CLASS','NAME','PRICE'])
            p=1
            for x in mydata:
                ne=x[0].upper()
                des=x[1].upper()
                pri=x[2]
                k.add_row([p,des,ne,pri])
                p+=1
                count+=1
            print(k)
            break
    ans=input("\n"+"\t"*9+"Would you like to order (y/n):")
    if ans.lower()=="y":
        sql="select * from cart"
        mycursor.execute(sql)
        mydat=mycursor.fetchall()
        
        if mydat!=[] and ok=="no":
            print("\n"+"\t"*13+"NOTICE\n"+"_"*104)
            nas=input("\n"+"\t"*6+"Previous order pending.Would you like to start a new cart(y/n):")
            if nas.lower()=="y":
                sql="delete from cart"
                mycursor.execute(sql)
                while True:
                    n=int(input("\t\t Item No. :"))
                    while n>count or n==0:
                        print("\033[35cm ")
                        print("\033")
                        print("\n\n\n\n\n")
                        print("\n"+'_'*104)
                        print("\n\n\n\n"+"\t"*13+"ERROR")
                        print("\n"+"\t"*12+"INVALID OPTION")
                        print("\n\n\n"+'_'*104)
                        
                        n=int(input("\n\t\t Item No. :"))
                    qua=int(input("\t\t Quantity :"))
                    pr=mydata[n-1][2]
                    ry=mydata[n-1][0]
                    it="select item_id from "+a+" where item_name='{}'".format(ry)
                    mycursor.execute(it)
                    it1=mycursor.fetchall()
                    sql="insert into cart values({},'{}',{},{})".format(it1[0][0],ry,qua,pr)
                    mycursor.execute(sql)
                    mycon.commit()
                    ans=input("\n"+"\t"*8+"Would you like to continue ordering (y/n):")
                    if ans.lower()=="n":
                        break
                else:
                    resturant_list()
                    
        elif mydat!=[] and ok=="yes":
            while True:
                n=int(input("\n\t\t Item No. :"))
                while n>count or n==0:
                    print("\033[35cm ")
                    print("\033")
                    print("\n\n\n\n\n")
                    print("\n"+'_'*104)
                    print("\n\n\n\n"+"\t"*13+"ERROR")
                    print("\n"+"\t"*12+"INVALID OPTION")
                    print("\n\n\n"+'_'*104)
                    
                    n=int(input("\n\t\t Item No. :"))
                qua=int(input("\t\t Quantity :"))
                pr=mydata[n-1][2]
                ry=mydata[n-1][0]
                it="select item_id from "+a+" where item_name='{}'".format(ry)
                mycursor.execute(it)
                it1=mycursor.fetchall()
                sql="insert into cart values({},'{}',{},{})".format(it1[0][0],ry,qua,pr)
                mycursor.execute(sql)
                mycon.commit()
                ans=input("\n"+"\t"*8+"Would you like to continue ordering (y/n):")
                if ans.lower()=="n":
                    break 
                
        elif mydat==[]:
            while True:
                n=int(input("\n\t\t Item No. :"))
                while n>count or n==0:
                    print("\033[35cm ")
                    print("\033")
                    print("\n\n\n\n\n")
                    print("\n"+'_'*104)
                    print("\n\n\n\n"+"\t"*13+"ERROR")
                    print("\n"+"\t"*12+"INVALID OPTION")
                    print("\n\n\n"+'_'*104)
                    
                    n=int(input("\n\t\t Item No. :"))
                qua=int(input("\t\t Quantity :"))
                pr=mydata[n-1][2]
                ry=mydata[n-1][0]
                it="select item_id from "+a+" where item_name='{}'".format(ry)
                mycursor.execute(it)
                it1=mycursor.fetchall()
                sql="insert into cart values({},'{}',{},{})".format(it1[0][0],ry,qua,pr)
                mycursor.execute(sql)
                mycon.commit()
                ans=input("\n"+"\t"*8+"Would you like to continue ordering (y/n):")
                if ans.lower()=="n":
                    break
    elif ans.lower()=="n":
        resturant_list()
        
    print("\n"+"\t"*11+"(C)CART "+"\n"+"\t"*11+"(R)RESTURANT LIST"+"\n"+"\t"*11+"(E)EXIT\n\n\n" + "_" *104)    

    cl=input("\n"+"\t"*12+"Enter action: ")
    if cl.lower()=="c":
        cart(gh)
    elif cl.lower()=="r":
        print("\n"+"\t"*10+"  Current cart items deleted")
        sql="delete from cart"
        mycursor.execute(sql)
        mycon.commit()
        resturant_list()
    elif cl.lower()=="e":
        print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
    else:
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n")
        print("\n"+'_'*104)
        print("\n\n\n\n"+"\t"*13+"ERROR")
        print("\n"+"\t"*12+"INVALID OPTION")
        print("\n\n\n"+'_'*104)
        menu(gh,b)
        
         
        
def cart(z):
    """This function displays the cart of a customer"""
    mycon=con.connect(host="localhost",user="root",password="carmel",database="anurodh",auth_plugin='caching_sha2_password')
    mycursor=mycon.cursor()
    sql="select item_name, quantitiy,price from cart"
    mycursor.execute(sql)
    mydata=mycursor.fetchall()
    global count
    global foo
    foo=" "
    count=0
    while True:
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            print("*" * 50 + "CART" + "*" * 50)
            k=table(['NO','NAME','QUANTITY','PRICE'])
            p=1
            if mydata == []:
                print("\n\n\n\n"+"\t"*10+"    CART EMPTY")
                print("\n"+"\t"*11+"(C)CHECKOUT "+"\n"+"\t"*11+"(R)RESTURANT LIST\n\n\n" + "_" *104) 
                cl=input("\n"+"\t"*12+"Enter action: ")
                if cl.lower()=="c":
                    for x in mydata:
                        foo+=x[0]+" x "+str(x[1])+","
                    payment()
                elif cl.lower()=="r":
                    resturant_list()
                else:
                    print("\033[35cm ")
                    print("\033")
                    print("\n\n\n\n\n")
                    print("\n"+'_'*104)
                    print("\n\n\n\n"+"\t"*13+"ERROR")
                    print("\n"+"\t"*12+"INVALID OPTION")
                    print("\n\n\n"+'_'*104)
                break
            else:
                for x in mydata:
                    ne=x[0].upper()
                    qua=x[1]
                    pri=x[2]
                    k.add_row([p,ne,qua,pri])
                    p+=1
                    count+=qua*pri
                print(k)
                print("\n"+"\t"*8+"TOTAL:",count,"\n"+"_" * 104)
                print("\n"+"\t"*11+"(C)CHECKOUT "+"\n"+"\t"*11+"(U)UPDATE CART"+"\n"+"\t"*11+"(R)RESTURANT LIST\n\n\n" + "_" *104) 
                cl=input("\n"+"\t"*12+"Enter action: ")
                if cl.lower()=="c":
                    for x in mydata:
                        foo+=x[0]+" x "+str(x[1])+","
                    payment()
                elif cl.lower()=="u":
                    edit_cart()
                elif cl.lower()=="r":
                    resturant_list()
                else:
                    print("\033[35cm ")
                    print("\033")
                    print("\n\n\n\n\n")
                    print("\n"+'_'*104)
                    print("\n\n\n\n"+"\t"*13+"ERROR")
                    print("\n"+"\t"*12+"INVALID OPTION")
                    print("\n\n\n"+'_'*104)
                
            break
        
    
def edit_cart():
    '''This function allows customers to edit their cart'''
    mycon=con.connect(host='localhost',user='root',password='carmel',database='anurodh')
    mycursor=mycon.cursor()
    sql='select item_name, quantitiy, price from cart'
    mycursor.execute(sql)
    mydata=mycursor.fetchall()
    global foo
    global count
    foo=" "
    count=0
    while True:
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            print("*" * 50 + "CART" + "*" * 50)
            k=table(['NO','NAME','QUANTITY','PRICE'])
            p=1
            for x in mydata:
                ne=x[0].upper()
                qua=x[1]
                pri=x[2]
                k.add_row([p,ne,qua,pri])
                p+=1
                count+=qua*pri
            print(k)
            break
    print("\n"+"\t"*8+"TOTAL:",count ,"\n"+"_" * 104)

    print("\n"+"\t"*11+"(A)ADD ITEM "+"\n"+"\t"*11+"(D)DELETE ITEM"+"\n"+"\t"*11+"(E)EDIT QUANTITY\n\n\n" + "_" *104)

    ch=input("\n"+"\t"*12+"Enter action: ")
    if ch.lower()=="a":
        a="yes"
        menu(n_res,restu,a)
    elif ch.lower()=="d":
        ans="y"
        while ans.lower()=="y":
            em=int(input("\n\t\t Item No. :"))
            while em >len(mydata) or em==0:
                print("\n\t\t Item no does not exist")
                em=int(input("\t\t Item No. :"))
            nm=mydata[em-1]
            sql="delete from cart where item_name='{}'".format(nm[0])
            mycursor.execute(sql)
            mycon.commit()
            ans=input("\n"+"\t"*8+"Would you like to delete another item (y/n):")
            if ans.lower()=='n':
                break
            
        sql='select item_name, quantitiy, price from cart'
        mycursor.execute(sql)
        mydata=mycursor.fetchall()
        while True:
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            print("*" * 50 + "CART" + "*" * 50)
            k=table(['NO','NAME','QUANTITY','PRICE'])
            p=1
            count=0
            for x in mydata:
                ne=x[0].upper()
                qua=x[1]
                pri=x[2]
                k.add_row([p,ne,qua,pri])
                p+=1
                count+=qua*pri
            print(k)
            break
        print("\n"+"\t"*8+"TOTAL:",count ,"\n"+"_" * 104)
        print("\n"+"\t"*11+"(C)CHECKOUT "+"\n"+"\t"*11+"(U)UPDATE CART"+"\n"+"\t"*11+"(R)RESTURANT LIST\n\n\n" + "_" *104)
 
        cl=input("\n"+"\t"*12+"Enter action: ")
        if cl.lower()=="c":
            for x in mydata:
                foo+=x[0]+" x "+str(x[1])+"\n"
            payment()
        elif cl.lower()=="u":
            edit_cart()
        elif cl.lower()=="r":
            resturant_list()
        else:
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n")
            print("\n"+'_'*104)
            print("\n\n\n\n"+"\t"*13+"ERROR")
            print("\n"+"\t"*12+"INVALID OPTION")
            print("\n\n\n"+'_'*104)
                
            
    elif ch.lower()=="e":
        ans="y"
        while ans.lower()=="y":
            em=int(input("\n\t\t Item No. :"))
            while em >len(mydata) or em==0:
                print("\n\t\t\t\t\t Item no does not exist")
                em=int(input("\t\t Item No. :"))
            nm=mydata[em-1][0]
            n=int(input("\t\t New Quantity:"))
            sql1="update cart set quantitiy={} where item_name='{}'".format(n,nm)
            mycursor.execute(sql1)
            mycon.commit()
            ans=input("\n"+"\t"*6+"Would you like to edit the quantity of another item (y/n):")
            if ans.lower()=="n":
                print("\n"+"\t"*12+"Quantity Edited")
                break
     
        sql='select item_name, quantitiy, price from cart'
        mycursor.execute(sql)
        mydata=mycursor.fetchall()
        while True:
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n\t\t\t\t")
            print("*" *50 + "CART" + "*" *50)
            k=table(['NO','NAME','QUANTITY','PRICE'])
            p=1
            count=0
            for x in mydata:
                ne=x[0].upper()
                qua=x[1]
                pri=x[2]
                k.add_row([p,ne,qua,pri])
                p+=1
                count+=qua*pri
            print(k)
            break
        print("\n"+"\t"*8+"TOTAL:",count ,"\n"+"_" * 104)
        print("\n"+"\t"*11+"(C)CHECKOUT "+"\n"+"\t"*11+"(U)UPDATE CART"+"\n"+"\t"*11+"(R)RESTURANT LIST\n\n\n" + "_" *104)

        cl=input("\n"+"\t"*12+"Enter action: ")
        if cl.lower()=="c":
            for x in mydata:
                foo+=x[0]+" x "+str(x[1])+"\n"
            payment()
        elif cl.lower()=="u":
            edit_cart()
        elif cl.lower()=="r":
            resturant_list()
        else:
            print("\033[35cm ")
            print("\033")
            print("\n\n\n\n\n")
            print("\n"+'_'*104)
            print("\n\n\n\n"+"\t"*13+"ERROR")
            print("\n"+"\t"*12+"INVALID OPTION")
            print("\n\n\n"+'_'*104)
    mycursor.close()
    mycon.close()


def payment():
    print("\033[35cm ")
    print("\033")
    print("\n\n\n\n\n\t\t\t\t")
    print("\n\n\n\n"+"\t"*13+"PAYMENT\n"+ "_" * 104)
    print("\n\n\n\t\t ")
    print("\n"+"\t"*12+"(C) CREDIT "+"\n"+"\t"*12+"(D) DEBIT"+"\n"+"\t"*12+"(I) IN PERSON\n\n\n" + "_" *104)
    ch=input("\n"+"\t"*11+"Select Payment Method:")
    if ch.lower()=="c":
        ans="y"
        while ans=="y":
            card_no=int(input("\t\t Credit card number :"))
            while len(str(card_no))<16:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n")
                print("\n"+'_'*104)
                print("\n\n\n\n"+"\t"*13+"ERROR")
                print("\n"+"\t"*12+"INVALID CARD NUMBER")
                print("\n\n\n"+'_'*104)
                
                card_no=int(input("\t\t Credit card number :"))
            expiry_date=input("\t\t Expiry date (MM/YY):")
            cvv=int(input("\t\t CVV                :"))
            ans="n"
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n\t\t\t\t")
        print("\n"+"\t"*10+"Your order is being prepared")
        print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
        print("\n\t\t ")
        cart_ord()
        
        
    elif ch.lower()=="d":
        ans="y"
        while ans=="y":
            card_no=int(input("\t\t Debit card number  :"))
            while len(str(card_no))<16:
                print("\033[35cm ")
                print("\033")
                print("\n\n\n\n\n")
                print("\n"+'_'*104)
                print("\n\n\n\n"+"\t"*13+"ERROR")
                print("\n"+"\t"*12+"INVALID CARD")
                print("\n\n\n"+'_'*104)
                
                card_no=int(input("\t\t Debit card number  :"))
            expiry_date=input("\t\t Expiry date (MM/YY):")
            cvv=int(input("\t\t CVV                :"))
            ans="n"
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n\t\t\t\t")
        print("\n"+"\t"*10+"Your order is being prepared")
        print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
        print("\n\n\n\t\t ")
        cart_ord()
        
        
    elif ch.lower()=="i":
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n\t\t\t\t")
        print("\n"+"\t"*10+"Your order is being prepared")
        print("\n\n\n\n\t\t\t\t\t  Thank you for using Anurodh! We hope to see you again soon!")
        print("\n\n\n\t\t ")
        cart_ord()
        
    else:
        print("\033[35cm ")
        print("\033")
        print("\n\n\n\n\n")
        print("\n"+'_'*104)
        print("\n\n\n\n"+"\t"*13+"ERROR")
        print("\n"+"\t"*12+"INVALID CLASS")
        print("\n\n\n"+'_'*104)
        payment()
        
        
def cart_ord():
    '''This function transfers orders of a customer from cart to order table'''
    mycon=con.connect(host='localhost',user='root',password='carmel',database='anurodh')
    mycursor=mycon.cursor()
    global foo
    global count

    sql="select acc_id from customers where email='{}'".format (al)
    mycursor.execute(sql)
    myit=mycursor.fetchall()
    acc=myit[0][0]
    sql="select c_name from customers where acc_id={} ".format(acc)
    mycursor.execute(sql)
    myit=mycursor.fetchall()
    cna=myit[0][0]
    rna=b
    
    sql="insert into orders(acc_id,food,c_name,r_name,total) values({},'{}','{}','{}',{})".format(acc,str(foo),cna,rna,count)
    mycursor.execute(sql)
    mycon.commit()
    foo=[]
    
    sql="delete from cart"
    mycursor.execute(sql)
    mycon.commit()
    
 
def heading():
    print()
    print()
    print("\n"+'҉'*104)
    print("\t"*37+" ANURODH DELIVERY SERVICES")
    print("\t"*37+"25A Al Safa St, Kuwait City") 
    print("\t"*38+" Ph. No. 22276002")
    print("\n"+'҉'*104)
main()
users()
b=""
tot=0
count=0
n_res=""
restu=""
