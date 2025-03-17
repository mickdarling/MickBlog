from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from core.models import SiteConfig

def contact(request):
    """Contact form view"""
    site = SiteConfig.get()
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Create contact object but don't save yet
            contact = form.save(commit=False)
            
            # Save IP and user agent for security
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            contact.ip_address = ip
            contact.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Save the contact message
            contact.save()
            
            # Add success message and redirect
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact:success')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'site': site,
    }
    
    return render(request, 'contact/contact.html', context)

def contact_success(request):
    """Success page after contact form submission"""
    site = SiteConfig.get()
    
    context = {
        'site': site,
    }
    
    return render(request, 'contact/success.html', context)