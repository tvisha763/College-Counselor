import json

from django.conf import settings
from openai import OpenAI

from counselor.models import CollegeApplication, TakenEC, WonAward


def store_in_session(request, page_identifier, role, message):
    session_key = f"chat_{page_identifier}"
    history = request.session.get(session_key, [])
    history.append({"role": role, "message": message})
    request.session[session_key] = history


def get_session_history(request, page_identifier):
    session_key = f"chat_{page_identifier}"
    return request.session.get(session_key, [])


def get_user_context(user):
    if not user or not getattr(user, "is_authenticated", False):
        return {}

    context = {
        "name": getattr(user, "fname", None) + getattr(user, "lname", None),
        "email": getattr(user, "email", None),
        "location": getattr(user, "location", None),
        "ethnicity": getattr(user, "ethnicity", None),
        "gender": getattr(user, "gender", None),
        "school": getattr(user, "school", None),
        "grade": get_grade_display(user),
        "gpa": get_gpa_display(user),
        "psat": getattr(user, "psat", None),
        "sat": getattr(user, "sat", None),
        "act": getattr(user, "act", None),
        "fresh_sched": get_sched_display(user.freshman_schedule),
        "soph_sched": get_sched_display(user.sophomore_schedule),
        "jun_sched": get_sched_display(user.junior_schedule),
        "sen_sched": get_sched_display(user.senior_schedule),
        "class_rank": getattr(user, "class_rank", None),
        "class_size": getattr(user, "class_size", None),
        "college_goals": getattr(user, "college_goals", None),
        "intended_major": getattr(user, "intended_major", None),
        "major_goals": getattr(user, "major_goals", None),
        "school_list": get_school_list(user),
        "citizenship": get_citizenship_display(user),
        "first_gen_status": get_first_gen_display(user),
        "extracurriculars": get_ec_string(user),
        "awards": get_award_string(user),
    }

    return {k: v for k, v in context.items() if v is not None}


def get_grade_display(user):
    if hasattr(user, "GRADE") and hasattr(user, "grade"):
        try:
            return user.GRADE[user.grade - 9][1]
        except (IndexError, TypeError):
            pass
    return getattr(user, "grade_level", None)


def get_gpa_display(user):
    total = 0
    num = 0

    for schedule in [
        user.freshman_schedule,
        user.sophomore_schedule,
        user.junior_schedule,
        user.senior_schedule,
    ]:
        if schedule.sem1_gpa is not None:
            total += schedule.sem1_gpa
            num += 1
        if schedule.sem2_gpa is not None:
            total += schedule.sem2_gpa
            num += 1

    return round(total / num, 2) if num > 0 else 0


def get_citizenship_display(user):
    if hasattr(user, "CITIZENSHIP") and hasattr(user, "citizenship_status"):
        try:
            return user.CITIZENSHIP[user.citizenship_status - 1][1]
        except (IndexError, TypeError):
            pass
    return None


def get_first_gen_display(user):
    if hasattr(user, "FIRST_GEN") and hasattr(user, "first_gen"):
        try:
            return user.FIRST_GEN[user.first_gen - 1][1]
        except (IndexError, TypeError):
            pass
    return None


def get_school_list(user):
    school_str = ""
    for a in CollegeApplication.objects.filter(user=user):
        data = [
            {
                "college": a.college,
                "major": a.major,
                "alt_major": a.alt_major,
            }
        ]

        school_str += json.dumps(({"schools": data})) + " "
        return school_str


def get_ec_string(user):
    ec_str = ""
    for ec in TakenEC.objects.filter(user=user):
        data = [
            {
                "name": ec.extracurricular.name,
                "description": ec.extracurricular.description,
                "position": ec.extracurricular.position,
                "type": ec.extracurricular.get_type_display(),  # convert choice field to readable string
                "start_date": (
                    ec.extracurricular.start_date.isoformat()
                    if ec.extracurricular.start_date
                    else None
                ),
                "end_date": (
                    ec.extracurricular.end_date.isoformat()
                    if ec.extracurricular.end_date
                    else None
                ),
            }
        ]

        ec_str += json.dumps(({"extracurriculars": data})) + " "
        return ec_str


def get_award_string(user):
    award_str = ""
    for a in WonAward.objects.filter(user=user):
        data = [
            {
                "name": a.award.name,
                "description": a.award.description,
                "date_received": (
                    a.award.date_received.isoformat()
                    if a.award.date_received
                    else None
                ),
            }
        ]

        award_str += json.dumps(({"awards": data})) + " "
        return award_str


def get_sched_display(sched):
    if sched != None:
        sched_data = {
            "grades": sched.grades,
            "ap scores": sched.ap_scores,
            "ib scores": sched.ib_scores,
            "sem1 gpa": sched.sem1_gpa,
            "sem2 gpa": sched.sem2_gpa,
        }
        return sched_data
    else:
        return {"data": "No Data"}


def format_user_context(context):
    parts = []

    # Class rank and size
    if context.get("class_rank") and context.get("class_size"):
        parts.append(
            f"Class Rank: {context['class_rank']}/{context['class_size']}"
        )

    # Basic info
    field_map = {
        "name": "Name: {}",
        "email": "Email: {}",
        "grade": "Grade: {}",
        "gpa": "GPA: {}",
        "school": "Current School: {}",
        "location": "Location: {}",
        "citizenship": "Citizenship: {}",
        "first_gen_status": "First Generation Student: {}",
        "ethnicity": "Ethnicity: {}",
        "gender": "Gender: {}",
        "psat": "PSAT Score: {}",
        "sat": "SAT Score: {}",
        "act": "ACT Score: {}",
        "intended_major": "Intended Major: {}",
        "college_goals": "College Goals: {}",
        "major_goals": "Career Goals: {}",
        "school_list": "Target Schools: {}",
        "extracurriculars": "\nExtracurriculars:\n{}",
        "awards": "\nAwards:\n{}",
    }

    for key, template in field_map.items():
        if key in context and context[key]:
            if key == "school_list":
                try:
                    school_data = json.loads(context[key])
                    formatted = ", ".join(
                        school["college"] for school in school_data["schools"]
                    )
                    parts.append(template.format(formatted))
                except:
                    parts.append(template.format(context[key]))
            else:
                parts.append(template.format(context[key]))

    # Schedule details
    sched_map = {
        "fresh_sched": "\nFreshman Year:\n{}",
        "soph_sched": "\nSophomore Year:\n{}",
        "jun_sched": "\nJunior Year:\n{}",
        "sen_sched": "\nSenior Year:\n{}",
    }

    for key, label in sched_map.items():
        sched = context.get(key)
        if sched and isinstance(sched, dict):
            sched_parts = []
            for field, value in sched.items():
                sched_parts.append(f"{field.title()}: {value}")
            parts.append(label.format("\n".join(sched_parts)))

    return "\n".join(parts)


def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)
