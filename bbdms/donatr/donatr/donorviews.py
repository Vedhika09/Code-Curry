from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from django.contrib.auth import  logout,login,authenticate
from django.contrib.auth.decorators import login_required
from bbdmsapp.models import CustomUser,Bloodgroup,DonorReg,BloodRequest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
User = get_user_model()


def DONORSIGNUP(request):
    bg = Bloodgroup.objects.all()

    if request.method == "POST":
        try:
            pic = request.FILES.get('pic')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            mobno = request.POST.get('mobno')
            age = int(request.POST.get("age")) if request.POST.get("age") else None
            bg_id = request.POST.get('bg_id')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            password = request.POST.get('password')

            if not all([first_name, last_name, username, email, mobno, age, bg_id, gender, address, password]):
                messages.error(request, "All fields are required.")
                return redirect('donorsignup')

            if CustomUser.objects.filter(email=email).exists():
                messages.warning(request, 'Email already exists')
                return redirect('donorsignup')

            if CustomUser.objects.filter(username=username).exists():
                messages.warning(request, 'Username already exists')
                return redirect('donorsignup')

            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                user_type=2,
                profile_pic=pic,
            )
            user.set_password(password)
            user.save()

            bg_instance = Bloodgroup.objects.get(id=int(bg_id))

            blooddonor = DonorReg(
                admin=user,
                age=age,
                mobilenumber=mobno,
                bloodgroup=bg_instance,
                gender=gender,
                address=address,
            )
            blooddonor.save()

            messages.success(request, 'Signup Successful! Please login to continue.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Error during signup: {e}")
            return redirect('donorsignup')

    return render(request, 'donor/donor-signup.html', {'bg': bg})



@login_required(login_url='/')
def BLOODREQUESTDETAILS(request):
    donor_admin = request.user
    donor_id = DonorReg.objects.get(admin=donor_admin)
    bloodreq = BloodRequest.objects.filter(donid=donor_id)
    context = {'bloodreq':bloodreq,

    }
    return render(request,'donor/view-request.html',context)

login_required(login_url='/')
def DONORPROFILE(request):
    bg = Bloodgroup.objects.all()
    donor = DonorReg.objects.get(admin = request.user.id)
    context = {
        "donor":donor,
        "bg":bg,
    }
    return render(request,'donor/donor-profile.html',context)

@login_required(login_url='/')
def DONOR_PROFILE_UPDATE(request):
    try:
        customuser = CustomUser.objects.get(id=request.user.id)
        donor = DonorReg.objects.get(admin=request.user.id)
    except ObjectDoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('donor-profile')

    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        age = request.POST.get('age')
        mobilenumber = request.POST.get('mobilenumber')
        bloodgroup_id = request.POST.get('bloodgroup')
        gender = request.POST.get('gender')
        address = request.POST.get('address')

        try:
            if first_name:
                customuser.first_name = first_name
            if last_name:
                customuser.last_name = last_name
            if profile_pic:
                customuser.profile_pic = profile_pic

            if age:
                donor.age = age
            if mobilenumber:
                donor.mobilenumber = mobilenumber
            if bloodgroup_id:
                donor.bloodgroup = Bloodgroup.objects.get(id=bloodgroup_id)
            if gender:
                donor.gender = gender
            if address:
                donor.address = address

            customuser.save()
            donor.save()

            messages.success(request, "Your profile has been updated successfully")
            return redirect('/DonorProfile/?updated=1')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    # Whether GET request or POST failure, render with context
    bg = Bloodgroup.objects.all()
    context = {
        "donor": donor,
        "bg": bg
    }
    return render(request, 'donor/donor-profile.html', context)
