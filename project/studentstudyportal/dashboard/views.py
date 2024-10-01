from django.shortcuts import redirect, render # type: ignore
from .models import Notes
from . forms import *
from django.contrib import messages
from django.views import generic
from django.template.context_processors import csrf
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required

from django.forms.widgets import FileInput
from django.db.models.query import RawQuerySet
from django.views.generic import DetailView






# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')
@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(
                user=request.user,
                title=request.POST['title'],
                description=request.POST['description']  # Corrected key
            )
            notes.save()
            print("Form is valid!")
            messages.success(request, f"Notes added from {request.user.username} successfully.")
    else:
        form = NotesForm()
        notes = Notes.objects.all()
        print(form.errors)

    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_notes(request, pk=None):
    note = Notes.objects.get(id=pk)
    note.delete()  # Call the delete method to remove the note
    messages.success(request, f"Note '{note.title}' deleted successfully.")  # Optional: Add a success message
    return redirect("notes")

class NoteDetailView(DetailView):
    model = Notes
    template_name = 'dashboard/note_detail.html'

@login_required
def homework(request):
    form = HomeworkForm()  # Initialize the form outside the POST block

    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST.get('is_finished', 'off') == 'on'  # Simplified 'finished' logic
            except KeyError:
                finished = False

            homeworks = Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished,
            )
            homeworks.save()
            messages.success(request, f'Homework added by {request.user.username}!')
    
    # Fetch homework for the user
    homework = Homework.objects.filter(user=request.user)
    
    # Determine if any homework exists
    homework_done = len(homework) == 0
    
    context = {
        'homeworks': homework,
        'homeworks_done': homework_done,
        'form': form,  # Make sure form is passed to the template
    }

    return render(request, 'dashboard/homework.html', context)
@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
         homework.is_finished = False

    else:
        homework.is_finished= True
    homework.save()
    return redirect('homework')
@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

def youtube(request):
    if request.method == "POST":
        form = Dashboardform(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']

            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']

            result_dict['description'] = desc
            result_list.append(result_dict) 
            context = {
                'form':form,
                'results':result_list
            } 
        return   render(request,'dashboard/youtube.html',context)     

    else:
         form = Dashboardform()

   
    context = {'form':form}

    return render(request,"dashboard/youtube.html",context)
@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else :
                    finished = False
            except:
                finished = False
            todos = Todo(
                user =request.user,
                title =  request.POST['title'],
                is_finished = finished
            )
            todos.save()
            messages.success(request,f"Todo added from {request.user.username}")
    else:
        form = TodoForm()
        
    todo = Todo.objects.filter(user=request.user)
    if len(todo)== 0:
        todos_done = True
    else:
       todos_done = False 
    context = {
        'form':form,
        'todos':todo,
        'todos_done':todos_done

        
    }
    return render(request,'dashboard/todo.html',context)
@login_required
def update_todo(request,pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')
@login_required
def delete_todo(request,pk:None):
    Todo.objects.get(id=pk)
    return redirect('todo')

def books(request):
    if request.method == "POST":
        form = Dashboardform(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        
        result_list = []
        for i in range(10):
            result_dict = {
               
                'title':answer['items'][i]['volumeInfo']['title'],
               'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
               'description':answer['items'][i]['volumeInfo'].get('description'),
               'count':answer['items'][i]['volumeInfo'].get('pageCount'),
               'categories':answer['items'][i]['volumeInfo'].get('categories'),
               'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
               'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail', 'default_thumbnail_url'),


               'preview':answer['items'][i]['volumeInfo'].get('previewLink')

            }
            
            result_list.append(result_dict) 
            context = {
                'form':form,
                'results':result_list
            } 
        return   render(request,'dashboard/books.html',context)     

    else:
         form = Dashboardform()

   
    context = {'form':form}

    return render(request,"dashboard/books.html",context)

  

def dictionary(request):
    form = Dashboardform()

    if request.method == "POST":
        form = Dashboardform(request.POST)
        text = request.POST.get('text')  # Safely retrieve the 'text' value from the form
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{text}"
        
        try:
            r = requests.get(url)
            r.raise_for_status()  # Raises HTTPError if the response contains a bad status code

            # Parse JSON response
            answer = r.json()

            # Safely access data with checks
            phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'No phonetics available')
            audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
            definition = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', 'No definition available')
            example = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('example', 'No example available')
            synonyms = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('synonyms', [])

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms
            }
        except (requests.exceptions.HTTPError, IndexError, KeyError, requests.exceptions.JSONDecodeError):
            context = {
                'form': form,
                'input': text,
                'error': 'Unable to fetch dictionary data. Please try again or check the word.',
            }
        return render(request, "dashboard/dictionary.html", context)

    # GET request: Just render the form
    context = {'form': form}
    return render(request, 'dashboard/dictionary.html', context)

def wiki(request):
    if request.method == 'POST':
         
         text = request.POST['text']
         form = Dashboardform(request.POST)
         search = wikipedia.page(text)
         context = {
             'form':form,
             'title':search.title,
             'link':search.url,
             'details':search.summary

        } 
         return render(request,"dashboard/wiki.html",context)
    else:
     
     form = Dashboardform()
     context = {
         'form':form
     }
    return render(request, 'dashboard/wiki.html',context)


def conversion(request):
    form = ConversionForm()
    context = {
        'form': form,
        'input': False,
    }

    # Check if the request method is POST
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        measurement_type = request.POST.get('measurement')
        answer = ''
        input_value = request.POST.get('input')

        # Determine which specific conversion form to use
        if measurement_type == 'length':
            measurement_form = ConversionLengthForm()
        elif measurement_type == 'mass':
            measurement_form = ConversionMassForm()
        else:
            measurement_form = None

        # Ensure the appropriate form is available
        if measurement_form:
            context.update({
                'form': form,
                'm_form': measurement_form,
                'input': True
            })

            if input_value:
                try:
                    input_value = float(input_value)  # Convert input value to float
                    first_measure = request.POST.get('measure1')
                    second_measure = request.POST.get('measure2')

                    # Check if both measurement units are provided
                    if not first_measure or not second_measure:
                        context['error'] = "Please select both units of measurement."
                    else:
                        # Length conversion logic
                        if measurement_type == 'length':
                            if first_measure == 'yard' and second_measure == 'foot':
                                answer = f'{input_value} yard = {input_value * 3} foot'
                            elif first_measure == 'foot' and second_measure == 'yard':
                                answer = f'{input_value} foot = {input_value / 3} yard'
                            else:
                                context['error'] = "Invalid length units selected."

                        # Mass conversion logic
                        elif measurement_type == 'mass':
                            if first_measure == 'pound' and second_measure == 'kilogram':
                                answer = f'{input_value} pound = {input_value * 0.453592} kilogram'
                            elif first_measure == 'kilogram' and second_measure == 'pound':
                                answer = f'{input_value} kilogram = {input_value * 2.20462} pound'
                            else:
                                context['error'] = "Invalid mass units selected."

                        # If a valid answer is found, update the context
                        if answer:
                            context['answer'] = answer

                except ValueError:
                    context['error'] = "Please enter a valid numerical input."

    return render(request, 'dashboard/conversion.html', context)
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account Created for {username} !!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    context = {
        'form':form
       }
    return render(request,"dashboard/register.html",context)
@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks) == 0:
        homework_done = True

    else:
        homework_done = False

    if len(todos) == 0:
        todos_done = True

    else:
        todos_done = False

    context = {
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todos_done':todos_done

    }

    return render(request,"dashboard/profile.html",context)


                

     

     

