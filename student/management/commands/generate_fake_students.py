import random
from datetime import datetime
from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from app.models import UserPermission, DegreeSpecialization
from student.models import StudentDetails, JobInfo


class Command(BaseCommand):
    help = 'Generates fake student data for the past 6 years, 300 students per year with 30% job placements using JobInfo model.'

    def handle(self, *args, **options):
        fake = Faker()

        # Predefined job-related data
        job_titles = [
            "SOFTWARE ENGINEER", "DATA ANALYST", "FRONTEND DEVELOPER", "BACKEND DEVELOPER",
            "DEVOPS ENGINEER", "MACHINE LEARNING ENGINEER", "CLOUD SOLUTIONS ARCHITECT",
            "QA ENGINEER", "BUSINESS ANALYST", "CYBERSECURITY ANALYST"
        ]

        company_names = [
            "INFOSYS", "TCS", "WIPRO", "ACCENTURE", "CAPGEMINI",
            "COGNIZANT", "IBM", "DELOITTE", "AMAZON", "MICROSOFT"
        ]

        company_locations = [
            "BANGALORE", "HYDERABAD", "PUNE", "MUMBAI", "CHENNAI",
            "GURGAON", "NOIDA", "KOLKATA", "DELHI", "AHMEDABAD"
        ]

        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        genders = ['Male', 'Female', 'Other']

        # Build degree-specialization dictionary
        degree_programs = {}
        for item in DegreeSpecialization.objects.values("degree").distinct():
            specs = DegreeSpecialization.objects.filter(
                degree=item["degree"]
            ).values_list("specialization", flat=True)
            degree_programs[item["degree"]] = list(specs)

        current_year = datetime.now().year
        total_students = 0

        for year_offset in range(6):
            year = current_year - year_offset
            self.stdout.write(self.style.NOTICE(f'\n📅 Creating students for year: {year}'))

            for i in range(300):
                try:
                    # Fake join date for this year
                    start_date = datetime(year, 1, 1)
                    end_date = datetime(year, 12, 31)
                    join_date = fake.date_time_between(start_date=start_date, end_date=end_date)

                    username = f"student{fake.unique.user_name()}"
                    email = fake.unique.email()

                    # Create user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='1'
                    )
                    user.date_joined = join_date
                    user.save()

                    # Assign user permissions
                    UserPermission.objects.create(
                        user=user,
                        is_student=True,
                        is_approved=True,
                        is_teacher=False,
                        is_company=False,
                        is_principal=False
                    )

                    # Random degree/specialization
                    degree = random.choice(list(degree_programs.keys()))
                    specialization = random.choice(degree_programs[degree])

                    # 3-year course (6 semesters)
                    semester = random.randint(1, 6)
                    course_year = ((semester - 1) // 2) + 1

                    student = StudentDetails.objects.create(
                        user=user,
                        name=fake.name(),
                        email=email,
                        phone=fake.unique.msisdn()[:15],
                        address=fake.address(),
                        date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
                        gender=random.choice(genders),
                        blood_group=random.choice(blood_groups),
                        profile_picture=None,
                        course=degree,
                        branch=specialization,
                        year=str(course_year),
                        sem=str(semester),
                        roll_no=f"{degree[:2].upper()}{fake.unique.random_number(digits=4)}",
                        reg_no=f"REG{fake.unique.random_number(digits=8)}",
                        cgpa=round(random.uniform(5.0, 10.0), 2),
                        resume=None,
                        is_resume_approved=random.choice([True, False, None])
                    )

                    # 30% chance the student is placed
                    if random.random() < 0.4:
                        JobInfo.objects.create(
                            student=student,
                            job_title=random.choice(job_titles),
                            company_name=random.choice(company_names),
                            company_location=random.choice(company_locations),
                            salary=round(random.uniform(3.0, 20.0), 2) * 100000,
                            date=join_date.date()
                        )

                    total_students += 1

                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Year {year} - Created student {i + 1}/300 ({degree}, Sem {semester})'
                    ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'❌ Error creating student {i + 1} for year {year}: {e}'
                    ))
                    continue

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Successfully created {total_students} fake students over 6 years!'))
