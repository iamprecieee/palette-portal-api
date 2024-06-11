def format_error(e):
    error_list = []
    
    for key, value in e.detail.items():
        for error in value:
            if error.code == "required":
                error_list.append(f"{key.title()} is required.")
            elif error.code == "unique":
                        error_list.append(error.capitalize())
                
    if len(error_list) == 1:
        error_list = error_list[0]
        
    return error_list