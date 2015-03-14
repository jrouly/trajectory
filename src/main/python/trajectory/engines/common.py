class Scraper:

    def __init__(self, metadata_file):

        # Set up logging object.
        import logging
        self.log = logging.getLogger("root")

        # Generate metadata object from engine JSON file.
        from trajectory import config as TRJ
        import json, os
        _json = open(os.path.join(TRJ.ENGINE_METADATA, metadata_file))
        self.META = json.load(_json)
        _json.close()

        # Register the target with the database, if not already present.
        from trajectory.models import University, Department, Course
        from trajectory.models.meta import session
        try:
            university = self.META.get("school")
            university_query = session.query(University)\
                    .filter(University.name==university.get("name"))

            # If the university has already been registered, alert the user
            # but grab a reference to it for the Departments.
            if(university_query.count() > 0):
                university = university_query.first()
                self.log.warn("University '%s' already registered." % \
                        university.name)

            # If the university has not been registered, register a new
            # one.
            else:
                self.log.info("Registering university '%s' with database." % \
                        university.get("name"))
                university = University(
                        name=university.get("name"),
                        abbreviation=university.get("abbreviation"),
                        url=university.get("url"))

                # Add the university to the session.
                session.add(university)

            self.university = university

            # Loop over the departments defined in the metadata.
            departments = self.META.get("departments")
            for department in departments:
                department_query = session.query(Department)\
                        .join(University)\
                        .filter(Department.name==department.get("name"))\
                        .filter(Department.university_id==self.university.id)

                # If the department has been registered, alert the user.
                if department_query.count() > 0:
                    self.log.warn("Department '%s' already registered." % \
                            department.get("name"))
                    continue

                # Otherwise register a new one.
                else:
                    self.university.departments.append(Department(
                            name=department.get("name"),
                            abbreviation=department.get("abbreviation"),
                            url=department.get("url")))
                    self.log.info("Registering department '%s' with database." % \
                            department.get("name"))

        except AttributeError as e:
            self.log.warn("Metadata not correctly defined.")
            self.log.debug(e)
            return

        # Index departments by their prefix for easy reference.
        self.departments = {
                department.abbreviation.lower() : department
                for department in self.university.departments
        }


    def __repr__(self):
        return "%s" % self.META.get("school").get("abbreviation").lower()


    def scrape(self, args):
        raise NotImplementedError("Define a custom scrape() function.")
