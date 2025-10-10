from django import forms
from accounts.models import Profile, Contact

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = '__all__'

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'required': True}),
            'email': forms.EmailInput(attrs={'required': True}),
            'whatsapp': forms.TextInput(attrs={'required': True}),
            'enterprise': forms.TextInput(attrs={'required': True}),}