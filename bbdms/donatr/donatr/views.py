from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from bbdmsapp.models import CustomUser, Bloodgroup, DonorReg, Contact, BloodRequest

User = get_user_model()

def BASE(request):
    return render(request, 'base.html')

def LOGIN(request):
    return render(request, 'login.html')

def doLogout(request):
    logout(request)
    return redirect('login')

def doLogin(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user is not None:
            login(request, user)
            user_type = user.user_type
            return redirect('dashboard')  # Redirect all user types to dashboard
        else:
            messages.error(request, 'Username or Password is not valid')
            return redirect('login')
    else:
        messages.error(request, 'Username or Password is not valid')
        return redirect('login')

@login_required(login_url='/')
def DASHBOARD(request):
    context = {
        "bg_count": Bloodgroup.objects.count(),
        "donor_count": DonorReg.objects.count(),
        "br_count": BloodRequest.objects.count(),
        "contact_count": Contact.objects.count(),
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='/')
def SEARCH_DONOR(request):
    bgrp = Bloodgroup.objects.all()
    searchdonor = None

    if request.method == "GET":
        bloodgroup = request.GET.get('bloodgroup')
        location = request.GET.get('location')

        if bloodgroup and location:
            searchdonor = DonorReg.objects.filter(
                bloodgroup__bloodgroup=bloodgroup,
                address__icontains=location
            )
            if not searchdonor.exists():
                messages.info(request, "No donor found for the selected criteria.")

    return render(request, 'search.html', {
        'bgrp': bgrp,
        'search': searchdonor
    })

@login_required(login_url='/')
def PROFILE(request):
    try:
        user = CustomUser.objects.get(id=request.user.id)
        donor = DonorReg.objects.get(admin=request.user)
        bloodgroups = Bloodgroup.objects.all()
    except DonorReg.DoesNotExist:
        messages.error(request, "No donor profile found.")
        return redirect('dashboard')

    context = {
        "user": user,
        "donor": donor,
        "bg": bloodgroups,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='/')
def DONOR_PROFILE_UPDATE(request):
    donor = DonorReg.objects.get(admin=request.user)
    user = request.user  # CustomUser

    if request.method == "POST":
        # User fields
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        profile_pic = request.FILES.get("profile_pic")

        # DonorReg fields
        age = request.POST.get("age")
        mobilenumber = request.POST.get("mobilenumber")
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        bloodgroup_id = request.POST.get("bloodgroup")

        # Update CustomUser model
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if profile_pic:
            user.profile_pic = profile_pic
        user.save()

        # Update DonorReg model
        if age:
            donor.age = age
        if mobilenumber:
            donor.mobilenumber = mobilenumber
        if gender:
            donor.gender = gender
        if address:
            donor.address = address
        if bloodgroup_id:
            try:
                bg = Bloodgroup.objects.get(id=bloodgroup_id)
                donor.bloodgroup = bg
            except Bloodgroup.DoesNotExist:
                messages.error(request, "Invalid blood group selected.")

        donor.save()
        messages.success(request, "Profile updated successfully")
        return redirect('profile')

    return redirect('profile')

@login_required(login_url='/')
def CHANGE_PASSWORD(request):
    if request.method == "POST":
        current = request.POST["cpwd"]
        new_pas = request.POST['npwd']
        user = User.objects.get(id=request.user.id)
        un = user.username

        if user.check_password(current):
            user.set_password(new_pas)
            user.save()
            messages.success(request, 'Password changed successfully!')

            # Re-login the user
            user = User.objects.get(username=un)
            login(request, user)
        else:
            messages.error(request, 'Current password is incorrect!')
            return redirect("change_password")

    data = User.objects.get(id=request.user.id)
    return render(request, 'change-password.html', {"data": data})
