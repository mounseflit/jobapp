from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from account.models import User
import os


class EmployeeRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].required = True
        self.fields['first_name'].label = "First Name:"
        self.fields['last_name'].label = "Last Name:"
        self.fields['password1'].label = "Password:"
        self.fields['password2'].label = "Confirm Password:"
        self.fields['email'].label = "Email:"
        self.fields['gender'].label = "Gender:"
        self.fields['cv'].label = "CV:"

        self.fields['first_name'].widget.attrs.update(
            {
                'placeholder': 'Enter First Name',
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'placeholder': 'Enter Last Name',
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'placeholder': 'Enter Email',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': 'Enter Password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': 'Confirm Password',
            }
        )
        self.fields['cv'].widget.attrs.update(
            {
                'placeholder': 'Enter CV',
            }
        )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'gender', 'cv']

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError("Gender is required")
        return gender
    


    def save(self, commit=True):
            user = super().save(commit=False)
            user.role = "employee"
            cv_file = self.cleaned_data['cv']
            if cv_file:
                # Generate a unique file name
                file_name = f"cv_{user.pk}_{cv_file.name}"

                # Build the file path
                file_path = os.path.join(settings.MEDIA_ROOT, file_name)

                # Save the file
                with open(file_path, 'wb+') as destination:
                    for chunk in cv_file.chunks():
                        destination.write(chunk)

                # Set the cv field to the saved file path
                user.cv = file_path

            if commit:
                user.save()

            return user



class EmployerRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['first_name'].label = "Company Name"
        self.fields['last_name'].label = "Company Address"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"

        self.fields['first_name'].widget.attrs.update(
            {
                'placeholder': 'Enter Company Name',
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'placeholder': 'Enter Company Address',
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'placeholder': 'Enter Email',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': 'Enter Password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': 'Confirm Password',
            }
        )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "employer"
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user = authenticate(email=email, password=password)
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("User Does Not Exist.")

            if not user.check_password(password):
                raise forms.ValidationError("Password Does not Match.")

            if not user.is_active:
                raise forms.ValidationError("User is not Active.")

        return cleaned_data

    def get_user(self):
        return self.user


class EmployeeProfileEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update(
            {
                'placeholder': 'Enter First Name',
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'placeholder': 'Enter Last Name',
            }
        )
        self.fields['cv'].widget.attrs.update(
            {
                'placeholder': 'Enter CV',
            }
        )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "gender", "cv"]

    def save(self, commit=True):
        user = super().save(commit=False)
        cv_file = self.cleaned_data['cv']
        if cv_file:
            # Generate a unique file name
            file_name = f"cv_{user.pk}_{cv_file.name}"

            # Build the file path
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            # Save the file
            with open(file_path, 'wb+') as destination:
                for chunk in cv_file.chunks():
                    destination.write(chunk)

            # Set the cv field to the saved file path
            user.cv = file_path

        if commit:
            user.save()

        return user