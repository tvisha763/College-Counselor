def store_in_session(request, page_identifier, role, message):
    session_key = f'chat_{page_identifier}'
    history = request.session.get(session_key, [])
    history.append({'role': role, 'message': message})
    request.session[session_key] = history

def get_session_history(request, page_identifier):
    session_key = f'chat_{page_identifier}'
    return request.session.get(session_key, [])
