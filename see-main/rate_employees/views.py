

from django.http import HttpResponse
from django.shortcuts import render, redirect
from rate_employees.models import Employee, Evaluation, Designation, Award,Notification
from . registrationForm import EmployeeRegistration
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, F
from .serializers import AwardSerializer
from django.contrib.auth.decorators import user_passes_test


from django.core.serializers import serialize
import json
from . import petro


# Create your views here.

@login_required(login_url='login')
def home(request):
     current_user=Employee.objects.get(enothi_id=request.user)
     counter=current_user.counter
     context={
            'counter':counter
        }
    
     return render(request,'employees/homePage.html',context)

@login_required(login_url='login')
def employees_info(request):
    employee = Employee.objects.all()
    return render (request, 'employees/evaluation.html', {'emp': employee} )

@login_required(login_url='login')
def mark_employees(request):
    return render (request, 'employees/mark.html')

def registerPage(request):

    if request.user.is_authenticated:
        current_user=Employee.objects.get(enothi_id=request.user)
        counter=current_user.counter
        context={
            'counter':counter
        }
        return redirect('home',context)
    else:

        if request.method == "POST":
            fm = UserCreationForm(request.POST)
            if fm.is_valid():
                fm.save()
                print("this post from registration")
                return redirect('home')
        else:
            fm = UserCreationForm()
        return render(request,'employees/registration.html',{'form': fm})

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else :
                messages.info(request, 'Username or Password is incorrect')

        return render(request,'employees/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def showProfileData(request):
    if request.method == 'POST':
        print("request post")
        print(request.POST)
        fm = EmployeeRegistration(request.POST)

        if fm.is_valid():
            mydata = Employee.objects.filter(enothi_id = request.user)
            if mydata.exists():
    
                myProfileData = Employee.objects.get(enothi_id = request.user)
                #print(" My Objects ",myProfileData[0])
                myProfileData.ename = request.POST['name']
                myProfileData.eemail = request.POST['email']
                myProfileData.empid = request.POST['empid']
                myProfileData.edesignation = request.POST['designation']
                myProfileData.esection = request.POST['section']
                myProfileData.edept = request.POST['department']
                myProfileData.edivision = request.POST['division']
                myProfileData.edirectorate = request.POST['directorate']
                myProfileData.save()
                return redirect('home')

            #print(fm)
            print("This is POST statement")
            print(request.POST['name'])
            name = request.POST['name']
            email = request.POST['email']
            enothi_id = request.user
            empid = request.POST['empid']
            designation = request.POST['designation']
            section = request.POST['section']
            department = request.POST['department']
            division = request.POST['division']
            directorate = request.POST['directorate']

            new_emp = Employee(empid = empid, enothi_id = enothi_id , ename = name, eemail = email, edesignation = designation, edept = department, esection = section, edivision = division, edirectorate = directorate)
            #print(fm.cleaned_data)
            new_emp.save()
            return redirect('home')
        #else if request.POST['enothi_id']:
        else:
            print("not valid enothi_id ",request.user)
            print("enothi_id from post ",request.POST['enothi_id'])
            #print(fm)

    else: 
        fm = EmployeeRegistration()
        fm.initial['enothi_id'] = request.user
        user_id = request.user
        mydata = Employee.objects.filter(enothi_id=request.user).values()
        if mydata.exists():
            print("mydata exists!!")
            print(request.POST)
            fm.initial['name'] = mydata[0]['ename']
            fm.initial['email'] = mydata[0]['eemail']
            fm.initial['empid'] = mydata[0]['empid']
            fm.initial['designation'] = mydata[0]['edesignation']
            fm.initial['section'] = mydata[0]['esection']
            fm.initial['department'] = mydata[0]['edept']
            fm.initial['division'] = mydata[0]['edivision']
            fm.initial['directorate'] = mydata[0]['edirectorate']
            

            designations = Designation.objects.all()
            
            context = {
                'myProfileData': mydata,
                'form': fm,
                'enothi_id':user_id,
                'designationData': designations
                }
            #return HttpResponse(template.render(context, request))
            print("This is my data",mydata[0]['ename'])
            print("This is Employee Enothi ",fm['enothi_id'])
            return render(request,'employees/profile.html',context)
    designations = Designation.objects.all()
    context = {
                'form':fm,
                'enothi_id':user_id,
                'designationData': designations
                }
    return render(request,'employees/profile.html',context)

@login_required(login_url='login')
def select_evaluatee(request): 
    if request.method == 'POST':
        print(request.POST['employee'][1:5]) # need to check
        evaluatee_empid = int(request.POST['employee'][1:5]) #employee id must be of 4 digits
        evaluatee = Employee.objects.filter(empid = evaluatee_empid).values()
        #print("Select Evaluatee")
        #print(Designation.objects.filter(desigid = evaluatee[0]['edesignation']).values()[0]['designame'])
        #evaluatee_designation = Designation.objects.filter(desigid = evaluatee[0]['edesignation']).values()[0]['designame']
        print(evaluatee[0]['edesignation'])
        context = {
                'evaluateeeData': evaluatee,
                
                }
        return redirect('evaluate',emp_id = evaluatee_empid)
    else:
        employees = Employee.objects.all()
        #serialized_data = serialize("json", employees)
        context = {
                'employeeData': employees
                }
        return render(request,'employees/select_evaluatee.html',context) 


@login_required(login_url='login')
def evaluate(request, emp_id):
    if request.method == 'POST':
        print("Evaluate Post Method ",request.user)
        for key, value in request.POST.items():
            print('Key: %s' % (key) ) 
            # print(f'Key: {key}') in Python >= 3.7
            print('Value %s' % (value) )
            # print(f'Value: {value}') in Python >= 3.7
        #print(request.GET['employee'][1:5]) # need to check
        print("Data type check ",type(request.user.id))
        print("Data type check ",(request.user))
        evaluateeid = int(request.POST['evaluateeid'])
        evaluatorid =  Employee.objects.filter(enothi_id = int(request.user.username)).values()[0]['empid']
        secDeptEv = int(request.POST['secDept'])
        commEv = int(request.POST['committee'])
        behavEv = int(request.POST['behaviour'])
        comid = 1 # need to be modified
        new_eval = Evaluation(evaluateeid = evaluateeid, evaluatorid = evaluatorid , secDeptEv = secDeptEv, commEv = commEv, behavEv = behavEv, comid = comid)
        #print(fm.cleaned_data)
        new_eval.save()
        return redirect('home')
    evaluatee_empid = emp_id #employee id must be of 4 digits
    evaluatee = Employee.objects.filter(empid = evaluatee_empid).values()[0]
    print("Evaluate function")
    print(evaluatee)
       
    context = {
                'evaluateeData': evaluatee,
                'evaluateeDesignation' : Designation.objects.filter(desigid = evaluatee['edesignation']).values()[0]['designame']
                }
    print("test ",context['evaluateeData']['ename'])
    return render(request,'employees/evaluate.html',context)
        #return render(request,'employees/evaluate.html') 

@login_required(login_url='login')
def showReport(request):

    if request.method == 'POST':
        print("Report Post method called")
        print(request.POST)
        if request.POST['profile'] == "Back to Query":
            designations = Designation.objects.all()
            employees = Employee.objects.all()
            context = {
                'designationData': designations,
                'employeeData': employees
            }
            return render(request,'employees/query.html',context)
        
        elif request.POST['evalBased'] == "everyone" :
            print("Everyone's Evaluation")
            #print(type(int(request.POST['employee'][1:5])))
            #evaluatee_section = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']
            all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'][1:5])).values()
            results = []
            #print(type(all_evals))
            #print("Evaluatee Section : ",evaluatee_section)

            
            for eval in all_evals:
                results.append(eval)
                print("Evaluator ID : ",eval['evaluatorid'])
                print(type(eval['evaluatorid']))
                evaluator_section = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['esection']
               
            final_report = []
            #print(results)
            for eval in results:
                evaluator = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]
                print("Evaluator Info : ",evaluator['ename'])
                print("Section : ",petro.sections[int(evaluator['esection'])-1][1])
                print("SecDept Eval : ",petro.remarks[int(eval['secDeptEv'])-1][1])
                print("Committee Eval : ",petro.remarks[int(eval['commEv'])-1][1])
                print("Behavior Eval : ",petro.remarks[int(eval['behavEv'])-1][1])

                final_report.append({
                                  'evaluatee': Employee.objects.filter(empid = eval['evaluateeid']).values()[0]['ename'],
                                  'evaluator': evaluator['ename'], 
                                  'section': petro.sections[int(evaluator['esection'])-1][1],
                                  'secDeptEval' : petro.remarks[int(eval['secDeptEv'])-1][1],
                                  'comEval' : petro.remarks[int(eval['commEv'])-1][1],
                                  'behavEval': petro.remarks[int(eval['behavEv'])-1][1],
                                    }
                                  )
            print("final Report")
            print(final_report)
            context = {
                'report_data': final_report
                }
            
            return render(request,'employees/report.html',context)
        elif request.POST['evalBased'] == "secDept":
            print("Section or Department's evaluation")
            print(type(int(request.POST['employee'][1:5])))
            evaluatee_section = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']
            all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'][1:5])).values()
            results = []
            print(type(all_evals))
            print("Evaluatee Section : ",evaluatee_section)

            
            for eval in all_evals:
                print("Evaluator ID : ",eval['evaluatorid'])
                print(type(eval['evaluatorid']))
                evaluator_section = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['esection']
                if evaluatee_section == evaluator_section:
                    print("Matched!! This should be inserted")
                    results.append(eval)
                #print("Evaluator Section : " ,query_set[0]['esection'])
                
                #results.append(eval)
            final_report = []
            print(results)
            for eval in results:
                evaluator = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]
                print("Evaluator Info : ",evaluator['ename'])
                print("Section : ",petro.sections[int(evaluator['esection'])-1][1])
                print("SecDept Eval : ",petro.remarks[int(eval['secDeptEv'])-1][1])
                print("Committee Eval : ",petro.remarks[int(eval['commEv'])-1][1])
                print("Behavior Eval : ",petro.remarks[int(eval['behavEv'])-1][1])

                appenfinal_report.d({
                                  'evaluatee': Employee.objects.filter(empid = eval['evaluateeid']).values()[0]['ename'],
                                  'evaluator': evaluator['ename'], 
                                  'section': petro.sections[int(evaluator['esection'])-1][1],
                                  'secDeptEval' : petro.remarks[int(eval['secDeptEv'])-1][1],
                                  'comEval' : petro.remarks[int(eval['commEv'])-1][1],
                                  'behavEval': petro.remarks[int(eval['behavEv'])-1][1],
                                    }
                                  )
            print("final Report")
            print(final_report)
            context = {
                'report_data': final_report
                }
            
            return render(request,'employees/report.html',context)
        #remarks = Evaluation.objects.filter(secDeptEv = int(request.POST['remark'])).values()
        #remarks = Evaluation.objects.filter(secDeptEv = 4)
        #employee_list = []
        #remarks=[]
        
        #for remark in remarks:
        #    print(remark['evaluateeid'])
        #    evaluatee = Employee.objects.filter(empid = remark['evaluateeid']).values()[0]
        ##    print(evaluatee['ename'])
        #    print(evaluatee['edesignation'])
        #    print(evaluatee['edept'])
        #    print(evaluatee['edivision'])
        #    print(evaluatee['esection'])

            #print(remark['evaluatorid'])
        #    print(petro.departments[2][1])
        #    print("Done")
        #    employee_list.append({
        #                          'name': evaluatee['ename'], 
        #                          'section': petro.sections[int(evaluatee['esection'])-1][1],
        #                          'designation' : Designation.objects.filter(desigid = evaluatee['edesignation']).values()[0]['designame'],
        #                          'dept' : petro.departments[int(evaluatee['edept'])-1][1],
        #                          'division': petro.divisions[int(evaluatee['edivision'])-1][1],
        #                            }
        #                          )
            
        #print(type(int(request.POST['remark'])))
        #print(employee_list)
        context = {
                'report_data': final_report,
                }
        return render(request,'employees/report.html',context)
    
    designations = Designation.objects.all()
    employees = Employee.objects.all()
    context = {
                'designationData': designations,
                'employeeData': employees
            }
    return render(request,'employees/query.html',context)


@login_required(login_url='login')
def giveAward(request):
    if request.method == 'POST':

        print("checkkk!!!!!!!")
        print(request.POST['employee'])
        print(request.POST['permission'])
        return redirect('home')
        #return redirect('writeAwardDescription',emp_id = int(request.POST['employee']))
    employee = Employee.objects.all()
    #   evaluator_section = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['esection']
    #          'behavEval': petro.remarks[int(eval['behavEv'])-1][1],
    #   all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'][1:5])).values()
    #        evaluatee = Employee.objects.filter(empid = evaluatee_empid).values()
    #-   if request.method == 'POST':
     #  if form.is_valid():
      #      award = form.save(commit=False)
       #     award.user = request.user
        #    award.save()
         #   user_profile.counter -= 1
          #  user_profile.save()
           # return redirect('award_success')  # Redirect to a success page
    #else:
     #   form = AwardForm()
    #return render(request, 'give_award.html', {'form': form})
  #   evaluatee_section = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']
     #       all_evals = Evaluation.objects.filter(evaluateeid = int(request.POST['employee'][1:5])).values()
     #       results = []
     #       print(type(all_evals))
      #      print("Evaluatee Section : ",evaluatee_section)

            
     #       for eval in all_evals:
        #        print("Evaluator ID : ",eval['evaluatorid'])
        #        print(type(eval['evaluatorid']))
        #        evaluator_section = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]['esection']
        #        if evaluatee_section == evaluator_section:
        #            print("Matched!! This should be inserted")
        #            results.append(eval)
                #print("Evaluator Section : " ,query_set[0]['esection'])
                
                #results.append(eval)
       #     final_report = []
      #      print(results)
       #     for eval in results:
         #       evaluator = Employee.objects.filter(empid = eval['evaluatorid']).values()[0]
         #       print("Evaluator Info : ",evaluator['ename'])
          #      print("Section : ",petro.sections[int(evaluator['esection'])-1][1])
          #      print("SecDept Eval : ",petro.remarks[int(eval['secDeptEv'])-1][1])
          #      print("Committee Eval : ",petro.remarks[int(eval['commEv'])-1][1])
          #      print("Behavior Eval : ",petro.remarks[int(eval['behavEv'])-1][1])

            #    final_report.append({
                
    advisor = Employee.objects.filter(empid = int(request.POST['employee'][1:5])).values()[0]['esection']

    
    return render (request, 'employees/award.html', {'employeeData': employee} )



@login_required(login_url='login')
def getadvisor(request,emp_id):

    employee = Employee.objects.filter(id=employee_id).first()
    if employee:
        advisor_name = employee.advisor.name
        data = {
            'advisor_name': advisor_name
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    

@login_required(login_url='login')
def writeAwardDescription(request,emp_id):
    if request.method == 'POST':
        #print(request.POST['giveAward'])
        #print(request.POST['employee'])
        print("if from writeAwardDescription")
        
    print("get from write award")
    employee = Employee.objects.all()
    return render (request, 'employees/write_award_description.html', {'employeeData': employee} )

##############################Main award Function#############################################
@login_required(login_url='login')
def AwardSystem(request):
      #on post method. if counter>0 it will updatate award table
      #when advisor will login on clicking the notification bar it will redirect to the notfications.html where he will see the awardd table matchh with his enothi id.
      #on approving the report only then the counter value will be decreased


        
      if request.method == 'POST':
        current_user= Employee.objects.get(enothi_id = request.user) 
        counter=current_user.counter
        context={
            'counter':counter
        }  
      
        #if fmis valied?
       

        
          # Decrement the counter by 1
        if current_user.counter > 0:
         current_user.counter=current_user.counter-1
         current_user.save()
             
         print("checkkk!!!!!!!")
         award_evaluetee=Employee.objects.get(empid =request.POST['employee'])
         advisor_object=Employee.objects.get(enothi_id =request.POST['seek'])
         current_user= Employee.objects.get(enothi_id = request.user)
         #current_user.counter=10 
         award_evaluatorname =current_user.ename,
         award_evaluateename = award_evaluetee.ename,
         purposeid=request.POST['purpose'],
         description= request.POST['description'],
         advisorname= request.POST['seek']

         #advisor_deginations=petro.designations[advisor_object.edesignation-1][1]
         #print("dgdfgdg==============="+advisor_deginations)
         print("fuck")
         print (type(int(advisor_object.edesignation)))
         print (type(petro.designations[int(advisor_object.edesignation)][1]))
         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
         print (type(advisorname))
         print(advisorname)
         print (type(current_user))
         print (type(advisor_object))
         print(current_user)
         print(advisor_object)
         advisor=Employee.objects.get(enothi_id=advisorname)  




         #save data to award table:
         award = Award.objects.create(
         award_evaluatorid=current_user.enothi_id,
         award_evaluateeid=award_evaluetee.enothi_id,
         purposeid=request.POST.get('purpose'),
         description=request.POST.get('description'),
         advisorid=advisor_object.enothi_id,
    )
         award.save()
            # Create notification for advisor
         notification_message = f'{award_evaluatorname} is trying to give an award to { award_evaluateename}.'
         no=Notification.objects.create(
                    recipient=advisor_object,  # Assuming advisor_object has a 'user' field
                    sender=current_user,  # Assuming current_user has a 'user' field
                    message=notification_message
                )

            # Provide feedback to the user
         messages.success(request, 'Award request has been sent for approval.')
    
        
        else:
            messages.error(request, 'You have 0 award counter.')

        return redirect('award')
      ###############get###################
      
      else:
          emp_id=request.user
          current_user= Employee.objects.get(enothi_id = request.user)
          if(current_user.counter==0):
              messages.error(request, 'You have 0 award counter.')
              
         # advisor=Employee.objects.get(edivision=request.user )
         # print(advisor.ename+ "===========advisor")
          print(current_user.ename+ "===========ename")
         # print(current_user.empid)
          #print(current_user.enothi_id)
          current_division = current_user.edivision

        # Filter employees who are in the same department and have the designation "General Manager"
          advisor = Employee.objects.filter(edivision=current_division, edesignation=1).first()
          print("cute!!!!")
          print(advisor.edivision )

          supervisor=advisor.ename
          print(supervisor+ "===========supervisor")


          division= petro.divisions[int(current_user.edivision)-1][1]
         # print(division+ "===========edivision")
          designations = Designation.objects.all()
          employees = Employee.objects.all()
          advisor_designations=petro.designations[int(advisor.edesignation)][1]
          advisor_divisions=petro.divisions[int(advisor.edivision)-1][1]
          counter=current_user.counter
          print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
          print(advisor_divisions)
    
          context={
             'evaluator_division': division,
             'advisor':supervisor,
             'designationData': designations,
             'employeeData': employees,
             'advisor_object':advisor,
             'ade':advisor_designations,
             'adi':advisor_divisions,
             'counter': counter

         }

          return render(request,'employees/award.html',context)   

        # current_user.counter -= 1    
         #current_user.save()
         #new_award=Award (                
         #award_evaluatorname =current_user.ename,
         #award_evaluateename = award_evaluetee.ename,
         #purposeid=request.POST['purpose'],
         #description= request.POST['description'],
         #advisorname= request.POST['seek'] 

        #)
         #new_award.save()
         #messages.success(request, "Award given successfully.")
     
        #else:
         #   messages.error(request, "You have 0 award counter.")
            #return redirect('home')

        #return redirect('award')    
 

 # if request.method == 'POST':
    #    print ("o yes")
      #  print(request.POST['employee'][1:5]) # need to check
     #   evaluatee_empid = int(request.POST['employee'][1:5]) #employee id must be of 4 digits
     #   evaluatee = Employee.objects.filter(empid = evaluatee_empid).values()
      #  #print("Select Evaluatee")
        #print(Designation.objects.filter(desigid = evaluatee[0]['edesignation']).values()[0]['designame'])
        #evaluatee_designation = Designation.objects.filter(desigid = evaluatee[0]['edesignation']).values()[0]['designame']
      #  print(evaluatee[0]['edesignation'])
      #  context = {
           #    'evaluateeeData': evaluatee,
                
           #     }
    #    return redirect('evaluate',emp_id = evaluatee_empid)



#if fm.is_valid():
          #  mydata = Employee.objects.filter(enothi_id = request.user)#this will ensure that form is saved to logged in user even if we repeatedly change data
          #  if mydata.exists():
    
              #  myProfileData = Employee.objects.get(enothi_id = request.user)
              #  #print(" My Objects ",myProfileData[0])
             #   myProfileData.ename = request.POST['name']
              #  myProfileData.eemail = request.POST['email']
              #  myProfileData.empid = request.POST['empid']
             #   myProfileData.edesignation = request.POST['designation']
            #    myProfileData.esection = request.POST['section']
             #   myProfileData.edept = request.POST['department']
             #   myProfileData.edivision = request.POST['division']
             #   myProfileData.edirectorate = request.POST['directorate']
           #     myProfileData.save()
           #     return redirect('home')#
def notifications_view(request):
    if hasattr(request.user, 'ename'):
        employee = request.user.ename
        notifications = Notification.objects.filter(recipient=employee, is_read=False)
        print("o yes")
        print(notifications)
        unread_notifications_count = notifications.count()
    else:
        print("o yes else ")
        notifications = []
        unread_notifications_count = 0

    context = {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, 'employees/notifications.html', context)

def approve_award(request, notification_id):
    notification = Notification.objects.get(id=notification_id)

    # Logic to approve the award
    award = Award.objects.create(
        award_evaluatorname=notification.sender.username,
        award_evaluateename=notification.message.split(' to ')[1].split('.')[0],
        purposeid=request.POST.get('purpose'),
        description=request.POST.get('description'),
        advisorname=notification.recipient.username,
    )

    # Decrease the counter of the evaluator
    evaluator = Employee.objects.get(ename=notification.sender.username)
    evaluator.counter -= 1
    evaluator.save()

    # Notify the evaluator
    notification_message = f'Your award to {award.award_evaluateename} has been approved.'
    Notification.objects.create(recipient=notification.sender, sender=request.user, message=notification_message)

    notification.is_read = True
    notification.save()

    return redirect('notifications_view')

@login_required(login_url='login')
def AwardReport(request):
 
 
    if request.method == 'GET':
        print(request.user)
        try:
            current_user = Employee.objects.get(enothi_id=request.user)
        except Employee.DoesNotExist:
            # Handle case where current user doesn't exist (optional)
            current_user = None
        
        if current_user:
            award_advisor = Award.objects.filter(award_evaluatorid=current_user.enothi_id)
            
            if award_advisor.exists():
                current_user.counter=current_user.counter-1
                finalawardreport = []
                
                for eval in award_advisor:
                    evaluator_employee = Employee.objects.get(enothi_id=eval.award_evaluatorid)
                    evaluatee_employee = Employee.objects.get(enothi_id=eval.award_evaluateeid)

                    finalawardreport.append({
                        'award_id': eval.awardid,
                        'advisorid': eval.advisorid,
                        'evaluator_name': evaluator_employee.ename,
                        'evaluatee_name': evaluatee_employee.ename,
                        'purpose': eval.purposeid,
                        'description': eval.description,
                        'status': petro.status[eval.Status][1],
                        'Counter': evaluator_employee.counter,
                        'evaluator_id': evaluator_employee.enothi_id,
                        'remark':eval.remark
                    })
                
                context = {
                    'report_data': finalawardreport
                }
                
                return render(request, 'employees/awardreport.html', context)
            else:
                # Redirect to homepage if no awards exist for the advisor
                return redirect('home')  # Assuming 'home' is the name of your homepage URL
        else:
            # Handle case where current user is None (optional)
            return redirect('home')  # Redirect to homepage if user doesn't exist or isn't logged in
    

@login_required(login_url='login')
def Advisor_approval(request):
 
    if request.method == 'GET':
        print(request.user)
        try:
            current_user = Employee.objects.get(enothi_id=request.user)
        except Employee.DoesNotExist:
            # Handle case where current user doesn't exist (optional)
            current_user = None
        
        if current_user:
            award_advisor = Award.objects.filter(advisorid=current_user.enothi_id,Status=0)| Award.objects.filter(advisorid=current_user.enothi_id,remark="ORyd9sG1JrdDI1m")
            
            if award_advisor.exists():
                current_user.counter=current_user.counter-1
                finalawardreport = []
                
                for eval in award_advisor:
                    evaluator_employee = Employee.objects.get(enothi_id=eval.award_evaluatorid)
                    evaluatee_employee = Employee.objects.get(enothi_id=eval.award_evaluateeid)

                    finalawardreport.append({
                        'award_id': eval.awardid,
                        'advisorid': eval.advisorid,
                        'evaluator_name': evaluator_employee.ename,
                        'evaluatee_name': evaluatee_employee.ename,
                        'purpose': eval.purposeid,
                        'description': eval.description,
                        'status': petro.status[eval.Status][1],
                        'Counter': evaluator_employee.counter,
                        'evaluator_id': evaluator_employee.enothi_id
                    })
                
                context = {
                    'report_data': finalawardreport
                }
                
                return render(request, 'employees/notifications.html', context)
            else:
                # Redirect to homepage if no awards exist for the advisor
                return redirect('home')  # Assuming 'home' is the name of your homepage URL
        else:
            # Handle case where current user is None (optional)
            return redirect('home')  # Redirect to homepage if user doesn't exist or isn't logged in

    # Handle other HTTP methods if needed
    # Example: return HttpResponseNotAllowed(['GET'])

     #advisor_object_award=Award.objects.get(request.user.enothi_id=)
     
     ###########AWARD Status PENDING APPROVE/REJECT##########################
    

@csrf_exempt
def update_remark_status(request):
    if request.method == 'POST':
       
        award_id = request.POST.get('award_id')
        awardobject=Award.objects.get(awardid=award_id)
        #new_status = request.POST.get('new_status')
        remarks = request.POST.get('remark')
       # awardobject.Status=new_status
        awardobject.remark=remarks
        awardobject.save()
        # Add logic to update the award status in the database
        # Example:
        # award = Award.objects.get(id=award_id)
        # award.status = new_status
        # award.remark = remark
        # award.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})

@require_POST
def update_award_status(request):
    award_id = request.POST.get('award_id')
    new_status = request.POST.get('new_status')
    print(type(new_status))
    print("pyramid*********************")
    print(new_status)
    new_counter=request.POST.get('new_counter')
    employee_id=request.POST.get('employee_id')
    employee=Employee.objects.get(enothi_id=employee_id)
    if(new_status=="1"):
        employee.counter=employee.counter+1
        employee.save()
        
    award = get_object_or_404(Award, awardid=award_id)
    award.Status = new_status
    award.remark="ORyd9sG1JrdDI1m"
    award.save()
    return JsonResponse({'status': 'success'})


@login_required(login_url='login')
def award_distribution(request, enothi_id):
    print("enothiid")
    print(enothi_id)
    employee = Employee.objects.get(enothi_id=enothi_id)
    print(employee.ename)
    own_department = Award.objects.filter(
        award_evaluateeid=employee.enothi_id,
        #employee__edept=employee.edept
    ).count()
   # other_department = Award.objects.filter(
       # award_evaluateeid=employee.enothi_id
   # ).exclude(employee__edept=employee.edept).count()
    
    data = {
        'own_department': own_department,
       # 'other_department': other_department
    }
    return JsonResponse(data)

def advisor_status(request):
    pending = Award.objects.filter(Status=0).count()
    approved = Award.objects.filter(Status=2).count()
    rejected = Award.objects.filter(Status=1).count()
    
    data = {
        'pending': pending,
        'approved': approved,
        'rejected': rejected
    }
    return JsonResponse(data)

def dashboard(request):
    return render(request, 'employees/dashboard.html')
@login_required(login_url='login')
def award_data(request):
    awards = Award.objects.all().values('advisorid', 'award_evaluatorid', 'award_evaluateeid', 'Status','remark')
    awards_data = []
    for award in awards:
        print("wtffffff")
        print(award['advisorid'])
  
        awards_data.append({
            'id': Employee.objects.get(enothi_id=award['advisorid']).ename,
            'evaluator': award['award_evaluatorid'],
            'evaluator_name':Employee.objects.get(enothi_id=award['award_evaluatorid']).ename,
            'evaluatee': award['award_evaluateeid'],
            'evaluatee_name':Employee.objects.get(enothi_id=award['award_evaluateeid']).ename,
            'status': petro.status[award['Status']][1],
            'remark': award['remark']
        })
    return JsonResponse({'awards': awards_data})

def search_employee(request):
    query = request.GET.get('q', '')
    if query:
        employees = Employee.objects.filter(Q(ename__icontains=query) | Q(enothi_id__icontains=query))
        employees_data = [{'enothi_id': emp.enothi_id, 'name': emp.ename} for emp in employees]
        print("Employees data: ", employees_data)  # Debugging log
    else:
        employees_data = []
    return JsonResponse({'employees': employees_data})


def award_pie(request,enothi_id):
    try:
        print(enothi_id)
        print("the great wall")
        # Fetch the employee by enothi_id
        evaluatee = Employee.objects.get(enothi_id=enothi_id)
        ename=evaluatee.ename
        enothi=evaluatee.enothi_id
        #evaluator=Award.objects.ge
        
        # Get awards where the evaluator is in the same department as the evaluatee
        own_department_awards = Award.objects.filter(
            award_evaluateeid=evaluatee.enothi_id,
            award_evaluatorid__in=Employee.objects.filter(edivision=evaluatee.edivision).values_list('enothi_id', flat=True),
            Status=2
        ).count()
        print(own_department_awards)
        print("BANKOK")
        
        # Get awards where the evaluator is in a different department than the evaluatee
        other_department_awards = Award.objects.filter(
            award_evaluateeid=evaluatee.enothi_id
        ).exclude(
            award_evaluatorid__in=Employee.objects.filter(edivision=evaluatee.edivision).values_list('enothi_id', flat=True)
        ).filter(
            Status=2
        ).count()
        print(other_department_awards)
        print("BALI")
        
        # Return the results as a JSON response
        return JsonResponse({
            'own_department': own_department_awards,
            'other_department': other_department_awards,
            'name': ename,
            'enothi': enothi, 
        })
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
    
def get_employee_awards(request, enothi_id):
    print("INDIA")
    awards= Award.objects.filter(award_evaluateeid=enothi_id)
    serializer = AwardSerializer(awards, many=True)
    return JsonResponse({'awards': serializer.data})



def search_advisor(request):
    print("srilanka")
    if request.method == 'GET':
       award=Award.objects.all()
       context={
        'advisorData':award
         }
       return render (request,'employees/dashboard.html',context)
   

def is_superuser(user):
    return user.is_superuser

# Apply the user_passes_test decorator to your view
@user_passes_test(is_superuser)
def dashboard(request):
    return render(request, 'employees/dashboard.html')   

