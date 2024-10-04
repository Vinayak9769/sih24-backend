import re


def parse_criteria(response_text):
    criteria = {
        'experience': 0,
        'education': '',
        'expertise': '',
        'categories': []
    }

    exp_match = re.search(r'Experience Level:\s*(\d+)', response_text, re.IGNORECASE)
    if exp_match:
        criteria['experience'] = int(exp_match.group(1))

    # Extract education
    edu_match = re.search(r'Education Background:\s*([\w\s]+)', response_text, re.IGNORECASE)
    if edu_match:
        criteria['education'] = edu_match.group(1).strip()

    # Extract expertise
    exp_match = re.search(r'Area of Expertise:\s*([\w\s]+)', response_text, re.IGNORECASE)
    if exp_match:
        criteria['expertise'] = exp_match.group(1).strip()

    # Extract categories
    cat_match = re.search(r'Categories:\s*([\w\s,]+)', response_text, re.IGNORECASE)
    if cat_match:
        criteria['categories'] = [cat.strip() for cat in cat_match.group(1).split(',')]

    return criteria
