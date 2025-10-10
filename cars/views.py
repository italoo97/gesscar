from django.shortcuts import render
from cars.models import Car, Brand
from cars.forms import CarModelForm, CarBrandForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from openai_api.client import get_ai_response, get_fallback_response

def index(request):
	return render(request, )

class CarListView(ListView):
	model = Car
	template_name = 'cars.html'
	context_object_name = 'cars'

	def get_queryset(self):
		cars = super().get_queryset().order_by('model')
		search = self.request.GET.get('search')
		if search:
			cars = cars.filter(model__icontains=search)
		return cars

@method_decorator(login_required, name='dispatch')
class NewCarsCreateView(CreateView):
	model = Car
	form_class = CarModelForm
	template_name = "new_car.html"
	success_url = '/cars/'

class CarDetailView(DetailView):
	model = Car
	template_name = 'car_detail.html'

@method_decorator(login_required, name='dispatch')
class CarUpdateView(UpdateView):
	model = Car
	form_class = CarModelForm
	template_name = 'car_update.html'
	success_url = '/cars/'

	def get_success_url(self):
		return reverse_lazy('car_detail', kwargs={'pk': self.object.pk})

@method_decorator(login_required, name='dispatch')
class CarDeleteView(DeleteView):
	model = Car
	template_name = 'car_delete.html'
	success_url = '/cars/'

@method_decorator(login_required, name='dispatch')
class NewBrandCreateView(CreateView):
	model = Brand
	form_class = CarBrandForm
	template_name = "new_brand.html"
	success_url = '/cars/'

@require_POST
@csrf_exempt
def chat_api(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'response': 'Por favor, digite uma mensagem.'})
        
        company_context = f"""
        Você é um assistente virtual da GESSCAR.
        
        Informações importantes:
        - Horário: Segunda a Sexta (8h-18h), Sábado (8h-12h)
        - Local: Rua das Concessionárias, 123 - Centro, São Paulo
        - Telefone: (11) 9999-9999
        - Email: contato@gesscar.com
        - Especialidade: Carros usados e seminovos
        - Serviços: Vendas, financiamento, avaliação de veículos
        
        Pergunta do usuário: {user_message}
        
        Responda de forma amigável, útil e profissional. Não de Informações que ele não pediu, seja direto.
        """
        try:
            response = get_ai_response(company_context, provider='chatgpt')
        except:
            response = get_fallback_response(user_message)
        
        return JsonResponse({'response': response})
        
    except Exception as e:
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)