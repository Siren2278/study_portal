from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from . forms import *
from django.views import generic
#from googleapiclient.discovery import build
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from decouple import config


def custom_logout(request):
    logout(request)
    return redirect('login')

# Create your views here.
@login_required
def home(request):
    dashboard_items_first = [
    {'url': 'notes', 'icon': 'fa-sticky-note', 'title': 'Notes', 'description': 'Create and store personal notes for future reference'},
    {'url': 'homework', 'icon': 'fa-tasks', 'title': 'Homework', 'description': 'Track assignments with priority-based deadline management'},
    {'url': 'youtube', 'icon': 'fa-youtube', 'title': 'YouTube', 'description': 'Search and discover educational video content'},
    {'url': 'todo', 'icon': 'fa-list-alt', 'title': 'To Do', 'description': 'Organize daily tasks and track your progress'}
    ]

    dashboard_items_second = [
        {'url': 'books', 'icon': 'fa-book', 'title': 'Books', 'description': 'Browse curated book collections and resources'},
        {'url': 'dictionary', 'icon': 'fa-language', 'title': 'Dictionary', 'description': 'Instant word definitions for comprehensive learning'},
        {'url': 'wiki', 'icon': 'fa-wikipedia-w', 'title': 'Wikipedia', 'description': 'Quick research for academic assignments'},
        {'url': 'conversion', 'icon': 'fa-exchange-alt', 'title': 'Conversion', 'description': 'Easy measurement and unit conversions'}
    ]
    
    return render(request, 'dashboard/home.html', {
        'dashboard_items_first': dashboard_items_first,
        'dashboard_items_second': dashboard_items_second
    })

@login_required
def notes(request):
    if(request.method == 'POST'):
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
        messages.success(request, f"Notes Added from {request.user.username} Successfully!")
        form = NotesForm()
    else:
        form = NotesForm()

    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form':form}
    return render(request, 'dashboard/notes.html', context)

# message for deleting a note
@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect('notes')

class NotesDetailView(generic.DetailView):
    model = Notes

def update_note(request, pk):
    """
    View to update an existing note.
    
    Parameters:
    - request: HTTP request object
    - pk: Primary key of the note to be updated
    
    Returns:
    - Rendered update note form or redirects after successful update
    """
    # Get the specific note or return 404 if not found
    note = get_object_or_404(Notes, id=pk, user=request.user)
    
    if request.method == 'POST':
        # Process the form submission
        form = NotesForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated successfully!')
            return redirect('notes-detail', pk)
    else:
        # Display the form with existing note data
        form = NotesForm(instance=note)
    
    context = {
        'form': form,
        'note': note
    }
    return render(request, 'dashboard/update_note.html', context)

@login_required
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST('is_finished')
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            
            homework = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )
            homework.save()
            messages.success(request, f'Homework Added from {request.user.username}!!')
            form = HomeworkForm()
    else:
        form = HomeworkForm()

    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {'homeworks':homework, 'homework_done': homework_done, 'form': form}
    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect('homework')

@login_required
def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data['text']  # Correctly fetch the search query

            # Get the API key from the environment
            api_key = config('API_KEY', default=None)

            if not api_key:
                messages.error(request, "API key is not configured!")
                return render(request, 'dashboard/youtube.html', {'form': form})

            url = "https://youtube.googleapis.com/youtube/v3/search"
            headers = {'Referer': 'http://127.0.0.1:8000'}
            params = {
                'q': search_query,
                'part': 'snippet',
                'maxResults': 10,
                'type': 'video',
                'key': api_key,  # Use the secure API key
            }

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()

                search_response = response.json()
                result_list = []
                for item in search_response.get('items', []):
                    video_id = item['id'].get('videoId', '')
                    if video_id:
                        video = {
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'thumbnail': item['snippet']['thumbnails']['high']['url'],
                            'video_id': video_id,
                            'link': f"https://www.youtube.com/watch?v={video_id}",
                            'channel': item['snippet']['channelTitle'],
                            'published': item['snippet']['publishedAt'],
                        }
                        result_list.append(video)

                context = {'form': form, 'results': result_list}
                return render(request, 'dashboard/youtube.html', context)

            except requests.RequestException as e:
                messages.error(request, f"Error fetching YouTube results: {str(e)}")
    else:
        form = DashboardForm()

    return render(request, 'dashboard/youtube.html', {'form': form})


@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST('is_finished')
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                description = request.POST['description'],
                is_finished = finished
            )
            todos.save()
            messages.success(request, f"Todo Added from {request.user.username} Successfully!!")
            form = TodoForm()
    else:
        form = TodoForm()
        
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False

    context = {
        'todos': todo,
        'form': form,
        'todos_done': todos_done

    }
    return render(request, 'dashboard/todo.html', context)

@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request, pk=None):
    todo = get_object_or_404(Todo, id=pk)
    todo.delete()
    return redirect('todo')


def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = request.POST['text']
            url = f"https://www.googleapis.com/books/v1/volumes?q={text}&maxResults=10"
            
            try:
                r = requests.get(url)
                r.raise_for_status()  # Raise an exception for bad responses
                answer = r.json()
                
                result_list = []
                for item in answer.get('items', []):
                    volume_info = item.get('volumeInfo', {})
                    result_dict = {
                        'title': volume_info.get('title', 'No Title'),
                        'subtitle': volume_info.get('subtitle', ''),
                        'description': volume_info.get('description', 'No description available'),
                        'page_count': volume_info.get('pageCount', 'Unknown'),
                        'categories': volume_info.get('categories', ['No Categories']),
                        'rating': volume_info.get('averageRating', 'Not Rated'),
                        'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                        'preview_link': volume_info.get('previewLink', ''),
                        'info_link': volume_info.get('infoLink', ''),
                        'authors': volume_info.get('authors', ['Unknown Author'])
                    }
                    result_list.append(result_dict)
                
                context = {
                    'form': form,
                    'results': result_list,
                }
                return render(request, 'dashboard/books.html', context)
            
            except requests.RequestException as e:
                messages.error(request, f"Error fetching books: {e}")
    
    form = DashboardForm()
    return render(request, 'dashboard/books.html', {'form': form})

def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = f'https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}'
        
        try:
            r = requests.get(url)
            r.raise_for_status()  # Raise an exception for bad HTTP responses
            answer = r.json()
            
            # Safe extraction with .get() method
            phonetics = answer[0].get('phonetics', [{}])[0].get('text', '')
            audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
            definition = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', '')
            example = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('example', '')
            synonyms = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('synonyms', [])

            if audio and not audio.startswith(('http:', 'https:')):
                audio = f'https:{audio}'
            
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example or 'No example available',
                'synonyms': synonyms
            }
        except requests.RequestException as e:
            context = {
                'form': form,
                'error': f'API request failed: {str(e)}'
            }
        except (KeyError, IndexError) as e:
            context = {
                'form': form,
                'error': 'Word not found or invalid response'
            }
    else:
        form = DashboardForm()
        context = {
            "form": form
        }
    
    return render(request, 'dashboard/dictionary.html', context)

def wiki(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            try:
                search = wikipedia.page(text)
                context = {
                    'form': form,
                    'title': search.title,
                    'link': search.url,
                    'details': search.summary
                }
            except wikipedia.exceptions.DisambiguationError as e:
                context = {
                    'form': form,
                    'error': f"Multiple results found. Did you mean: {', '.join(e.options[:5])}"
                }
            except (wikipedia.exceptions.PageError, wikipedia.exceptions.WikipediaException):
                context = {
                    'form': form,
                    'error': f"No Wikipedia page found for '{text}'"
                }
        else:
            context = {
                'form': form,
                'error': 'Invalid input'
            }
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
        context = {
            "form": form
        }
    return render(request, 'dashboard/wiki.html', context)


def conversion(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        if form.is_valid():
            measurement_type = form.cleaned_data['measurement']
            
            if measurement_type == 'length':
                measurement_form = ConversionLengthForm()
                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input': True,
                    'conversion_type': 'length'
                }
            
            elif measurement_type == 'mass':
                measurement_form = ConversionMassForm()
                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input': True,
                    'conversion_type': 'mass'
                }
            
            return render(request, 'dashboard/conversion.html', context)
        
        # Handle conversion calculation
        conversion_type = request.POST.get('conversion_type')
        if conversion_type == 'length':
            measurement_form = ConversionLengthForm(request.POST)
        elif conversion_type == 'mass':
            measurement_form = ConversionMassForm(request.POST)
        else:
            return redirect('conversion')
        
        if measurement_form.is_valid():
            first = measurement_form.cleaned_data['measure1']
            second = measurement_form.cleaned_data['measure2']
            input_value = measurement_form.cleaned_data['input']
            
            answer = ''
            if input_value is not None:
                if conversion_type == 'length':
                    if first == 'yard' and second == 'foot':
                        answer = f'{input_value} yard = {input_value * 3} foot'
                    elif first == 'foot' and second == 'yard':
                        answer = f'{input_value} foot = {input_value / 3} yard'
                
                elif conversion_type == 'mass':
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input_value} pound = {input_value * 0.453592} kilogram'
                    elif first == 'kilogram' and second == 'pound':
                        answer = f'{input_value} kilogram = {input_value * 2.2062} pound'
            
            context = {
                'form': ConversionForm(initial={'measurement': conversion_type}),
                'm_form': measurement_form,
                'input': True,
                'conversion_type': conversion_type,
                'answer': answer
            }
            return render(request, 'dashboard/conversion.html', context)
    
    else:
        form = ConversionForm()
    
    context = {
        'form': form,
        'input': False
    }
    return render(request, 'dashboard/conversion.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account Created for {username} Successfully!!")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'dashboard/register.html', context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    
    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done
    }
    return render(request, 'dashboard/profile.html', context)