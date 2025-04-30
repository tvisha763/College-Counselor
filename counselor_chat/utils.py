from django.conf import settings
from openai import OpenAI
from counselor.models import TakenEC, WonAward 
import json

def store_in_session(request, page_identifier, role, message):
    session_key = f'chat_{page_identifier}'
    history = request.session.get(session_key, [])
    history.append({'role': role, 'message': message})
    request.session[session_key] = history

def get_session_history(request, page_identifier):
    session_key = f'chat_{page_identifier}'
    return request.session.get(session_key, [])

def get_user_context(user):
    if not user or not getattr(user, 'is_authenticated', False):
        return {}
    
    context = {
        "name": getattr(user, 'name', None),
        "email": getattr(user, 'email', None),
        "location": getattr(user, 'location', None),
        "ethnicity": getattr(user, 'ethnicity', None),
        "gender": getattr(user, 'gender', None),
        "school": getattr(user, 'school', None),
        "grade": get_grade_display(user),
        "gpa": getattr(user, 'gpa', None),
        "class_rank": getattr(user, 'class_rank', None),
        "college_goals": getattr(user, 'college_goals', None),
        "intended_major": getattr(user, 'intended_major', None),
        "major_goals": getattr(user, 'major_goals', None),
        "school_list": get_school_list(user),
        "citizenship": get_citizenship_display(user),
        "first_gen_status": get_first_gen_display(user),
        "extracurriculars": get_ec_string(user),
        "awards": get_award_string(user)
    }

    return {k: v for k, v in context.items() if v is not None}

def get_grade_display(user):
    if hasattr(user, 'GRADE') and hasattr(user, 'grade'):
        try:
            return user.GRADE[user.grade - 9][1]
        except (IndexError, TypeError):
            pass
    return getattr(user, 'grade_level', None)

def get_citizenship_display(user):
    if hasattr(user, 'CITIZENSHIP') and hasattr(user, 'citizenship_status'):
        try:
            return user.CITIZENSHIP[user.citizenship_status - 1][1]
        except (IndexError, TypeError):
            pass
    return None

def get_first_gen_display(user):
    if hasattr(user, 'FIRST_GEN') and hasattr(user, 'first_gen'):
        try:
            return user.FIRST_GEN[user.first_gen - 1][1]
        except (IndexError, TypeError):
            pass
    return None

def get_school_list(user):
    if hasattr(user, 'schools'):
        return [s.name for s in user.schools.all()]
    return []

def get_ec_string(user):
    return " ".join(json.dumps(ec.extracurricular) for ec in TakenEC.objects.filter(user=user))

def get_award_string(user):
    return " ".join(json.dumps(award.award) for award in WonAward.objects.filter(user=user))

def format_user_context(context):
    parts = []

    if context.get('class_rank') and context.get('class_size'):
        parts.append(f"Class Rank: {context['class_rank']}/{context['class_size']}")
    
    field_map = {
        'name': "Name: {}",
        'email': "Email: {}",
        'grade': "Grade: {}",
        'gpa': "GPA: {}",
        'school': "Current School: {}",
        'location': "Location: {}",
        'citizenship': "Citizenship: {}",
        'intended_major': "Intended Major: {}",
        'college_goals': "College Goals: {}",
        'major_goals': "Career Goals: {}",
        'first_gen_status': "First Generation Student: {}",
        'ethnicity': "Ethnicity: {}",
        'gender': "Gender: {}",
        'school_list': "Target Schools: {}",
        'extracurriculars': "\nExtracurriculars:\n{}",
        'awards': "\nAwards:\n{}",
    }

    for key, template in field_map.items():
        if key in context and context[key]:
            if key == 'school_list':
                parts.append(template.format(', '.join(context[key])))
            else:
                parts.append(template.format(context[key]))

    return '\n'.join(parts)

def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


