from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from .LinkJoiner import LinkJoiner
import os


# Create your views here.
def upload(request):
    if request.method == 'POST':
            if 'file' not in request.FILES:
                return HttpResponse("Error: No file uploaded!", status=400)
        
            uploaded_file = request.FILES['file']
            variables_list = request.POST.getlist('var[]')
            filtered_variable_list = [value for value in variables_list if value != '']
            
            if not filtered_variable_list:
                return HttpResponse("Error: No variables provided!", status=400)
            
             
            VJoin = LinkJoiner(request,uploaded_file,filtered_variable_list)
            Modified_file_path = VJoin.VarJoiner()
        
            print("Modified_file_path",Modified_file_path)
        
        
            if os.path.exists(Modified_file_path):
                with open(Modified_file_path, 'rb') as file:
                    response = HttpResponse(file.read(), content_type="text/plain")
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(Modified_file_path)}"'
                    request.session.flush()
                    return response
                    
    return render(request,'index.html')
