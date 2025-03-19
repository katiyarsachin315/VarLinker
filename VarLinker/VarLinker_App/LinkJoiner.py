from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import FileUpload
from urllib.parse import urlencode
import os


class LinkJoiner:
    def __init__(self, request, uploaded_file, variable_list):
        self.request = request
        self.valid_extensions = ['txt']
        self.media_root = settings.MEDIA_ROOT
        self.full_path = None
        self.file_path = None
        self.uploaded_file = uploaded_file
        self.variable_list = variable_list
        self.variable_dict  = {}
        self.final_file_path = None
    
    
    def VarJoiner(self):
        File_valid = self.validate_file_extensions()
        if not File_valid:
            return {'state':False, 'Msg':self.Error_List}
        if File_valid:
            self.create_folder()
            self.file_path = os.path.join(self.full_path, self.uploaded_file.name)
            self.variable_dict = self.create_variable_dict(self.variable_list)
            self.final_file_path = self.append_params_to_urls(self.file_path)
        return self.final_file_path           
    
    def validate_file_extensions(self):
        CheckFlag = True
        file_extension = os.path.splitext(self.uploaded_file.name)[1][1:].lower()
        if file_extension not in self.valid_extensions:
            CheckFlag = False
            self.Error_List.append(f"Unsupported file extension '{file_extension}' in file '{self.uploaded_file.name}'.")
        return CheckFlag

    def create_folder(self):
        user_name = "User_name"
        self.upload_obj = FileUpload(Title=user_name)
        self.upload_obj.save()
        formatted_date = self.upload_obj.created_at.strftime('%Y%m%d')
        self.folder_name = f"{formatted_date}_{str(self.upload_obj.uKey)}"
        self.full_path = os.path.join(self.media_root, self.folder_name)
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)
            folder_path = self.folder_name
            self.upload_obj.fullURL = folder_path
            self.upload_obj.save()
            self.save_files(self.full_path)
            self.folder_path = (self.upload_obj.fullURL)
            return True
        else:
            self.Error_List.append(f"Unsupported file extension")
            return False
    
    def save_files(self, Full_folder_path):
        fs = FileSystemStorage(location=Full_folder_path)
        if self.uploaded_file:
            fs.save(self.uploaded_file.name, self.uploaded_file)  # Save file directly
        else:
            print("No file to save.")


    def create_variable_dict(self,variable_list):
        default_values = ['XXXX', 'YYYY', 'ZZZZ', 'AAAA', 'BBBB']
        max_length = min(len(variable_list), 5)

        variable_dict = {}

        for i in range(max_length):
            variable_dict[variable_list[i]] = default_values[i]

        return variable_dict            

    def append_params_to_urls(self, file_path):
        try:
            dir_name, file_name = os.path.split(file_path)
            output_file_path = os.path.join(self.request.get_host(),'media', self.full_path, f"modified_{file_name}")

            with open(file_path, 'r', encoding='utf-8') as file, open(output_file_path, 'w', encoding='utf-8') as output_file:
                for index, line in enumerate(file):
                    if index == 0:
                        continue

                    base_url = line.strip()
                    query_string = urlencode(self.variable_dict)
                    final_url = f"{base_url}&{query_string}"
                    output_file.write(final_url + '\n')
            return output_file_path

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

            
            