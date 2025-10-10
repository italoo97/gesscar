from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.forms import ProfileForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .forms import ContactForm
from .models import Contact
from django.views.generic import CreateView
from django.urls import reverse_lazy

@method_decorator(csrf_exempt, name='dispatch')
class ProcessarFormularioView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'index.html'
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        form.save()
        return JsonResponse({'success': True, 'message': 'Formulário enviado com sucesso!'})
    
    def form_invalid(self, form):
        return JsonResponse({
            'success': False, 
            'errors': form.errors,
            'message': 'Por favor, corrija os erros no formulário.'
        })

def auth_page_view(request):
    login_form = AuthenticationForm()
    register_form = UserCreationForm()
    is_register = "register" in request.path
    active_tab = "register" if is_register else "login"

    if request.method == "POST":
        if "username" in request.POST and "password" in request.POST and "password1" not in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, f"Bem-vindo, {user.username}!")
                return redirect("cars_list")
            else:
                messages.error(request, "Usuário ou senha incorretos.")
                active_tab = "login"

        elif "password1" in request.POST and "password2" in request.POST:
            register_form = UserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                messages.success(request, "Cadastro realizado com sucesso! Faça login.")
                active_tab = "login"
            else:
                messages.error(request, "Erro ao cadastrar. Verifique os campos.")
                active_tab = "register"

    context = {
        "login_form": login_form,
        "register_form": register_form,
        "active_tab": active_tab,
    }
    return render(request, "logindinamyc.html", context)

@login_required
def change_view(request):
    if request.method == 'POST':
        change_form = PasswordChangeForm(user=request.user, data=request.POST)
        if change_form.is_valid():
            user = change_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('login')
    else:
        change_form = PasswordChangeForm(user=request.user)
    return render(request, 'change.html', {'change_form': change_form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('cars_list')

@login_required
def profile_view(request):
    return render(request, 'profile.html', {"user": request.user})

@login_required
def edit_profile_view(request):
	if request.method =='POST':
		profile_form = ProfileForm(request.POST, request.FILES)
		if profile_form.is_valid():
			profile_form.save()
			return redirect('cars_list')
	else:
		profile_form = ProfileForm()
	return render(request, 'editprofile.html', {'profile_form': profile_form})


