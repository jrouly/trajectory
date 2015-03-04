"""
trajectory/engines/gmu_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to GMU's CS department.
"""


from trajectory.models import University, Department, Course
from trajectory.core import clean
from bs4 import BeautifulSoup
import requests
import re
import os


def scrape(args):
    """
    Scrape the available syllabi from the GMU CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Scraping GMU CS data." )


    # Constant values.
    catalog_index_url = "http://catalog.gmu.edu/preview_course_incoming.php?cattype=combined&prefix=%s"
    course_url = "http://catalog.gmu.edu/preview_course.php?catoid=%s&coid=%s"

    # Regex to select only the catid and coid.
    catid_re = re.compile("(^[^']*)|(, this.*$)|(')")

    # List of prefixes from the META object.
    prefixes = [department.get("abbreviation").lower()
                    for department in META.get("departments")]

    # Fetch existing metadata objects from database.
    university = META.get("school").get("name")
    university = args.session.query(University)\
            .filter(University.name==university)\
            .first()
    departments = {department.abbreviation.lower() : department
                    for department in args.session.query(Department)\
                        .filter(Department.university==university)\
                        .all()}

    for prefix in prefixes:
        catalog_index = requests.get(catalog_index_url % prefix)
        soup = BeautifulSoup( catalog_index.text )

        # Identify the list of courses.
        course_list = soup.find_all(
                name="a",
                onclick=re.compile("showCourse.*"))

        # Identify relevant information for each course.
        prereqs = {}
        for course in course_list:

            # Generate metadata
            log.debug(course.text)
            full_title = re.compile("\s+").split(course.text)
            prefix = full_title[0]
            cnum = full_title[1]
            title = ' '.join(full_title[3:])

            # Identify coid to get description.
            onclick = course['onclick']
            (catid, coid) = re.sub(catid_re, "", onclick).split(", ")

            # Generate a BeautifulSoup object of the course description.
            course_page = requests.get(course_url % (catid, coid))
            course_soup = BeautifulSoup(course_page.text)
            content = course_soup.find(class_="block_content_popup").hr.text

            # Clean up the description.
            description = content
            try:
                description = description[:description.index("Hours of Lecture")]
            except:
                pass

            # Identify prerequisites
            # TODO: Match these up with their database entries.
            prereq_index = description.find("Prerequisite(s)")
            if prereq_index > -1:
                prereq_string = description[prereq_index:]
                description = description[:prereq_index]

                prereq_re = re.compile("\w{2,4}\s\d{3}")
                matches = re.findall(prereq_re, prereq_string)
                if len(matches) > 0:
                    prereqs["%s %s" % (prefix, cnum)] = matches

            # Clean the description string
            description_raw = description
            description = clean(args, description)
            if description is None:
                continue

            # Generate the appropriate course object.
            departments[prefix.lower()].courses.append(Course(
                number=cnum,
                title=title,
                description=description,
                description_raw=description_raw))

    log.info( "Completed scraping." )


# Constant values.
META = {
    'school': {
        'name': "George Mason University",
        'abbreviation': "GMU",
        'url': "gmu.edu",
        },
    'departments': [
        {
            "name": "Accounting",
            "abbreviation": "ACCT",
        },
        {
          "name": "African and African American Studies",
          "abbreviation": "AFAM",
        },
        {
          "name": "Applied Information Technology",
          "abbreviation": "AIT",
        },
        {
          "name": "Arts Management",
          "abbreviation": "AMGT",
        },
        {
          "name": "Anthropology",
          "abbreviation": "ANTH",
        },
        {
          "name": "Arabic",
          "abbreviation": "ARAB",
        },
        {
          "name": "History and Art History",
          "abbreviation": "ARTH",
        },
        {
          "name": "Astronomy",
          "abbreviation": "ASTR",
        },
        {
          "name": "Athletic Training Education Program",
          "abbreviation": "ATEP",
        },
        {
          "name": "Art and Visual Technology",
          "abbreviation": "AVT",
        },
        {
          "name": "Bachelors of Applied Science",
          "abbreviation": "BAS",
        },
        {
          "name": "Bioengineering",
          "abbreviation": "BENG",
        },
        {
          "name": "Bioinformatics",
          "abbreviation": "BINF",
        },
        {
          "name": "Biodefense",
          "abbreviation": "BIOD",
        },
        {
          "name": "Biology",
          "abbreviation": "BIOL",
        },
        {
          "name": "Biosciences",
          "abbreviation": "BIOS",
        },
        {
          "name": "Bachelor of Individualized Study",
          "abbreviation": "BIS",
        },
        {
          "name": "Biomedical Science",
          "abbreviation": "BMED",
        },
        {
          "name": "Business Management",
          "abbreviation": "BMGT",
        },
        {
          "name": "Business and Legal Studies",
          "abbreviation": "BULE",
        },
        {
          "name": "Computational and Data Sciences",
          "abbreviation": "CDS",
        },
        {
          "name": "Civil, Environmental, and Infrastructure Engineering",
          "abbreviation": "CEIE",
        },
        {
          "name": "Computer Forensices",
          "abbreviation": "CFRS",
        },
        {
          "name": "Chemistry",
          "abbreviation": "CHEM",
        },
        {
          "name": "Chinese",
          "abbreviation": "CHIN",
        },
        {
          "name": "College of Humanities and Social Sciences",
          "abbreviation": "CHSS",
        },
        {
          "name": "Comparative Literature",
          "abbreviation": "CL",
        },
        {
          "name": "Classical Studies",
          "abbreviation": "CLAS",
        },
        {
          "name": "Climate Sciences",
          "abbreviation": "CLIM",
        },
        {
          "name": "Communications",
          "abbreviation": "COMM",
        },
        {
          "name": "Conflict Analysis and Resolution",
          "abbreviation": "CONF",
        },
        {
          "name": "Conservation and Policy",
          "abbreviation": "CONS",
        },
        {
          "name": "Mathematics and Statistical Science Dual-Degree",
          "abbreviation": "CRIM",
        },
        {
          "name": "Computer Science",
          "abbreviation": "CS",
        },
        {
          "name": "Computational Science",
          "abbreviation": "CSI",
        },
        {
          "name": "Computational Social Science",
          "abbreviation": "CSS",
        },
        {
          "name": "College Teaching",
          "abbreviation": "CTCH",
        },
        {
          "name": "Cultural Studies",
          "abbreviation": "CULT",
        },
        {
          "name": "College of Visual and Performing Arts",
          "abbreviation": "CVPA",
        },
        {
          "name": "Cybersecurity",
          "abbreviation": "CYSE",
        },
        {
          "name": "Data Analysis and Engineering",
          "abbreviation": "DAEN",
        },
        {
          "name": "Dance",
          "abbreviation": "DANC",
        },
        {
          "name": "Early Action Program",
          "abbreviation": "EAP",
        },
        {
          "name": "Electrical and Computer Engineering",
          "abbreviation": "ECE",
        },
        {
          "name": "Early Childhood Education",
          "abbreviation": "ECED",
        },
        {
          "name": "Economics",
          "abbreviation": "ECON",
        },
        {
          "name": "Education Administration and Leadership",
          "abbreviation": "EDAL",
        },
        {
          "name": "Education Assistive Technologies",
          "abbreviation": "EDAT",
        },
        {
          "name": "Counseling and Development",
          "abbreviation": "EDCD",
        },
        {
          "name": "Character Education",
          "abbreviation": "EDCE",
        },
        {
          "name": "Curriculum and Instructon",
          "abbreviation": "EDCI",
        },
        {
          "name": "Educational Psychology",
          "abbreviation": "EDEP",
        },
        {
          "name": "Educational Instructional Technology",
          "abbreviation": "EDIT",
        },
        {
          "name": "Education Leadership",
          "abbreviation": "EDLE",
        },
        {
          "name": "Eduation Professional Development",
          "abbreviation": "EDPD",
        },
        {
          "name": "Eucation Reading",
          "abbreviation": "EDRD",
        },
        {
          "name": "Education Research",
          "abbreviation": "EDRS",
        },
        {
          "name": "Special Education",
          "abbreviation": "EDSE",
        },
        {
          "name": "Education",
          "abbreviation": "EDUC",
        },
        {
          "name": "Exercise Fitness Health Promotion",
          "abbreviation": "EFHP",
        },
        {
          "name": "Executive MBA",
          "abbreviation": "EMBA",
        },
        {
          "name": "English",
          "abbreviation": "ENGH",
        },
        {
          "name": "Engineering",
          "abbreviation": "ENGR",
        },
        {
          "name": "Environmental Science and Public Policy",
          "abbreviation": "EVPP",
        },
        {
          "name": "Film and Video Studies",
          "abbreviation": "FAVS",
        },
        {
          "name": "Finance",
          "abbreviation": "FNAN",
        },
        {
          "name": "French",
          "abbreviation": "FREN",
        },
        {
          "name": "Foreign Language",
          "abbreviation": "FRLN",
        },
        {
          "name": "Forensic Science",
          "abbreviation": "FRSC",
        },
        {
          "name": "Game Design",
          "abbreviation": "GAME",
        },
        {
          "name": "Global and Community Health",
          "abbreviation": "GCH",
        },
        {
          "name": "Geology",
          "abbreviation": "GEOL",
        },
        {
          "name": "German",
          "abbreviation": "GERM",
        },
        {
          "name": "Geography and GeoInformation Science",
          "abbreviation": "GGS",
        },
        {
          "name": "Global Affairs",
          "abbreviation": "GLOA",
        },
        {
          "name": "Government",
          "abbreviation": "GOVT",
        },
        {
          "name": "Greek",
          "abbreviation": "GREE",
        },
        {
          "name": "Graduate School of Management",
          "abbreviation": "GSOM",
        },
        {
          "name": "Health Administration and Policy",
          "abbreviation": "HAP",
        },
        {
          "name": "Human Development and Family Sciences",
          "abbreviation": "HDFS",
        },
        {
          "name": "Health",
          "abbreviation": "HEAL",
        },
        {
          "name": "Hebrew",
          "abbreviation": "HEBR",
        },
        {
          "name": "Health and Human Services",
          "abbreviation": "HHS",
        },
        {
          "name": "History",
          "abbreviation": "HIST",
        },
        {
          "name": "Honors",
          "abbreviation": "HNRS",
        },
        {
          "name": "Honors and Technology",
          "abbreviation": "HNRT",
        },
        {
          "name": "International Education",
          "abbreviation": "IETT",
        },
        {
          "name": "Infosystems",
          "abbreviation": "INFS",
        },
        {
          "name": "Information Security and Assurance",
          "abbreviation": "ISA",
        },
        {
          "name": "Information Technology",
          "abbreviation": "IT",
        },
        {
          "name": "Italian",
          "abbreviation": "ITAL",
        },
        {
          "name": "International Commerce and Policy",
          "abbreviation": "ITRN",
        },
        {
          "name": "Japanese",
          "abbreviation": "JAPA",
        },
        {
          "name": "Kinesiology",
          "abbreviation": "KINE",
        },
        {
          "name": "Korean",
          "abbreviation": "KORE",
        },
        {
          "name": "Latin American Studies",
          "abbreviation": "LAS",
        },
        {
          "name": "Latin",
          "abbreviation": "LATN",
        },
        {
          "name": "Linguistics",
          "abbreviation": "LING",
        },
        {
          "name": "Masters in Interdisciplinary Studies",
          "abbreviation": "MAIS",
        },
        {
          "name": "Mathematics",
          "abbreviation": "MATH",
        },
        {
          "name": "Masters in Business Administration",
          "abbreviation": "MBA",
        },
        {
          "name": "Mechanical Engineering",
          "abbreviation": "ME",
        },
        {
          "name": "Middle East and Islamic Studies",
          "abbreviation": "MEIS",
        },
        {
          "name": "Management",
          "abbreviation": "MGMT",
        },
        {
          "name": "Management Information Systems",
          "abbreviation": "MIS",
        },
        {
          "name": "Marketing",
          "abbreviation": "MKTG",
        },
        {
          "name": "Medical Laboratory Sciences",
          "abbreviation": "MLAB",
        },
        {
          "name": "Military Sciences",
          "abbreviation": "MLSC",
        },
        {
          "name": "Masters in New Professionalism and Education",
          "abbreviation": "MNPE",
        },
        {
          "name": "Masters of New Professional Studies",
          "abbreviation": "MNPS",
        },
        {
          "name": "Management of Secure Information Systems",
          "abbreviation": "MSEC",
        },
        {
          "name": "Minor in Business",
          "abbreviation": "MSOM",
        },
        {
          "name": "Music",
          "abbreviation": "MUSI",
        },
        {
          "name": "Native American and Indigenous Studies",
          "abbreviation": "NAIS",
        },
        {
          "name": "Nanotechnology and Nanoscience",
          "abbreviation": "NANO",
        },
        {
          "name": "New Century College",
          "abbreviation": "NCLC",
        },
        {
          "name": "Neuroscience",
          "abbreviation": "NEUR",
        },
        {
          "name": "Nursing",
          "abbreviation": "NURS",
        },
        {
          "name": "Nutrition",
          "abbreviation": "NUTR",
        },
        {
          "name": "Organization Development and Knowledge Management",
          "abbreviation": "ODKM",
        },
        {
          "name": "Operations Management",
          "abbreviation": "OM",
        },
        {
          "name": "Operations Research",
          "abbreviation": "OR",
        },
        {
          "name": "Persian",
          "abbreviation": "PERS",
        },
        {
          "name": "Physical Education",
          "abbreviation": "PHED",
        },
        {
          "name": "Philosophy",
          "abbreviation": "PHIL",
        },
        {
          "name": "Physics",
          "abbreviation": "PHYS",
        },
        {
          "name": "Portuguese",
          "abbreviation": "PORT",
        },
        {
          "name": "Parks and Recreation Leisure Studies",
          "abbreviation": "PRLS",
        },
        {
          "name": "Provost",
          "abbreviation": "PROV",
        },
        {
          "name": "Physical Sciences",
          "abbreviation": "PSCI",
        },
        {
          "name": "Psychology",
          "abbreviation": "PSYC",
        },
        {
          "name": "Public Administration",
          "abbreviation": "PUAD",
        },
        {
          "name": "Public Policy",
          "abbreviation": "PUBP",
        },
        {
          "name": "Real Estate",
          "abbreviation": "REAL",
        },
        {
          "name": "Religion",
          "abbreviation": "RELI",
        },
        {
          "name": "Rehabilitation Sciences",
          "abbreviation": "RHBS",
        },
        {
          "name": "Russian",
          "abbreviation": "RUSS",
        },
        {
          "name": "Sytems Engineering and Operations Research",
          "abbreviation": "SEOR",
        },
        {
          "name": "Sociology and Anthropology",
          "abbreviation": "SOAN",
        },
        {
          "name": "Sociology",
          "abbreviation": "SOCI",
        },
        {
          "name": "Social Work",
          "abbreviation": "SOCW",
        },
        {
          "name": "School of Management",
          "abbreviation": "SOM",
        },
        {
          "name": "Spanish",
          "abbreviation": "SPAN",
        },
        {
          "name": "Sports Management",
          "abbreviation": "SPMT",
        },
        {
          "name": "Sport and Recreation Studies",
          "abbreviation": "SRST",
        },
        {
          "name": "Statistics",
          "abbreviation": "STAT",
        },
        {
          "name": "Software Engineering",
          "abbreviation": "SWE",
        },
        {
          "name": "Systems Engineering and Operations Research",
          "abbreviation": "SYST",
        },
        {
          "name": "Tax",
          "abbreviation": "TAX",
        },
        {
          "name": "Telecommunications2",
          "abbreviation": "TCOM",
        },
        {
          "name": "Technology Management",
          "abbreviation": "TECM",
        },
        {
          "name": "Telecommunications",
          "abbreviation": "TELE",
        },
        {
          "name": "Theater",
          "abbreviation": "THR",
        },
        {
          "name": "Tourism",
          "abbreviation": "TOUR",
        },
        {
          "name": "Turkish",
          "abbreviation": "TURK",
        },
        {
          "name": "University",
          "abbreviation": "UNIV",
        },
        {
          "name": "Urban and Suburban Studies",
          "abbreviation": "USST",
        },
        {
          "name": "Women and Gender Studies",
          "abbreviation": "WMST",
        },
    ]
}


