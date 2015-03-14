"""
trajectory/scrape/engines/__init__.py
Author: Jean Michel Rouly

Backends for the scraper engine.
"""


import trajectory.engines.acalog

# Kansas State University
ksu = lambda: acalog.Scraper(
    metadata_file="ksu.json",
    index_url="http://catalog.k-state.edu/content.php?filter[27]=%s&cur_cat_oid=13&navoid=1425",
    course_url="http://catalog.k-state.edu/preview_course_nopop.php?catoid=%s&coid=%s"
)

# Louisiana State University
lsu = lambda: acalog.Scraper(
    metadata_file="lsu.json",
    index_url="http://catalog.lsu.edu/content.php?filter[27]=%s&cur_cat_oid=6&navoid=538",
    course_url="http://catalog.lsu.edu/preview_course_nopop.php?catoid=%s&coid=%s",
    title_parser=lambda split: split[2:-1],
)

# George Mason University
gmu = lambda: acalog.Scraper(
    metadata_file="gmu.json",
    index_url="http://catalog.gmu.edu/preview_course_incoming.php?cattype=combined&prefix=%s",
    course_url="http://catalog.gmu.edu/preview_course.php?catoid=%s&coid=%s"
)

# List of known targets.
targets = {
        'gmu': gmu,
        'ksu': ksu,
        'lsu': lsu,
}

# Define the formal package list of known targets.
__all__ = [t for t in targets]
