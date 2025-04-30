def store_in_session(request, page_identifier, role, message):
    session_key = f'chat_{page_identifier}'
    history = request.session.get(session_key, [])
    history.append({'role': role, 'message': message})
    request.session[session_key] = history

def get_session_history(request, page_identifier):
    session_key = f'chat_{page_identifier}'
    return request.session.get(session_key, [])

def get_user_context(user):
    if not user:
        return {}

    return {
        "name": user.name,
        "grade_level": user.grade_level,
        "gpa": user.gpa,
        "intended_major": user.intended_major,
        "school_list": [s.name for s in user.schools.all()] if hasattr(user, 'schools') else [],
    }

def format_user_context(context):
    parts = []
    if context.get("name"):
        parts.append(f"Name: {context['name']}")
    if context.get("grade_level"):
        parts.append(f"Grade Level: {context['grade_level']}")
    if context.get("gpa"):
        parts.append(f"GPA: {context['gpa']}")
    if context.get("intended_major"):
        parts.append(f"Intended Major: {context['intended_major']}")
    if context.get("school_list"):
        parts.append(f"School List: {', '.join(context['school_list'])}")
    
    return "\n".join(parts)

