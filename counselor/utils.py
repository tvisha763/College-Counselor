import json

from .models import Course, Extracurricular, TakenCourse, TakenEC, WonAward

GRADE_SCHEDULE_FIELDS = {
    "freshman": "freshman_schedule",
    "sophomore": "sophomore_schedule",
    "junior": "junior_schedule",
    "senior": "senior_schedule",
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
            "name": ec.name,
            "description": ec.description,
            "position": ec.position,
            "type": TYPE_LABELS.get(ec.type, "Unknown"),
            "start_date": ec.start_date,
            "end_date": ec.end_date,
        }
        for ec in queryset
    ]


def get_or_create_course(name, type, organization):
    course, _ = Course.objects.get_or_create(
        name=name, organization=organization, defaults={"type": type}
    )
    return course


def update_schedule_entry(schedule, course, sem1, sem2, ap, ib):
    grades = json.loads(schedule.grades)
    grades["sem1"][course.name] = sem1
    grades["sem2"][course.name] = sem2
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

    for tc in schedule.takencourse_set.select_related("course"):
        c = tc.course
        entries.append(
            {
                "name": c.name,
                "type": TYPE_DISPLAY.get(c.type, "Unknown"),
                "sem1_grade": grades["sem1"].get(c.name),
                "sem2_grade": grades["sem2"].get(c.name),
                "ap": ap_scores.get(c.name),
                "ib": ib_scores.get(c.name),
                "organization": c.organization,
            }
        )
    return entries

def get_sched_data(sched):
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

def get_context(user):
    user_data = {
        "school": user.school,
        "grade": user.GRADE[user.grade - 9][1],
        "location": user.location,
        "citizenship": user.CITIZENSHIP[user.citizenship_status - 1][1] if user.citizenship_status != None else None,
        "college goals": user.college_goals,
        "major goals": user.major_goals,
        "class rank": user.class_rank,
        "class size": user.class_size,
        "first gen status": user.FIRST_GEN[user.first_gen - 1][1] if user.first_gen != None else None,
        "ethnicity": user.ethnicity,
        "gender": user.gender,
        "psat": user.psat,
        "sat": user.sat,
        "act": user.act,
    }

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

    context = "user_profile: " + json.dumps(user_data) + "\n Freshman Schedule: " + json.dumps(get_sched_data(user.freshman_schedule)) + "\n Sophomore Schedule: " + json.dumps(get_sched_data(user.sophomore_schedule))+ "\n Junior Schedule: " + json.dumps(get_sched_data(user.junior_schedule)) + "\n Senior Schedule: " + json.dumps(get_sched_data(user.senior_schedule)) + "\n Extracurriculars: " + ec_str + "\n Awards" + award_str
    return context