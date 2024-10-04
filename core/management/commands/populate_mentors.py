import random
from django.core.management.base import BaseCommand
from faker import Faker
from core.models import Mentor, Category  # Replace 'myapp' with the actual name of your app

class Command(BaseCommand):
    help = 'Populate database with Mentor records'

    def handle(self, *args, **kwargs):
        fake = Faker()
        specific_names = ["Vinayak Mohanty", "Devansh Nair", "Vaibhav Sharma", "Yanshuman Yadav", "Vedang Kulkarni"]
        genders = ['male', 'female', 'other']

        # Ensure categories exist
        categories = list(Category.objects.all())
        if len(categories) == 0:
            self.stdout.write(self.style.ERROR('No categories found. Please add some categories first.'))
            return

        for i in range(15):
            name = specific_names[i] if i < len(specific_names) else fake.name()
            email = fake.unique.email()

            # Generate a unique username by appending a random number to the name
            username = name.lower().replace(" ", "_") + str(random.randint(1, 10000))

            mentor = Mentor.objects.create(
                username=username,  # Assign the generated username
                name=name,
                bio=fake.text(),
                profile_picture=None,
                phone_number=fake.phone_number(),
                gender=random.choice(genders),
                email=email,
                expertise=fake.job(),
                linkedin_profile=fake.url(),
                description=fake.paragraph(),
                price=round(random.uniform(10.0, 100.0), 2),
                experience=random.randint(0, 30),
                company=fake.company(),
            )

            # Adjust sampling to avoid errors
            max_sample_size = min(len(categories), 3)
            if max_sample_size > 0:
                random_categories = random.sample(categories, random.randint(1, max_sample_size))
                mentor.categories.set(random_categories)

        self.stdout.write(self.style.SUCCESS('Successfully populated the Mentor model with 15 records.'))
