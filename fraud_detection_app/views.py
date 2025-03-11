from django.shortcuts import render
from django.views import View
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView
from .models import CustomUser,AppScanSummary,SafeAppSummary,FraudAppSummary
from .forms import UserRegistrationForm, UserLoginForm,AdminLoginForm
from django.http import JsonResponse
import requests
from fraud_detection_app.models import ScannedApp
from google_play_scraper import app
from google_play_scraper import search
import time
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator



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

# def fetch_app_data(package_name):
#     try:
#         result = app(package_name)
        
#         # Extracting all available details
#         app_data = {
#             "app_name": result.get("title", "N/A"),
#             "description": result.get("description", "N/A"),
#             "developer": result.get("developer", "N/A"),
#             "developer_website": result.get("developerWebsite", "N/A"),
#             "developer_email": result.get("developerEmail", "N/A"),
#             "category": result.get("genre", "N/A"),
#             "category_id": result.get("genreId", "N/A"),
#             "icon": result.get("icon", ""),
#             "header_image": result.get("headerImage", ""),
#             "video": result.get("video", "N/A"),
#             "video_image": result.get("videoImage", "N/A"),
#             "screenshots": result.get("screenshots", []),
#             "content_rating": result.get("contentRating", "N/A"),
#             "price": result.get("price", "Free"),
#             "currency": result.get("currency", "N/A"),
#             "free": result.get("free", False),
#             "installs": result.get("installs", "N/A"),
#             "min_installs": result.get("minInstalls", "N/A"),
#             "max_installs": result.get("maxInstalls", "N/A"),
#             "score": result.get("score", "N/A"),
#             "ratings": result.get("ratings", "N/A"),
#             "reviews": result.get("reviews", "N/A"),
#             "size": result.get("size", "Unknown"),
#             "version": result.get("version", "N/A"),
#             "released": result.get("released", "N/A"),
#             "updated": result.get("updated", "N/A"),
#             "android_version": result.get("androidVersion", "N/A"),
#             "android_version_text": result.get("androidVersionText", "N/A"),
#         }
        
#         return app_data
    
#     except Exception as e:
#         return {"error": str(e)}








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


    


class UserDashboardView(View):
    def get(self, request, *args, **kwargs):
        # Restrict admin users from accessing the dashboard
        if request.user.is_authenticated and request.user.user_type == "admin":
            return redirect('userlogin_view')  # Redirect admin users

        # Default values to prevent UnboundLocalError
        safe_apps = fraudulent_apps = []
        total_scanned_apps = 0
        fraudulent_apps_count = 0

        # If user is authenticated and is a regular user
        if request.user.is_authenticated and request.user.user_type == "user":
            safe_apps = ScannedApp.objects.filter(user=request.user, security_score__gte=50)
            fraudulent_apps = ScannedApp.objects.filter(user=request.user, security_score__lt=50)

            total_scanned_apps = ScannedApp.objects.filter(user=request.user).count()
            fraudulent_apps_count = fraudulent_apps.count()

        return render(request, 'user_dashboard.html', {
            'safe_apps': safe_apps,
            'fraudulent_apps': fraudulent_apps,
            'total_scanned_apps': total_scanned_apps,
            'fraudulent_apps_count': fraudulent_apps_count
        })

class ScanAppView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'user':
            messages.error(request, "You are not authorized to access this page.")
           
            return redirect('userdashboard_view')  # Redirect all unauthorized users
        scanned_apps = ScannedApp.objects.filter(user=request.user)
        return render(request, 'scan_app.html',{'scanned_apps': scanned_apps})
    
def search_apps(request):
    query = request.GET.get("q", "")  # Get search query
    if query:
        results = search(query)[:10]  # Fetch top 10 matching apps
        app_list = [
            {
                "title": app["title"],
                "package_name": app["appId"],
                "icon": app["icon"],
                "rating": app.get("score", "N/A"),
                "developer": app["developer"]
            }
            for app in results
        ]
        return JsonResponse({"apps": app_list})
    return JsonResponse({"apps": []})

def calculate_security_score(app_data):
    """Calculate security score based on rating, installs, and updates."""
    score = 50  # Start with a base score

    # Ensure rating is a float
    rating = float(app_data.get("score", 0) or 0)
    if rating >= 4.5:
        score += 20
    elif rating >= 4.0:
        score += 15
    elif rating >= 3.5:
        score += 10
    elif rating >= 3.0:
        score += 5
    else:
        score -= 10  # Penalize low-rated apps

    # Increase score for high installs
    installs = app_data.get("installs", "0").replace(",", "").replace("+", "")
    try:
        installs = int(installs)
        if installs >= 100_000_000:
            score += 20
        elif installs >= 10_000_000:
            score += 15
        elif installs >= 1_000_000:
            score += 10
        elif installs >= 100_000:
            score += 5
        else:
            score -= 10  # Penalize low installs
    except ValueError:
        score -= 5  # Penalize if installs are missing

    # Ensure updated field is a string
    updated = str(app_data.get("updated", "N/A"))
    if "2024" in updated or "2023" in updated:
        score += 10  # Recent updates improve security

    # Cap score between 0 and 100
    score = max(0, min(score, 100))

    return score


@login_required
def app_details_view(request):
    package_name = request.GET.get('package')

    if not package_name:
        return render(request, 'app_details.html', {'error': 'No package name provided'})

    try:
        app_data = app(package_name)  # Fetch app details
        security_score = calculate_security_score(app_data)  # Compute security score

        app_info = {
            "app_name": app_data.get("title", "N/A"),
            "developer": app_data.get("developer", "N/A"),
            "icon": app_data.get("icon", ""),
            "installs": app_data.get("installs", "N/A"),
            "rating": app_data.get("score", "N/A"),
            "version": app_data.get("version", "N/A"),
            "updated": app_data.get("updated", "N/A"),
            "description": app_data.get("description", "N/A"),
            "app_url": f"https://play.google.com/store/apps/details?id={package_name}",
            "security_score": security_score
        }

        # Save scanned app details in the database
        scanned_app, created = ScannedApp.objects.get_or_create(
            user=request.user, package_name=package_name,
            defaults={
                "app_name": app_info["app_name"],
                "developer": app_info["developer"],
                "icon": app_info["icon"],
                "installs": app_info["installs"],
                "rating": app_info["rating"],
                "version": app_info["version"],
                "updated": app_info["updated"],
                "description": app_info["description"],
                "security_score": security_score
            }
        )

        if not created:
            # If app already exists, update its details
            scanned_app.app_name = app_info["app_name"]
            scanned_app.developer = app_info["developer"]
            scanned_app.icon = app_info["icon"]
            scanned_app.installs = app_info["installs"]
            scanned_app.rating = app_info["rating"]
            scanned_app.version = app_info["version"]
            scanned_app.updated = app_info["updated"]
            scanned_app.description = app_info["description"]
            scanned_app.security_score = security_score
            scanned_app.save()

        return render(request, 'app_details.html', {'app': app_info})

    except Exception as e:
        return render(request, 'app_details.html', {'error': str(e)})
    
def scanning_view(request):
    package_name = request.GET.get('package', '')
    return render(request, 'scanning.html', {'package_name': package_name})

    
# class ScanningView(View):
#     def get(self, request, *args, **kwargs):
#         package_name = request.GET.get("package", "")  # Get package name from query parameters
#         context = {
#             "package_name": package_name,  # Pass it to the template
#         }
#         return render(request, "scanning.html", context)
     
class ResultView(View):
     def get(self,request,*args,**kwargs):
        return render(request,'result.html')
     
class AdminLoginView(View):
    def get(self, request):
        form = AdminLoginForm()
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

CustomUser = get_user_model()

@method_decorator(login_required, name='dispatch')
class AdminDashboardView(View):
    def get(self, request, *args, **kwargs):
        if request.user.user_type != 'admin':  # Allow only admin users
            return render(request, '403.html')  # Create a 403 Forbidden page if needed
        scanned_apps=ScannedApp.objects.all()
        total_scanned = scanned_apps.count()
        users = CustomUser.objects.all()  # Fetch all users
        total_users = CustomUser.objects.count()
        return render(request, 'admin_dashboard.html', {'users': users , 'total_users': total_users,'total_scanned': total_scanned})

    
    
class UserManagmentView(View):
    def get(self,request,*args,**kwargs):
        users = CustomUser.objects.all() 
        return render(request, 'user_managment.html',{'users': users })
    
class ApplicationView(View):
    def get(self,request,*args,**kwargs):
        # Fetch apps from multiple categories
        security_apps = search("security", lang="en", country="us", n_hits=25)
        social_apps = search("social", lang="en", country="us", n_hits=25)
        games_apps = search("games", lang="en", country="us", n_hits=25)
        finance_apps = search("finance", lang="en", country="us", n_hits=25)

        # Combine all apps into one list
        all_apps = security_apps + social_apps + games_apps + finance_apps

        # Paginate results (10 apps per page)
        paginator = Paginator(all_apps, 10)
        page_number = request.GET.get('page')
        page_apps = paginator.get_page(page_number)
        return render(request, 'application.html',{'apps': page_apps})
    
class ActivitiesView(View):
    def get(self,request,*args,**kwargs):
        scanned_apps = ScannedApp.objects.all().order_by('-scanned_at')
        paginator = Paginator(scanned_apps, 10)  # Show 10 per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'activities.html', {'page_obj': page_obj})
    
class AdminLogoutView(View):
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

        return redirect('adminlogin_view')
    