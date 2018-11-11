from django.shortcuts import render, HttpResponseRedirect
from  . models import UserExt, UserProfile, SchClass, Grades, Attendance,\
     SchClass_Join_Approval, ParentMonitor
from django.contrib.auth.models import User
from django.db import IntegrityError
from datetime import datetime
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from . smsnotif import send_sms
from threading import Thread
from functools import partial
from pytz import timezone
timezone_UTC = timezone('UTC')
timezone_PH = timezone('Asia/Manila')
from PIL import Image


# Create your views here.


def get_userext_object(user):
    user_object = User.objects.get(username=user)
    userext_object = UserExt.objects.get(user=user_object.pk)
    return userext_object

def get_user_profile(userextid):
    user_profile = UserProfile.objects.get(user=userextid)
    return user_profile


def fetch_classes(userextid):
    class_objects = SchClass.objects.filter(instructor=userextid)
    return class_objects


def fetch_student_classes(userextid):
    verified_join = SchClass_Join_Approval.objects.filter(student=userextid)
    return verified_join


def format_id(user):
    user_object = User.objects.get(username=user)
    userext_object = UserExt.objects.get(user=user_object.pk)
    date_joined = user_object.date_joined
    userextid = userext_object.id
    return "gcc-%s" % str(userextid) + date_joined.strftime("%Y%m%d")


def send_multiple_sms(object_list):
    for i in object_list:
        send_sms(i['msg'], i['contact'])


def send_multiple_sms_thread(object_list):
    threadx = Thread(target=partial(send_multiple_sms, object_list))
    threadx.start()


def landing_page(request):
    return render(request, 'GAMS_webapp/landingpage.html')


def user_login(request):
    # authenticated user redirect
    if request.user.is_authenticated:
        return HttpResponseRedirect('/index/')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            login(request, user=user)
            return HttpResponseRedirect('/index/')
        else:
            context = {
                'auth_error': 'Incorrect username or password'
            }
            return render(request, 'GAMS_webapp/login.html', context=context)
    elif request.COOKIES.get('sessionid'):
        return HttpResponseRedirect('/index/')
    else:
        return render(request, 'GAMS_webapp/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')


def register_user(request):
    context = {}
    if request.method == 'POST':
        if request.POST['password'] == request.POST['confirm']:

            try:
                validate_password(request.POST['password'], user=None, password_validators=None)
                gender = 'male'
                if request.POST['gender'] == 'female':
                    gender = 'female'
                birthyear = int(request.POST['birthday'][:4])
                if (int(datetime.now().strftime("%Y")) - birthyear) < 10:
                    context['response'] = 'Invalid Age'
                else:
                    try:
                        user_object = User.objects.create(
                            username=request.POST['username'],
                            email=request.POST['email']
                        )
                        user_object.set_password(request.POST['password'])
                        user_object.save()

                        user_ext_object = UserExt.objects.create(
                            user=user_object,
                            user_type=request.POST['user_type'],
                            first_name=request.POST['first_name'],
                            middle_name=request.POST['middle_name'],
                            last_name=request.POST['last_name'],
                            course=request.POST['course'],
                            is_active=True
                        )
                        user_ext_object.save()

                        user_profile_obj = UserProfile.objects.create(
                            user=user_ext_object,
                            address=request.POST['address'],
                            birthday=request.POST['birthday'],
                            gender=gender,
                            contact_number=request.POST['contact_number'],
                            guardian_contact_number=request.POST['guardian_contact_number']
                        )
                        user_profile_obj.save()
                        context['response'] = True
                    except IntegrityError:
                        context['response'] = 'that username was already in use.'
            except:
                context['password_invalid'] = password_validators_help_texts()

        else:
            context['response'] = 'password didn\'t match'

    return render(request, 'GAMS_webapp/registration.html', context=context)

@ login_required
def index(request, response=None):
    try:
        userext_object = get_userext_object(request.user)
    except:
        logout(request)
        return HttpResponseRedirect('/login/')

    context = {
        'userext': userext_object,
        'user_profile': get_user_profile(userext_object.pk),
        'formatted_id': format_id(request.user),
        'response': response,
    }

    if userext_object.user_type == 'instructor':
        context['class_list'] = fetch_classes(userext_object.pk)

    elif userext_object.user_type == 'student':
        class_list = fetch_student_classes(userext_object.pk)
        classes_objects = []
        for i in class_list:
            schclass_object = SchClass.objects.get(id=i.schclass.id)
            instructor_object = UserExt.objects.get(id=schclass_object.instructor.id)
            schclass_object.instructor_name = "%s %s %s" % (instructor_object.first_name,
                                                            instructor_object.middle_name,
                                                            instructor_object.last_name)
            schclass_object.is_approved = i.verified
            classes_objects.append(schclass_object)
        context['classes_objects'] = classes_objects

        parent_objects = ParentMonitor.objects.filter(Q(student=userext_object) & Q(verified=True))
        for i in parent_objects:
            i.formatted_id_parent = format_id(i.parent.user.username)
        context['parents_objects'] = parent_objects


    elif userext_object.user_type == 'parent':
        monitor_list_objects = ParentMonitor.objects.filter(parent=userext_object)
        for i  in monitor_list_objects:
            i.student.formatted_id = format_id(i.student.user.username)
        context['monitor_list_objects'] = monitor_list_objects

    return render(request, 'GAMS_webapp/index.html', context=context)


@ login_required
def create_class(request):
    if request.method == 'POST':
        userext_object = get_userext_object(request.user)
        check_existence = SchClass.objects.filter(instructor=userext_object,
            course=request.POST['course'],
            schclass_name=request.POST['class_name'],
            class_year=request.POST['year_level'],
            section=request.POST['section'],).exists()

        if check_existence:
            return index(request, response='You already have created a class with the same information.')

        schclass = SchClass.objects.create(
            instructor=userext_object,
            course=request.POST['course'],
            schclass_name=request.POST['class_name'],
            class_year=request.POST['year_level'],
            section=request.POST['section'],
        )
        schclass.save()
        schclass.class_code = 'gcc-class-' + str(schclass.id)
        schclass.save()

    return HttpResponseRedirect('/index/')


@ login_required
def student_join_class(request):
    if request.method == 'POST':

        try:
            class_object = SchClass.objects.get(class_code=request.POST['class_code'])
        except SchClass.DoesNotExist:
            return index(request,
                         response='Class doesn\'t Exist. Please Ask your'
                                ' instructor for the correct class code')

        if class_object.verified is False:
            return index(request,
                         response='This class has not been verified by the administrator')

        userext_object = get_userext_object(request.user)

        request_existence = SchClass_Join_Approval.objects.\
            filter(Q(student=userext_object) & Q(schclass=class_object)).exists()

        if request_existence:
            return index(request, response='You already have submitted a request to'
                                           ' join this class or you already have join this class.')

        join_object = SchClass_Join_Approval.objects.create(
            student=userext_object,
            schclass=class_object,
            verified=False
        )
        join_object.save()
        return index(request, response='ok')

    return HttpResponseRedirect('/index/')

@ login_required
def student_pending_request(request):
    userext_object = get_userext_object(request.user)

    context = {
        'userext': userext_object,
    }

    join_requests = []

    requests_object = SchClass_Join_Approval.objects.all()

    for i in requests_object:
        schclass = SchClass.objects.get(id=i.schclass.id)
        student_object = UserExt.objects.get(id=i.student.id)
        student_user = User.objects.get(id=student_object.user.id)
        student_object.profile = UserProfile.objects.get(user=student_object.id)
        student_object.formatted_id = format_id(student_user)
        if schclass.instructor == userext_object and i.verified is False:
            i_request = {
                'request_object_id': i.id,
                'class_object': schclass,
                'student_object': student_object,
            }
            join_requests.append(i_request)

    context['join_requests'] = join_requests

    return render(request, 'GAMS_webapp/student_pending.html', context=context)


@ login_required
def delete_student_request(request):
    if request.method == 'POST':
        request_object = SchClass_Join_Approval.objects.get(id=request.POST['request_object'])

        class_object = SchClass.objects.get(id=request_object.schclass.id)
        user_profile = UserProfile.objects.get(user_id=request_object.student.id)
        contact = user_profile.contact_number

        msg_dict = {
            'msg': 'your class join request in ' + class_object.schclass_name + ' was rejected.',
            'contact': contact
        }

        request_object.delete()

        send_multiple_sms_thread([msg_dict])

    return HttpResponseRedirect('/request_pending/')


@ login_required
def accept_student_request(request):
    if request.method == 'POST':
        request_object = SchClass_Join_Approval.objects.get(id=request.POST['request_object'])
        request_object.verified = True
        request_object.save()

        class_object = SchClass.objects.get(id=request_object.schclass.id)
        user_profile = UserProfile.objects.get(user_id=request_object.student.id)
        contact = user_profile.contact_number

        msg_dict = {
            'msg': 'your class join request in ' + class_object.schclass_name + ' was approved.',
            'contact': contact
        }

        send_multiple_sms_thread([msg_dict])

    return HttpResponseRedirect('/request_pending/')


@ login_required
def monitor_pending_request(request):
    userext_object = get_userext_object(request.user)

    context = {
        'userext': userext_object,
    }

    pending_requests_objects = ParentMonitor.objects.filter(Q(schclass__instructor=userext_object) &
                                                            Q(verified=False))

    for i in pending_requests_objects:
        i.student.formatted_id = format_id(i.student.user.username)
        i.parent.formatted_id = format_id(i.parent.user.username)

    context['pending_requests_objects'] = pending_requests_objects

    return render(request, 'GAMS_webapp/monitor_requests_pending.html', context=context)


@ login_required
def delete_student_monitor_request(request):
    if request.method == 'POST':
        request_object = ParentMonitor.objects.get(id=request.POST['request_object'])
        parent_profile = UserProfile.objects.get(user=request_object.parent)

        student_name = "%s %s %s" % (request_object.student.first_name,
                                     request_object.student.middle_name,
                                     request_object.student.last_name)

        msg_dict = {
            'msg': 'your request to monitor ' + student_name + ' in class ' +
                   request_object.schclass.schclass_name + ' was rejected.',
            'contact': parent_profile.contact_number
        }

        request_object.delete()

        send_multiple_sms_thread([msg_dict])

    return HttpResponseRedirect('/monitor_requests_pending/')


@ login_required
def accept_student_monitor_request(request):
    if request.method == 'POST':
        request_object = ParentMonitor.objects.get(id=request.POST['request_object'])
        parent_profile = UserProfile.objects.get(user=request_object.parent)
        request_object.verified = True
        request_object.save()

        student_name = "%s %s %s" % (request_object.student.first_name,
                                     request_object.student.middle_name,
                                     request_object.student.last_name)

        msg_dict = {
            'msg': 'your request to monitor ' + student_name + ' in class ' +
                   request_object.schclass.schclass_name + ' was accepted.',
            'contact': parent_profile.contact_number
        }

        send_multiple_sms_thread([msg_dict])

    return HttpResponseRedirect('/monitor_requests_pending/')


@ login_required
def class_instructor_view(request, class_code, response=None):
    userext_object = get_userext_object(request.user)
    context = {
        'userext': userext_object,
        'response': response
    }
    try:
        class_object = SchClass.objects.get(class_code=class_code, verified=True)
        context['class_object'] = class_object

        student_lists = SchClass_Join_Approval.objects.filter(schclass=class_object, verified=True)

        student_objects = []

        for i in student_lists:
            student_obj = UserExt.objects.get(id=i.student.id)
            student_obj_user = User.objects.get(id=i.student.user.id)
            student_obj.formatted_id = format_id(student_obj_user.username)
            student_obj.profile = UserProfile.objects.get(user=i.student.id)
            student_objects.append(student_obj)

        context['student_object'] = student_objects

        class_attendances = Attendance.objects.filter(schclass=class_object)

        for i in class_attendances:
            i.student = UserExt.objects.get(id = i.student.id)
            student_obj_user = User.objects.get(id=i.student.user.id)
            i.formatted_student_id = format_id(student_obj_user.username)
            i.formatted_datetime = i.attendance_datetime.astimezone(timezone_PH).strftime("%B %d, %Y - %I:%M:%S %p")

        context['attendance_object'] = class_attendances

        class_grades = Grades.objects.filter(schclass=class_object)

        for i in class_grades:
            i.formatted_student_id = format_id(i.student.user.username)

        context['class_grades'] = class_grades

    except SchClass.DoesNotExist:
        context['error'] = 'Class Doesn\'t Exists Or Not Yet Verified'

    return render(request, 'GAMS_webapp/class_instructor_view.html', context=context)


@ login_required
def class_student_view(request, class_code):
    userext_object = get_userext_object(request.user)
    context = {
        'userext': userext_object,
    }
    try:
        class_object = SchClass.objects.get(class_code=class_code, verified=True)
        context['class_object'] = class_object

        attendance_objects = Attendance.objects.filter(Q(student=userext_object) & Q(schclass=class_object))
        for i in attendance_objects:
            i.formatted_datetime = i.attendance_datetime.astimezone(timezone_PH).strftime("%B %d, %Y - %I:%M:%S %p")
        context['attendance_objects'] = attendance_objects

        grade_object = Grades.objects.get(Q(student=userext_object) & Q(schclass=class_object))
        context['grade_object'] = grade_object

    except:
        context['error'] = 'This class doesn\'t exists or is not yet verified'

    return render(request, 'GAMS_webapp/class_student_view.html', context=context)

@ login_required
def instructor_profile_view(request, class_code, user_id):
    session_user = UserExt.objects.get(user__username=request.user)
    context = {
        'session_user': session_user
    }
    try:
        instructor_object = UserExt.objects.get(id=user_id)
        instructor_profile_object = UserProfile.objects.get(user=instructor_object)
        class_objects = SchClass.objects.filter(Q(instructor=instructor_object) & Q(verified=True))

        context['formatted_id'] = format_id(instructor_object.user.username)
        context['instructor_object'] = instructor_object
        context['profile_object'] = instructor_profile_object
        context['class_objects'] = class_objects

    except:
        context['error'] = 'I do not know who is this instructor.'

    return render(request, 'GAMS_webapp/instructor_profile_view.html', context=context)

@ login_required
def record_attendance(request):
    if request.method == 'POST':
        class_object = SchClass.objects.get(id=request.POST['class_id'])
        class_students = SchClass_Join_Approval.objects.filter(Q(schclass=class_object) & Q(verified=True))

        all_class_students = []

        for i in class_students:
            student_object = UserExt.objects.get(id=i.student.id)
            all_class_students.append(student_object)

        student_present_list = request.POST.getlist('is_present')
        student_present_objects = []

        for i in student_present_list:
            student_object = UserExt.objects.get(id=i)
            if student_object in all_class_students:
                all_class_students.remove(student_object)
            student_present_objects.append(student_object)

        student_absent_objects = all_class_students

        student_late_list = request.POST.getlist('is_late')

        check_existence = Attendance.objects.filter\
            (Q(attendance_datetime__icontains=datetime.now(timezone_UTC).strftime("%Y-%m-%d"))
             & Q(schclass=class_object))

        for i in check_existence:
            i.delete()

        msg_list = []

        for i in student_present_objects:
            remarks = None
            profile = get_user_profile(i.id)
            if str(i.id) in student_late_list:
                remarks = 'Late'
            record_present = Attendance.objects.create(
                schclass=class_object,
                student=i,
                attendance_datetime=datetime.now(timezone_UTC),
                remarks=remarks,
                is_present=True
            )
            record_present.save()

            msg_dict = {
                'msg': i.first_name + ' is present now in ' + class_object.schclass_name,
                'contact': profile.guardian_contact_number
            }

            parent_monitored = ParentMonitor.objects.filter(Q(student=i) & Q(schclass=class_object) & Q(verified=True))

            for i in parent_monitored:
                parent_profile = UserProfile.objects.get(user=i.parent)
                if parent_profile.contact_number != profile.guardian_contact_number:
                    msg_dict_parent = {
                        'msg': i.first_name + ' is present now in ' + class_object.schclass_name,
                        'contact': parent_profile.contact_number
                    }
                    msg_list.append(msg_dict_parent)

            msg_list.append(msg_dict)

        for i in student_absent_objects:
            remarks = None
            profile = get_user_profile(i.id)
            if str(i.id) in student_late_list:
                remarks = 'Late'
            record_absent = Attendance.objects.create(
                schclass=class_object,
                student=i,
                attendance_datetime=datetime.now(timezone_UTC),
                remarks=remarks,
                is_present=False
            )
            record_absent.save()

            msg_dict = {
                'msg': i.first_name + ' is absent now in ' + class_object.schclass_name,
                'contact': profile.guardian_contact_number
            }

            parent_monitored = ParentMonitor.objects.filter(Q(student=i) & Q(schclass=class_object) & Q(verified=True))

            for i in parent_monitored:
                parent_profile = UserProfile.objects.get(user=i.parent)
                if parent_profile.contact_number != profile.guardian_contact_number:
                    msg_dict_parent = {
                        'msg': i.first_name + ' is absent now in ' + class_object.schclass_name,
                        'contact': parent_profile.contact_number
                    }
                    msg_list.append(msg_dict_parent)

            msg_list.append(msg_dict)

        send_multiple_sms_thread(msg_list)

    response = 'Attendances were recorded'

    return class_instructor_view(request, class_code=request.POST['class_code'], response=response)


@ login_required
def profile_view(request, response=None):
    context = {
        'response': response
    }
    user_object = User.objects.get(username=request.user)
    user_ext_object = get_userext_object(request.user)
    user_profile = UserProfile.objects.get(user=user_ext_object)
    user_profile.birthday = user_profile.birthday.strftime("%Y-%m-%d")

    context['formatted_id'] = format_id(request.user)
    context['user_object'] = user_object
    context['userext'] = user_ext_object
    context['profile'] = user_profile

    return render(request, 'GAMS_webapp/profile_view.html', context=context)

@ login_required
def update_profile(request):
    response = None
    if request.method == 'POST':
        birthyear = int(request.POST['birthday'][:4])
        if (int(datetime.now().strftime("%Y")) - birthyear) < 10:
            response = 'Invalid Age'
        else:
            user_object = User.objects.get(username=request.user)
            user_object.email = request.POST['email']

            user_ext_object = get_userext_object(request.user)

            user_ext_object.first_name = request.POST['fname']
            user_ext_object.middle_name = request.POST['mname']
            user_ext_object.last_name = request.POST['lname']
            user_ext_object.course = request.POST['course']

            user_profile = UserProfile.objects.get(user=user_ext_object)
            gender = 'male'
            if request.POST['gender'] == 'female':
                gender = 'female'
            user_profile.gender = gender
            user_profile.address = request.POST['address']
            user_profile.birthday = request.POST['birthday']
            user_profile.contact_number = request.POST['contact_number']
            user_profile.guardian_contact_number = request.POST['guardian_contact_number']

            user_object.save()
            user_ext_object.save()
            user_profile.save()
            response = 'ok'

    return profile_view(request, response=response)


@ login_required
def update_photo(request):
    if request.method == 'POST':
        userext_object = get_userext_object(request.user)
        profile = get_user_profile(userext_object.id)

        if 'picture' in request.FILES:
            try:
                test = Image.open(request.FILES['picture'])
                test.verify()
                profile.profile_photo = request.FILES['picture']

                profile.save()
            except:
                return profile_view(request, 'invalid image format')

    return HttpResponseRedirect('/profile/')



@ login_required
def student_profile_instructor_view(request, class_code, user_id, response=None):
    userext_object = get_userext_object(request.user)
    class_object = SchClass.objects.get(class_code=class_code)
    context = {
        'class_object': class_object,
        'userext': userext_object,
        'response': response
    }
    try:
        student_object = UserExt.objects.get(id=user_id)
        student_profile = UserProfile.objects.get(user=user_id)

        parent_objects = ParentMonitor.objects.filter(Q(student=student_object)
                                                      & Q(schclass=class_object)
                                                      & Q(verified=True))
        for i in parent_objects:
            i.formatted_id_parent = format_id(i.parent.user.username)


        context['formatted_id'] = format_id(student_object.user.username)
        context['student_object'] = student_object
        context['student_profile'] = student_profile
        context['parents_object'] = parent_objects
        try:
            grade_object = Grades.objects.get(Q(student=student_object) & Q(schclass=class_object))
            context['grade_object'] = grade_object

        except Grades.DoesNotExist:
            pass
    except UserExt.DoesNotExist:
        context['error'] = 'Not Your Student'
    return render(request, 'GAMS_webapp/student_profile_intructor_view.html', context=context)


@ login_required
def student_submit_grade(request):
    if request.method == 'POST':
        class_object = SchClass.objects.get(class_code=request.POST['class_code'])
        instructor_object = UserExt.objects.get(id=class_object.instructor.id)

        student_object = UserExt.objects.get(id=request.POST['student_id'])
        profile = get_user_profile(student_object.id)

        if request.POST['equivalent'] == 'None':
            equivalent = None
            remarks = 'None'
        else:
            equivalent = float(request.POST['equivalent'])
            remarks = 'none'
            if 3 >= equivalent >= 1:
                remarks = 'passed'
            elif equivalent == 4.00:
                remarks = 'incomplete'
            elif equivalent == 5.00:
                remarks = 'failed'

        check_existence = Grades.objects.filter(Q(schclass=class_object)
                                                & Q(instructor=instructor_object)
                                                & Q(student=student_object))

        if check_existence.exists():
            check_existence.delete()

        grade_submit = Grades.objects.create(
            schclass=class_object,
            student=student_object,
            instructor=instructor_object,
            equivalent=equivalent,
            remarks=remarks,
            datetime_modified=datetime.now(timezone_UTC)
        )

        grade_submit.save()

        msg_list = []

        notif_parent = {
            'msg': student_object.first_name + '\'s grades in ' + class_object.schclass_name +
            ' is ' + str(equivalent) + '.\n' + 'remarks: ' + remarks.capitalize(),
            'contact': profile.guardian_contact_number
        }

        notif_student = {
            'msg': 'Your grades in ' + class_object.schclass_name +
            ' is ' + str(equivalent) + '.\n' + 'remarks: ' + remarks.capitalize(),
            'contact': profile.contact_number
        }

        parent_monitored = ParentMonitor.objects.filter(Q(student=student_object)
                                                        & Q(schclass=class_object)
                                                        & Q(verified=True))

        for i in parent_monitored:
            parent_profile = UserProfile.objects.get(user=i.parent)
            if parent_profile.contact_number != profile.guardian_contact_number:
                notif_parentx = {
                    'msg': student_object.first_name + '\'s grades in ' + class_object.schclass_name +
                    ' is ' + str(equivalent) + '.\n' + 'remarks: ' + remarks.capitalize(),
                    'contact': parent_profile.contact_number
                }
                msg_list.append(notif_parentx)


        msg_list.append(notif_parent)
        msg_list.append(notif_student)

        send_multiple_sms_thread(msg_list)

        response = 'Grade was Submitted'
        return student_profile_instructor_view(request, class_object.class_code, student_object.id, response=response)


@ login_required
def student_monitor_request(request):
    userext_object = get_userext_object(request.user)
    response = None
    if request.method == 'POST':
        try:
            class_object = SchClass.objects.get(Q(class_code=request.POST['class_code']) & Q(verified=True))
            try:
                cleaned_student_id = request.POST['student_id'].split('-')[1][:-8]
            except:
                response = 'invalid student ID'
                return index(request, response=response)
            student_object = UserExt.objects.get(id=int(cleaned_student_id))
            if student_object.user_type != 'student':
                response = 'The ID does\'nt belong to a student'
            else:
                schclass_student = SchClass_Join_Approval.objects.get(Q(schclass=class_object)
                                                                      & Q(student=student_object)
                                                                      & Q(verified=True))

                check_existence = ParentMonitor.objects.filter(Q(schclass=class_object) &
                                                               Q(student=student_object) &
                                                               Q(parent=userext_object)).exists()

                if check_existence:
                    response = 'You already have submitted a monitor request' \
                               ' in this student on the class you specified'
                else:
                    create_monitor_request = ParentMonitor.objects.create(
                        schclass=class_object,
                        student=student_object,
                        parent=userext_object
                    )
                    create_monitor_request.save()

                    response = 'ok'

        except SchClass_Join_Approval.DoesNotExist:
            response = 'the student is not yet joining ' \
                       'this class or is not yet verified by the instructor'
        except UserExt.DoesNotExist:
            response = 'Student with that ID is not existing'
        except SchClass.DoesNotExist:
            response = 'This class doesn\'t exists or is not yet verified'
    return index(request, response=response)


@ login_required
def class_parent_view(request, class_code, student_id):
    parent_object = get_userext_object(request.user)
    context = {
        'session_user': parent_object
    }

    try:
        class_object = SchClass.objects.get(class_code=class_code)
        student_object = UserExt.objects.get(id=student_id)
        student_profile = UserProfile.objects.get(user=student_object)

        context['class_object'] = class_object
        context['student_object'] = student_object
        context['student_profile'] = student_profile
        context['formatted_id'] = format_id(student_object.user.username)

        attendance_objects = Attendance.objects.filter(Q(student=student_object) & Q(schclass=class_object))
        for i in attendance_objects:
            i.formatted_datetime = i.attendance_datetime.astimezone(timezone_PH).strftime("%B %d, %Y - %I:%M:%S %p")
        context['attendance_objects'] = attendance_objects

        grade_object = Grades.objects.get(Q(student=student_object) & Q(schclass=class_object))
        context['grade_object'] = grade_object

    except UserExt.DoesNotExist:
        context['error'] = 'the student is not yet joining ' \
                           'this class or is not yet verified by the instructor'
    except SchClass.DoesNotExist:
        context['error'] = 'This class doesn\'t exists or is not yet verified'

    return render(request, 'GAMS_webapp/class_parent_view.html', context=context)


@ login_required
def parent_profile_view(request, parent_id):
    userext = get_userext_object(request.user)
    context = {
        'userext': userext
    }
    try:
        parent_object = UserExt.objects.get(id=parent_id)
        parent_profile = UserProfile.objects.get(user=parent_object)

        context['formatted_id'] = format_id(parent_object.user.username)
        context['parent_object'] = parent_object
        context['parent_profile'] = parent_profile

    except UserExt.DoesNotExist:
        context['error'] = 'This parent doesn\'t exists'

    return render(request, 'GAMS_webapp/parent_profile_view.html', context=context)

