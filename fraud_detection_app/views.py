from django.shortcuts import render
from django.views import View

# Create your views here.


# class UserLoginView(View):
#     def get(self,request,*args,**kwargs):
#         return render(request, 'user_login.html')
    
# class UserRegisterView(View):
#     def get(self,request,*args,**kwargs):
#         return render(request, 'user_register.html')
    
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView
from .models import CustomUser,AppScanSummary,SafeAppSummary,FraudAppSummary
from .forms import UserRegistrationForm, UserLoginForm,AdminLoginForm
from django.http import JsonResponse
import requests

from google_play_scraper import app
from google_play_scraper import search
import time

def get_all_apps(keyword, num_results=50):
    try:
        all_apps = []
        
        while len(all_apps) < num_results:
            print(f"Fetching apps for keyword: {keyword}...")
            results = search(keyword)

            if not results:  # Stop if no more results
                break

            for app in results:
                all_apps.append({
                    "title": app["title"],
                    "package_name": app["appId"],
                    "icon": app["icon"],
                    "rating": app.get("score", "N/A"),
                    "developer": app["developer"]
                })

                if len(all_apps) >= num_results:
                    break  # Stop if we reach the limit

            time.sleep(2)  # Prevent API rate limits

        return all_apps
    except Exception as e:
        return {"error": str(e)}

# Example: Fetch 50 apps related to "social"
all_apps = get_all_apps("social", 70)

if "error" in all_apps:
    print("Error:", all_apps["error"])
else:
    print(f"Total Apps Found: {len(all_apps)}")
    for app in all_apps:
        print(app["title"])


# def fetch_app_data(package_name):
#     try:
#         result = app(package_name)
#         app_data = {
#             "app_name": result.get("title", "N/A"),  # Use .get() to avoid KeyError
#             "size": result.get("size", "Unknown"),
#             "icon": result.get("icon", ""),
#             "downloads": result.get("installs", "N/A"),
#             "developer": result.get("developer", "N/A"),
#             "version": result.get("version", "N/A"),
#             "rating": result.get("score", "N/A"),
#             "last_updated": result.get("updated", "N/A")
#         }
#         print(result)
#         return app_data
#     except Exception as e:
#         return {"error": str(e)}

# # Example: Fetch details of WhatsApp
# app_details = fetch_app_data("com.whatsapp")
# print(app_details)





def get_third_party_apps(request):
    """Fetch app data from a third-party API."""
    api_url = "https://xkcd.com/info.0.json"  # Replace with actual API URL
    headers = {
        "Authorization": "Bearer YOUR_API_KEY"  # If the API requires authentication
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()
        return JsonResponse(data, safe=False)  # Return the third-party API response
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
    

class TesView(View):
    def get(self, request, *args, **kwargs):
        api_url = "https://api.apis.guru/v2/providers.json"

        try:
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            json_data = response.json()
            data_list = json_data.get("data", [])  # Extract 'data' list safely
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")  
            data_list = []  # Fallback to an empty list

        return render(request, 'test.html', {'data': data_list})
    
class Test2View(View):
    def get(self, request, *args, **kwargs):
        api_url = "https://api.zippopotam.us/us/33162"  # Example ZIP code API

        try:
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            json_data = response.json()

            # Extract data from JSON response
            post_code = json_data.get("post code", "N/A")
            country = json_data.get("country", "N/A")
            state = json_data.get("places", [{}])[0].get("state", "N/A")
            city = json_data.get("places", [{}])[0].get("place name", "N/A")
            latitude = json_data.get("places", [{}])[0].get("latitude", "N/A")
            longitude = json_data.get("places", [{}])[0].get("longitude", "N/A")

            # Format data for template rendering
            data = {
                "post_code": post_code,
                "country": country,
                "state": state,
                "city": city,
                "latitude": latitude,
                "longitude": longitude,
            }

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")  
            data = {"error": "Failed to fetch data from the API."}

        return render(request, 'test2.html', {"data": data})


class UserRegisterView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'user_register.html'
    
    def form_valid(self, form):
        try:
            user = form.save()
            login(self.request, user)
            return redirect('userlogin_view')
        except Exception as e:
            print(f"Registration Error: {e}")
            messages.error(self.request, "An error occurred while registering.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("Form Errors:", form.errors)  # Debugging
        messages.error(self.request, "Invalid registration details. Please correct the errors.")
        return self.render_to_response(self.get_context_data(form=form))

class UserLoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'user_login.html', {'form': form})

    def post(self, request):
        try:
            form = UserLoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('userdashboard_view')
            else:
                messages.error(request, "Invalid username or password.")
        except Exception as e:
            print(f"Login Error: {e}")
            messages.error(request, "An unexpected error occurred during login.")

        return render(request, 'user_login.html', {'form': form})

class UserLogoutView(View):
    def get(self, request):
        try:
            if request.user.is_authenticated:
                print(request.user)  # Print the user to see the status
                logout(request)
                messages.success(request, 'Logout Successful')
            else:
                messages.warning(request, 'You are not logged in.')
        except Exception as e:
            print(f"Logout Error: {e}")
            messages.error(request, "An unexpected error occurred during logout.")

        return redirect('userdashboard_view')

class AdminDashboardView(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'admin_dashboard.html')
    
class AdminLoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'admin_login.html', {'form': form})

    def post(self, request):
        try:
            form = AdminLoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        except Exception as e:
            print(f"Login Error: {e}")
            messages.error(request, "An unexpected error occurred during login.")

        return render(request, 'admin_login.html', {'form': form})
    
# class AdminLoginView(View):
#     def get(self,request,*args,**kwargs):
#         return render(request, 'admin_login.html')
    
class UserManagmentView(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'user_managment.html')
    
class ApplicationView(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'application.html')
    
class ActivitiesView(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'activities.html')
    
class UserDashboardView(View):
    def get(self,request,*args,**kwargs):
        scan_summary, created = AppScanSummary.objects.get_or_create(id=1, defaults={
        "total_apps_scanned": 0,
        "threats_detected": 0,
        "community_reports": 0
         })
        safeapps = SafeAppSummary.objects.all()
        fraudapps=FraudAppSummary.objects.all()
        return render(request,'user_dashboard.html',{ 'scan_summary':scan_summary , 'safeapps':safeapps , 'fraudapps':fraudapps })

class ScanAppView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'scan_app.html')
    
class ScanningView(View):
     def get(self,request,*args,**kwargs):
        return render(request,'scanning.html')
     
class ResultView(View):
     def get(self,request,*args,**kwargs):
        return render(request,'result.html')
    