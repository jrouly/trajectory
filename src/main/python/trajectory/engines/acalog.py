from trajectory.engines import common

class Scraper(common.Scraper):

    def __init__(self,
        metadata_file,  # JSON file storing university metadata.
        index_url,      # URL of the catalog index page.
        course_url,     # URL of per-course pages.

        # Regex to identify catoid's from links.
        catoid_re="(?<=catoid=)\d+",

        # Regex to identify coid's from links.
        coid_re="(?<=coid=)\d+",

        # Regex to identify prereq course titles.
        prereq_re="([A-Za-z,]{2,4})(\s|\\\\xa0)(\d{3})",

        # Course title index offset.
        title_parser=lambda split: split[3:],
    ):
        """
        Initialize this acalog scraper given its particular configuration
        values.
        """

        # Execute the parent class' constructor.
        super().__init__(metadata_file)

        # Store URL data.
        self.catalog_index_url = index_url
        self.course_url = course_url

        # Store scraping regular expressions.
        import re
        self.catoid_re = re.compile(catoid_re)
        self.coid_re = re.compile(coid_re)
        self.prereq_re = re.compile(prereq_re)

        # Store custom lambdas.
        self.title_parser = title_parser


    def scrape(self, args):
        """
        Scrape the available syllabi from the Acalog install's page into
        the database layer.
        """

        self.log.info("Beginning web scrape.")

        from trajectory.models import University, Department, Course
        from trajectory.core import clean
        from bs4 import BeautifulSoup
        import requests, re

        # List of prefixes from the META object.
        prefixes = self.departments.keys()

        prereq_dict = {} # Dictionary of Course : Prereq match list
        for prefix in prefixes:
            catalog_index = requests.get(self.catalog_index_url % prefix)
            soup = BeautifulSoup(catalog_index.text)

            # Identify the list of courses.
            course_list = soup.find_all(
                    name="a",
                    onclick=re.compile("showCourse.*"))

            # Identify relevant information for each course.
            for course in course_list:

                # Generate metadata
                self.log.debug(course.text)
                full_title = re.compile("\s+").split(course.text)
                prefix = full_title[0]
                cnum = full_title[1]
                title = ' '.join(self.title_parser(full_title))

                # Identify coid to get description.
                href = course['href']
                catoid = self.catoid_re.search(href).group(0)
                coid = self.coid_re.search(href).group(0)

                # Generate a BeautifulSoup object of the course description.
                course_page = requests.get(self.course_url % (catoid, coid))
                course_soup = BeautifulSoup(course_page.text)
                content = course_soup.find(class_="block_content").hr

                # Do some processing to remove extraneous text.
                # TODO
                content = content.text
                description = content

                # Clean the description string
                description_raw = description
                description = clean(content)
                if description is None:
                    continue

                # Generate the appropriate course object.
                new_course = Course(
                    number=cnum,
                    title=title,
                    description=description,
                    description_raw=description_raw)
                self.departments[prefix.lower()].courses.append(new_course)

        self.log.info("Completed scraping.")

