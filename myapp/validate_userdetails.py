import re

class Validate_data:
    def __init__(self, email, password):

        self.email = email
        self.password = password
        self.error_dict = {'all_correct': True}

    def validate_all(self):

        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', self.email):
            self.error_dict['all_correct'] = False
            self.error_dict['email_error'] = "Email address is not valid"
        
        if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', self.password):
            self.error_dict['all_correct'] = False
            self.error_dict['password_error'] = "Password must contain at least 8 characters, including both letters and digits"
            
        return self.error_dict    
    
    
