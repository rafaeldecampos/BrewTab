from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Brewery


@login_required(login_url='login')
def brewery_list(request):
    """List all breweries owned by the current user."""
    breweries = Brewery.objects.filter(owner=request.user)
    return render(request, 'brewery/brewery_list.html', {'breweries': breweries})


@login_required(login_url='login')
def brewery_create(request):
    """Create a new brewery."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        if not name:
            messages.error(request, 'Brewery name is required.')
            return render(request, 'brewery/brewery_form.html')
        
        if Brewery.objects.filter(name=name).exists():
            messages.error(request, 'A brewery with this name already exists.')
            return render(request, 'brewery/brewery_form.html')
        
        brewery = Brewery.objects.create(name=name, owner=request.user)
        messages.success(request, f'Brewery "{brewery.name}" created successfully.')
        return redirect('brewery:detail', brewery_id=brewery.id)
    
    return render(request, 'brewery/brewery_form.html', {'action': 'Create'})


@login_required(login_url='login')
def brewery_detail(request, brewery_id):
    """View brewery details."""
    brewery = get_object_or_404(Brewery, id=brewery_id)
    
    if brewery.owner != request.user:
        return HttpResponseForbidden('You do not have permission to view this brewery.')
    
    return render(request, 'brewery/brewery_detail.html', {'brewery': brewery})


@login_required(login_url='login')
def brewery_edit(request, brewery_id):
    """Edit brewery details."""
    brewery = get_object_or_404(Brewery, id=brewery_id)
    
    if brewery.owner != request.user:
        return HttpResponseForbidden('You do not have permission to edit this brewery.')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        if not name:
            messages.error(request, 'Brewery name is required.')
            return render(request, 'brewery/brewery_form.html', {'brewery': brewery, 'action': 'Edit'})
        
        if Brewery.objects.filter(name=name).exclude(id=brewery.id).exists():
            messages.error(request, 'A brewery with this name already exists.')
            return render(request, 'brewery/brewery_form.html', {'brewery': brewery, 'action': 'Edit'})
        
        brewery.name = name
        brewery.save()
        messages.success(request, f'Brewery "{brewery.name}" updated successfully.')
        return redirect('brewery:detail', brewery_id=brewery.id)
    
    return render(request, 'brewery/brewery_form.html', {'brewery': brewery, 'action': 'Edit'})


@login_required(login_url='login')
def brewery_delete(request, brewery_id):
    """Delete a brewery."""
    brewery = get_object_or_404(Brewery, id=brewery_id)
    
    if brewery.owner != request.user:
        return HttpResponseForbidden('You do not have permission to delete this brewery.')
    
    if request.method == 'POST':
        brewery_name = brewery.name
        brewery.delete()
        messages.success(request, f'Brewery "{brewery_name}" deleted successfully.')
        return redirect('brewery:list')
    
    return render(request, 'brewery/brewery_confirm_delete.html', {'brewery': brewery})
