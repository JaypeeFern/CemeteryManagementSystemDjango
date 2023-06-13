from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["username"].widget.attrs.update({
            'class': 'form-control enterevent',
            'id': 'username_register',
            'onkeyup': 'success()',
            'placeholder': '#',
            'required': ''
        })

        self.fields["password1"].widget.attrs.update({
            'class': 'form-control enterevent',
            'id': 'password1',
            'onkeyup': 'success()',
            'placeholder': '#',
            'required': ''
        })
        
        self.fields["password2"].widget.attrs.update({
            'class': 'form-control enterevent',
            'id': 'password2',
            'onkeyup': 'success()',
            'placeholder': '#',
            'required': ''
        })
        
        self.fields["first_name"].widget.attrs.update({
            'class': 'form-control enterevent',
            'id': 'name',
            'onkeyup': 'success()',
            'placeholder': '#',
            'required': ''
        })
    
    class Meta:
        model = User
        fields=['first_name','username','password1','password2']

class LoginFormAuthentication(AuthenticationForm):
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        
        self.fields["username"].widget.attrs.update({
            'class': 'form-control',
            'id': 'username',
            'aria-describedby': 'usernameHelp',
            'required': '',
            'placeholder': 'SMPI'
        })

        self.fields["password"].widget.attrs.update({
            'class': 'form-control',
            'id': 'password',
            'aria-describedby': 'passwordHelp',
            'required': '',
            'placeholder': 'SMPI'
        })

