import json
from .models import Course, TakenCourse, Extracurricular

GRADE_SCHEDULE_FIELDS = {
    'freshman':   'freshman_schedule',
    'sophomore':  'sophomore_schedule',
    'junior':     'junior_schedule',
    'senior':     'senior_schedule',
}

TYPE_DISPLAY = {
    1: "Regular",
    2: "Honors",
    3: "AP",
    4: "IB",
}

TYPE_LABELS = dict(Extracurricular.TYPE)

def serialize_extracurriculars(queryset):
    return [
        {
            'name': ec.name,
            'description': ec.description,
            'position': ec.position,
            'type': TYPE_LABELS.get(ec.type, "Unknown"),
            'start_date': ec.start_date,
            'end_date': ec.end_date,
        }
        for ec in queryset
    ]

def get_or_create_course(name, type, organization):
    course, _ = Course.objects.get_or_create(
        name=name,
        organization=organization,
        defaults={'type': type}
    )
    return course


def update_schedule_entry(schedule, course, sem1, sem2, ap, ib):
    grades = json.loads(schedule.grades)
    grades['sem1'][course.name] = sem1
    grades['sem2'][course.name] = sem2
    schedule.grades = json.dumps(grades)

    ap_scores = json.loads(schedule.ap_scores)
    ap_scores[course.name] = ap
    schedule.ap_scores = json.dumps(ap_scores)

    ib_scores = json.loads(schedule.ib_scores)
    ib_scores[course.name] = ib
    schedule.ib_scores = json.dumps(ib_scores)

    schedule.save()

    TakenCourse.objects.get_or_create(course=course, schedule=schedule)


def serialize_schedule(schedule):
    entries = []
    grades = json.loads(schedule.grades)
    ap_scores = json.loads(schedule.ap_scores)
    ib_scores = json.loads(schedule.ib_scores)

    for tc in schedule.takencourse_set.select_related('course'):
        c = tc.course
        entries.append({
            'name': c.name,
            'type': TYPE_DISPLAY.get(c.type, "Unknown"),
            'sem1_grade': grades['sem1'].get(c.name),
            'sem2_grade': grades['sem2'].get(c.name),
            'ap': ap_scores.get(c.name),
            'ib': ib_scores.get(c.name),
            'organization': c.organization,
        })
    return entries
